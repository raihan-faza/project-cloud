import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from auth.auth import app as auth_router
from payment.payment import app as payment_router
from dotenv import load_dotenv

load_dotenv()
origins = os.getenv("MY_IP")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])