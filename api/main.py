from fastapi import FastAPI
from auth.auth import app as auth_router
from payment.payment import app as payment_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])