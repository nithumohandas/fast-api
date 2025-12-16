import asyncio
import hashlib
import hmac
import json
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_URL = "sqlite:///./webhooks.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()


# Models
class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    events = Column(Text, nullable=False)  # JSON array as string
    secret = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, nullable=False)
    event = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=True)
    success = Column(Boolean, default=False)
    attempts = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Webhook delivery functions
def generate_signature(payload: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


async def deliver_webhook(
        subscription_id: int,
        url: str,
        event: str,
        payload: dict,
        secret: Optional[str] = None,
        db: Session = None
) -> bool:
    """Deliver webhook and log the result"""

    payload_str = json.dumps(payload)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MyApp-Webhook/1.0",
        "X-Event-Type": event
    }

    if secret:
        headers["X-Webhook-Signature"] = generate_signature(payload_str, secret)

    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, content=payload_str, headers=headers)

                # Log the delivery
                log = WebhookLog(
                    subscription_id=subscription_id,
                    event=event,
                    payload=payload_str,
                    status_code=response.status_code,
                    success=response.status_code in [200, 201, 202, 204],
                    attempts=attempt
                )
                db.add(log)
                db.commit()

                if response.status_code in [200, 201, 202, 204]:
                    return True

        except Exception as e:
            last_error = str(e)

        if attempt < max_retries:
            await asyncio.sleep(2 ** (attempt - 1))

    # Log final failure
    log = WebhookLog(
        subscription_id=subscription_id,
        event=event,
        payload=payload_str,
        success=False,
        attempts=max_retries,
        error_message=last_error
    )
    db.add(log)
    db.commit()

    return False


async def broadcast_event(event: str, data: dict, db: Session):
    """Broadcast event to all subscribers"""

    payload = {
        "event": event,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

    subscriptions = db.query(WebhookSubscription).filter(
        WebhookSubscription.active == True
    ).all()

    tasks = []
    for sub in subscriptions:
        events = json.loads(sub.events)
        if event in events or "*" in events:
            task = deliver_webhook(
                subscription_id=sub.id,
                url=sub.url,
                event=event,
                payload=payload,
                secret=sub.secret,
                db=db
            )
            tasks.append(task)

    if tasks:
        import asyncio
        await asyncio.gather(*tasks, return_exceptions=True)


# API Endpoints
@app.post("/webhooks/subscriptions")
def create_subscription(
        url: str,
        events: list[str],
        secret: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Create a new webhook subscription"""

    subscription = WebhookSubscription(
        url=url,
        events=json.dumps(events),
        secret=secret
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return {
        "id": subscription.id,
        "url": subscription.url,
        "events": events,
        "active": subscription.active
    }


@app.get("/webhooks/subscriptions")
def list_subscriptions(db: Session = Depends(get_db)):
    """List all webhook subscriptions"""

    subscriptions = db.query(WebhookSubscription).all()
    return {
        "subscriptions": [
            {
                "id": sub.id,
                "url": sub.url,
                "events": json.loads(sub.events),
                "active": sub.active,
                "created_at": sub.created_at.isoformat()
            }
            for sub in subscriptions
        ]
    }


@app.delete("/webhooks/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Delete a webhook subscription"""

    subscription = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()

    return {"status": "deleted"}


@app.get("/webhooks/logs")
def get_webhook_logs(
        limit: int = 50,
        subscription_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Get webhook delivery logs"""

    query = db.query(WebhookLog)

    if subscription_id:
        query = query.filter(WebhookLog.subscription_id == subscription_id)

    logs = query.order_by(WebhookLog.created_at.desc()).limit(limit).all()

    return {
        "logs": [
            {
                "id": log.id,
                "subscription_id": log.subscription_id,
                "event": log.event,
                "status_code": log.status_code,
                "success": log.success,
                "attempts": log.attempts,
                "error": log.error_message,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }


# Example: Trigger webhooks from business events
@app.post("/users")
async def create_user(
        name: str,
        email: str,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Create user and send webhook"""

    user_data = {
        "id": 123,
        "name": name,
        "email": email,
        "created_at": datetime.utcnow().isoformat()
    }

    background_tasks.add_task(broadcast_event, "user.created", user_data, db)

    return {"status": "success", "user": user_data}


# Testing endpoint
@app.post("/webhooks/test")
async def test_webhook(
        event: str,
        data: dict,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Test webhook delivery"""

    background_tasks.add_task(broadcast_event, event, data, db)
    return {"status": "triggered", "event": event}