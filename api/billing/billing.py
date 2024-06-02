import docker
from dotenv import load_dotenv
from fastapi import Depends, Request, HTTPException
from requests import Session
from sqlmodel import select
from schema import Container, Billing, Action, get_db
from fastapi.routing import APIRouter
from datetime import datetime, timedelta

load_dotenv()

app = APIRouter()
client = docker.from_env()


@app.post("/container/action/")
async def handle_action(action: Request, db: Session = Depends(get_db)):
    timestamp = datetime.strptime(f"{action.date} {action.time}", "%Y-%m-%d %H:%M:%S")
    action_log = Action(container_id=action.container_id, action=action.action, timestamp=timestamp)
    db.add(action_log)
    db.commit()
    return {"message": "Action logged successfully"}


@app.get("/container/billing/{container_id}")
async def get_billing(container_id: str, db: Session = Depends(get_db)):
    actions = db.exec(select(Action).where(Action.container_id == container_id).order_by(Action.timestamp)).all()
    if not actions:
        raise HTTPException(status_code=404, detail="No actions found for this container")

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

    total_minutes = int(total_uptime.total_seconds() // 60 + 1)
    total_cost = total_minutes * container.price

    billing = Billing(user_id=container.user_id, total=total_cost)
    db.add(billing)
    db.commit()

    return {"total_uptime_minutes": total_minutes, "total_cost": total_cost}
