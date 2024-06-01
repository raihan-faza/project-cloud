import docker
from dotenv import load_dotenv
from fastapi import Depends, Request, HTTPException
from requests import Session
from sqlmodel import select
from schema import Container, Billing, get_db
from fastapi.routing import APIRouter
from datetime import datetime, timedelta

load_dotenv()

app = APIRouter()
client = docker.from_env()


@app.get("/billing")
async def get_billing(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    if not data:
        raise HTTPException(status_code=404, detail="No actions found for this container")
    
    container_id = data.get("container_id")
    actions = data.get("actions")

    container = db.exec(select(Container).where(Container.id == container_id)).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    total_uptime = timedelta()
    last_unpause_time = None

    for action in actions:
        if action.action == "unpause":
            last_unpause_time = action.timestamp
        elif action.action == "pause" and last_unpause_time:
            total_uptime += action.timestamp - last_unpause_time
            last_unpause_time = None

    if last_unpause_time:
        total_uptime += datetime.now() - last_unpause_time

    total_minutes = total_uptime.total_seconds() // 60 + 1
    total_cost = int(total_minutes * container.price)

    billing = Billing(user_id=container.user_id, total=total_cost)
    db.add(billing)
    db.commit()

    return {"total_uptime_minutes": total_minutes, "total_cost": total_cost}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)