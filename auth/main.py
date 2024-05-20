from fastapi import (
    FastAPI,
    Request
)
from authlib.integrations.starlette_client import (
    OAuth,
    OAuthError
)
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import (
    RedirectResponse,
    JSONResponse
)
from hypercorn.asyncio import serve
from hypercorn.config import Config

app = FastAPI()

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
oauth.register(**OAUTH_PROVIDERS["google"])

app.add_middleware(SessionMiddleware, secret_key="secret")


@app.get("/")
async def read_root(request: Request):
    user = request.session.get('user')
    if not user:
        return {"message": "try login"}
    return {"message": "sup bro"}


@app.get("/dashboard")
async def dashboard(request: Request):
    user = request.session.get('user')
    if not user:
        return {"message": "you have to login first"}
    return {"message": "this is dashboard"}


@app.get("/hello")
async def read_hello():
    return {"message": "hahaha"}


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
        request.session['user'] = dict(user_info)
    return RedirectResponse(url='/')


if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    config.use_reloader = True
    config.use_debugger = True
    serve(app, config)
