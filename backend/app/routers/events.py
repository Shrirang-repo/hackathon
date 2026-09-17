from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import LandslideEvent, Location
from ..schemas import LandslideEventResponse, LandslideEventCreate

router = APIRouter(
    prefix="/api/v1/landslide-events",
    tags=["Historical Landslide Events"]
)


def _enrich_event_response(event: LandslideEvent) -> LandslideEventResponse:
    return LandslideEventResponse(
        id=event.id,
        location_id=event.location_id,
        event_date=event.event_date,
        latitude=event.latitude,
        longitude=event.longitude,
        severity=event.severity,
        cause=event.cause,
        rainfall_before_event=event.rainfall_before_event,
        description=event.description,
        source=event.source,
        created_at=event.created_at,
        location_name=event.location.name if event.location else None,
        state=event.location.state if event.location else None
    )


@router.get(
    "",
    response_model=List[LandslideEventResponse],
    summary="Get Historical Landslide Events",
    description="Retrieve historical landslide disaster occurrences with filters for state, location, severity, and dates."
)
def get_landslide_events(
    state: Optional[str] = Query(None, description="Filter by state"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MODERATE, HIGH, CRITICAL"),
    start_date: Optional[datetime] = Query(None, description="Events on or after this ISO date"),
    end_date: Optional[datetime] = Query(None, description="Events on or before this ISO date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(LandslideEvent).outerjoin(Location, LandslideEvent.location_id == Location.id)

    if location_id:
        query = query.filter(LandslideEvent.location_id == location_id)
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    if severity:
        query = query.filter(LandslideEvent.severity == severity.upper())
    if start_date:
        query = query.filter(LandslideEvent.event_date >= start_date)
    if end_date:
        query = query.filter(LandslideEvent.event_date <= end_date)

    events = query.order_by(desc(LandslideEvent.event_date)).offset(skip).limit(limit).all()
    return [_enrich_event_response(e) for e in events]


@router.post(
    "",
    response_model=LandslideEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Historical Landslide Event",
    description="Add a historical or newly occurred landslide event record to the database."
)
def create_landslide_event(event_in: LandslideEventCreate, db: Session = Depends(get_db)):
    if event_in.location_id:
        location = db.query(Location).filter(Location.id == event_in.location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {event_in.location_id} not found."
            )

    db_event = LandslideEvent(
        location_id=event_in.location_id,
        event_date=event_in.event_date,
        latitude=event_in.latitude,
        longitude=event_in.longitude,
        severity=event_in.severity.upper(),
        cause=event_in.cause,
        rainfall_before_event=event_in.rainfall_before_event or 0.0,
        description=event_in.description,
        source=event_in.source,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return _enrich_event_response(db_event)
