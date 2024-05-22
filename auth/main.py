import datetime
from fastapi import (
    Depends,
    FastAPI,
    Request,
    HTTPException
)
from authlib.integrations.starlette_client import (
    OAuth,
    OAuthError
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import bcrypt
import jwt

from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import (
    RedirectResponse,
    JSONResponse
)
from hypercorn.asyncio import serve
from hypercorn.config import Config
from dotenv import load_dotenv
import os

from schema import get_db
from schema import User
from starlette import status

load_dotenv()
app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

OAUTH_PROVIDERS = {
    "google": {
        "name": "google",
        "client_id": "1031929485356-0f2a323c0qj7s9c3hqg3dd8e5pgdku9l.apps.googleusercontent.com",
        "client_secret": "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",
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://accounts.google.com/o/oauth2/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v1/userinfo",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "scope": "openid email profile",
    }
}

oauth = OAuth()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="google/login")
oauth.register(**OAUTH_PROVIDERS["google"])

app.add_middleware(SessionMiddleware, secret_key="secret")


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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload

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
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return {"messages": f"{error.error}"}
    user_info = token['userinfo']
    if user_info:
        print(user_info)
        access_token = create_access_token({"email": user_info['email'], "username": user_info['name']})
        refresh_token = create_refresh_token({"email": user_info['email'], "username": user_info['name']})
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "user":{"name": user_info['name'], "email":user_info['email']}})
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
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"email": db_user.email, "username": db_user.username})
    refresh_token = create_refresh_token({"email": db_user.email, "username": db_user.username})

    return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "user":{"name": db_user.username, "email":db_user.email}})

@app.post("/refresh-token")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    email = payload.get("email")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect payload"
        )
    new_access_token = create_access_token({"email": user.email, "username": user.username})
    new_refresh_token = create_refresh_token({"email": user.email, "username": user.username})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    config.use_reloader = True
    config.use_debugger = True
    serve(app, config)
