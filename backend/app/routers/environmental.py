from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import Location, EnvironmentalData
from ..schemas import EnvironmentalDataResponse, EnvironmentalDataCreate

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Environmental Data"]
)


@router.get(
    "/{location_id}/environment",
    response_model=EnvironmentalDataResponse,
    summary="Get Latest Environmental Data",
    description="Fetch the most recent telemetry readings (rainfall, soil moisture, humidity, temperature, slope, elevation) for a location."
)
def get_latest_environment(location_id: int, db: Session = Depends(get_db)):
    # Verify location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    latest_env = (
        db.query(EnvironmentalData)
        .filter(EnvironmentalData.location_id == location_id)
        .order_by(desc(EnvironmentalData.recorded_at))
        .first()
    )
    if not latest_env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No environmental data recorded for location ID {location_id}."
        )

    return latest_env


@router.get(
    "/{location_id}/environment/history",
    response_model=List[EnvironmentalDataResponse],
    summary="Get Historical Environmental Measurements",
    description="Retrieve historical time-series environmental measurements for a location, formatted for frontend charts."
)
def get_environment_history(
    location_id: int,
    hours: Optional[int] = Query(None, ge=1, le=720, description="Filter measurements within the last N hours"),
    limit: int = Query(50, ge=1, le=500, description="Max number of historical records to return"),
    db: Session = Depends(get_db)
):
    # Verify location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    query = db.query(EnvironmentalData).filter(EnvironmentalData.location_id == location_id)

    if hours is not None:
        since_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = query.filter(EnvironmentalData.recorded_at >= since_time)

    records = query.order_by(desc(EnvironmentalData.recorded_at)).limit(limit).all()
    return records


@router.post(
    "/{location_id}/environment",
    response_model=EnvironmentalDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Environmental Sensor Reading",
    description="Record new environmental telemetry for a location."
)
def create_environment_record(
    location_id: int,
    env_in: EnvironmentalDataCreate,
    db: Session = Depends(get_db)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    data_dict = env_in.model_dump()
    if not data_dict.get("recorded_at"):
        data_dict["recorded_at"] = datetime.now(timezone.utc)

    db_env = EnvironmentalData(location_id=location_id, **data_dict)
    db.add(db_env)
    db.commit()
    db.refresh(db_env)
    return db_env
