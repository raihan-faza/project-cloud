import datetime
import uuid
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Request,
    HTTPException,
    requests
)
from authlib.integrations.starlette_client import (
    OAuth,
    OAuthError
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import bcrypt
import jwt
from starlette.responses import (
    RedirectResponse,
    JSONResponse
)
from dotenv import load_dotenv
import os

from schema import get_db
from schema import User
from starlette import status

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer


load_dotenv()
app = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

OAUTH_PROVIDERS = {
    "google": {
        "name": "google",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://accounts.google.com/o/oauth2/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v1/userinfo",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "scope": "openid email profile",
    }
}

oauth = OAuth()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth.register(**OAUTH_PROVIDERS["google"])

# app.add_middleware(SessionMiddleware, secret_key="secret")


def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_access_token(data: dict):
    copy_data = data.copy()
    exp  = datetime.datetime.now() + datetime.timedelta(minutes=15)
    copy_data.update({"exp": exp})
    return jwt.encode(copy_data, SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict):
    copy_data = data.copy()
    exp  = datetime.datetime.now() + datetime.timedelta(days=30)
    copy_data.update({"exp": exp})
    return jwt.encode(copy_data, REFRESH_SECRET_KEY)

def send_verification_email(email: str, token: str):
    mail_content = f'''
    Please click on the link to verify your account:
    http://localhost:8000/verify?token={token}
    '''
    

    message = MIMEMultipart()
    message['From'] = os.getenv("EMAIL")
    message['To'] = email
    message['Subject'] = 'Account Verification'   
    message.attach(MIMEText(mail_content, 'plain'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(os.getenv("EMAIL"), os.getenv("EMAIL_PASS")) 
    text = message.as_string()
    session.sendmail(os.getenv("EMAIL"), email, text)
    session.quit()



async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    uuid = payload.get("uuid")
    user = db.query(User).filter(User.uuid == uuid).first().to_safe_dict()
    if user is None:
        raise credentials_exception
    return user


@app.get("/")
async def read_root(request: Request):
    return {"message": "sup bro"}


# @app.get("/dashboard")
# async def dashboard(request: Request):
#     user = request.session.get('user')
#     if not user:
#         return {"message": "you have to login first"}
#     return {"message": "this is dashboard"}

@app.get("/dashboard")
async def read_dashboard(current_user: dict = Depends(get_current_user)):
    return {"message": "Welcome to the dashboard!", 'user':current_user}

@app.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return {"messages": f"{error.error}"}
    user_info = token['userinfo']
    if user_info:
        uuid = str(uuid.uuid4())
        access_token = create_access_token({"email": user_info['email'], "username": user_info['name'], "uuid": uuid})
        refresh_token = create_refresh_token({"email": user_info['email'], "username": user_info['name'], "uuid": uuid})
        user = User(email=user_info['email'], username=user_info['name'], uuid=uuid)
        db.add(user)
        
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "user":{"name": user_info['name'], "email":user_info['email'], "uuid": uuid}})
    return RedirectResponse(url='/')

@app.post("/register")
async def register(user: User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user.password = get_password_hash(user.password)
    user.uuid = str(uuid.uuid4())
    
    access_token = create_access_token({"email": user.email, "username": user.username, "password": user.password, "uuid": user.uuid})
    send_verification_email(user.email, access_token)
    return {"message": "Check your email for verification!"}

@app.post("/login")
async def login(user: User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"email": db_user.email, "username": db_user.username, "uuid": db_user.uuid})
    refresh_token = create_refresh_token({"email": db_user.email, "username": db_user.username, "uuid": db_user.uuid})

    return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "user":{"name": db_user.username, "email":db_user.email, "balance": db_user.balance}})

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@app.get("/verify")
async def verify(token: str, db: Session = Depends(get_db)):
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(payload)
        if payload:
            email = payload.get("email")
            username = payload.get("username")
            password = payload.get("password")
            uuid = payload.get("uuid")
            if email is None or username is None or password is None:
                raise credentials_exception
            user = User(email=email, username=username, password=password, uuid=uuid)
            
            access_token = create_access_token({"email": email, "username": username, "uuid": uuid})
            refresh_token = create_refresh_token({"email": email, "username": username, "uuid": uuid})
            db.add(user)
            db.commit()
            return {"message": "User verified successfully", "access_token": access_token, "refresh_token": refresh_token}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid payload"
            )

@app.post("/refresh-token")
async def refresh_token(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    email = payload.get("email")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect payload"
        )
    new_access_token = create_access_token({"email": user.email, "username": user.username, "uuid": user.uuid})
    new_refresh_token = create_refresh_token({"email": user.email, "username": user.username, "uuid": user.uuid})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    if current_user:
        return {"message": "User found", "user": current_user}
    else :
        return {"message": "User not found"}

@app.put("/balance")
async def update_balance(amount: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user:
        user = db.query(User).filter(User.uuid == current_user.get("uuid")).first()
        user.balance -= amount
        db.commit()
        if user.balance < 0:
            requests.post("http://localhost:8000/payment/charge", json={"message":"Your balance is empty","balance": 0})
            return {"message": "balance updated" }
        requests.post("http://localhost:8000/payment/charge", json={"message":"Balance updated","balance": abs(user.balance)})
        return {"message": "balance updated" }