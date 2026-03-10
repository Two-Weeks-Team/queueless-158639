from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from models import SessionLocal, QueueEntry, Customer, Location
from ai_service import predict_wait_time, get_recommendations

router = APIRouter()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Helper to serialize QueueEntry objects
# ---------------------------------------------------------------------------
def _queue_entry_to_dict(entry: QueueEntry) -> dict:
    return {
        "id": str(entry.id),
        "customer_name": entry.customer.name if entry.customer else None,
        "party_size": entry.party_size,
        "status": entry.status,
        "joined_at": entry.joined_at.isoformat() if entry.joined_at else None,
        "queue_code": entry.queue_code,
    }

@router.get("/queue", response_model=dict)
async def get_queue(db: Session = Depends(get_db)):
    entries = db.query(QueueEntry).filter(QueueEntry.status == "pending").order_by(QueueEntry.joined_at).all()
    return {"queue_entries": [_queue_entry_to_dict(e) for e in entries]}

@router.get("/wait-time", response_model=dict)
async def get_wait_time(location_id: str = Query(..., description="UUID of the location")):
    # Simple validation
    try:
        uuid.UUID(location_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid location_id")
    result = await predict_wait_time(location_id)
    # Expected to return a dict like {"wait_time": 12}
    return result

@router.get("/recommendations", response_model=dict)
async def get_recommendations_endpoint(customer_id: str = Query(..., description="UUID of the customer")):
    try:
        uuid.UUID(customer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer_id")
    result = await get_recommendations(customer_id)
    return result
