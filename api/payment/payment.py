import os
import uuid
from dotenv import load_dotenv
from fastapi.routing import APIRouter
import midtransclient

load_dotenv()


app = APIRouter()
core = midtransclient.CoreApi(
    is_production=False,
    server_key=os.getenv("MIDTRANS_SERVER_KEY"),
    client_key=os.getenv("MIDTRANS_CLIENT_KEY")
)

@app.post("/charge")
async def create_charge():
    charge_request = {
        "payment_type": "gopay",
        "transaction_details": {
            "order_id": str(uuid.uuid4()),
            "gross_amount": 10000
        }
    }
    charge_response = core.charge(charge_request)
    return {"message":"success", "data":charge_response}
