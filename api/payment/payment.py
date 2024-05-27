import os
import uuid
from dotenv import load_dotenv
from fastapi import Depends, Request
from fastapi.routing import APIRouter
import midtransclient
from requests import Session
from schema import Payment, User, get_db
from auth.auth import get_current_user
load_dotenv()


app = APIRouter()
core = midtransclient.CoreApi(
    is_production=False,
    server_key=os.getenv("MIDTRANS_SERVER_KEY"),
    client_key=os.getenv("MIDTRANS_CLIENT_KEY")
)

@app.post("/charge")
async def create_charge(req: Request, token:str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        data = await req.json()
        charge_request = {
            "payment_type": "gopay",
            "transaction_details": {
                "order_id": str(uuid.uuid4()),
                "gross_amount": data.get("gross_amount")
            }
        }
        print(token)
        charge_response = core.charge(charge_request)
        new_payment = Payment(user_id=token.get("id"), order_id=charge_response.get("order_id"))
        db.add(new_payment)
        db.commit()
    except Exception as e:
        print(e)
        raise e
    # return {"message":"success"}
    return {"message":"success", "data":charge_response, "user": token.get("username")}

# @app.post("/charge")
# async def create_charge():
   
#     charge_request = {
#         "payment_type": "qris",
#         "transaction_details": {
#             "gross_amount": 24145,
#             "order_id": str(uuid.uuid4()),
#         },
#     }
#     charge_response = core.charge(charge_request)
    
    # return {"message":"success", "data":charge_response}
@app.post("/notification")
async def notification(req: Request, db: Session = Depends(get_db)):
    notification = await req.json()
    payment = db.query(Payment).filter(Payment.order_id == notification.get("order_id")).first()
    
    if payment:
        if notification.get('transaction_status') == 'settlement' or notification.get('transaction_status') == 'capture':
            user = db.query(User).filter(User.id == payment.user_id).first()
            gross_amount = notification.get("gross_amount")
            if gross_amount is not None:
                user.balance += int(round(float(gross_amount)))
                db.commit()
    
    # notification = {
    #     "transaction_time": "2021-06-15 18:45:13",
    #     "transaction_status": "settlement",
    #     "transaction_id": "513f1f01-c9da-474c-9fc9-d5c64364b709",
    #     "status_message": "midtrans payment notification",
    #     "status_code": "200",
    #     "signature_key": "2496c78cac93a70ca08014bdaaff08eb7119ef79ef69c4833d4399cada077147febc1a231992eb8665a7e26d89b1dc323c13f721d21c7485f70bff06cca6eed3",
    #     "settlement_time": "2021-06-15 18:45:28",
    #     "payment_type": "gopay",
    #     "order_id": "Order-5100",
    #     "merchant_id": "G141532850",
    #     "gross_amount": "154600.00",
    #     "fraud_status": "accept",
    #     "currency": "IDR"
    # }
    
    return {"message":"success"}

