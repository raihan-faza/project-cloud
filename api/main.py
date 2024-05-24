from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from auth.auth import app as auth_router
from payment.payment import app as payment_router


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret")
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])