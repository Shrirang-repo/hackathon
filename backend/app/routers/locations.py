from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import Location, EnvironmentalData, RiskPrediction, Alert, LandslideEvent
from ..schemas import (
    LocationResponse,
    LocationDetailResponse,
    LocationCreate,
    EnvironmentalDataResponse,
    PredictionResponse,
    AlertResponse,
    LandslideEventResponse
)

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Locations"]
)


@router.get(
    "",
    response_model=List[LocationResponse],
    summary="Get All Monitored Locations",
    description="Retrieve all monitored landslide risk locations with coordinates, topographic factors, and current risk metrics."
)
def get_locations(
    state: Optional[str] = Query(None, description="Filter by state name (e.g. Assam, Meghalaya)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MODERATE, HIGH, CRITICAL)"),
    district: Optional[str] = Query(None, description="Filter by district"),
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: Session = Depends(get_db)
):
    query = db.query(Location)
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    if risk_level:
        query = query.filter(Location.risk_level == risk_level.upper())
    if district:
        query = query.filter(Location.district.ilike(f"%{district}%"))
    
    locations = query.order_by(desc(Location.risk_score)).offset(skip).limit(limit).all()
    return locations


@router.post(
    "",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Monitored Location",
    description="Register a new sensor station or monitored slope location."
)
def create_location(location_in: LocationCreate, db: Session = Depends(get_db)):
    db_loc = Location(**location_in.model_dump())
    db.add(db_loc)
    db.commit()
    db.refresh(db_loc)
    return db_loc


@router.get(
    "/{location_id}",
    response_model=LocationDetailResponse,
    summary="Get Location Details",
    description="Retrieve detailed information for a single location including latest environmental telemetry, current AI risk prediction, recent alerts, risk history, and historical events."
)
def get_location_details(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    # 1. Latest Environmental Reading
    latest_env = (
        db.query(EnvironmentalData)
        .filter(EnvironmentalData.location_id == location_id)
        .order_by(desc(EnvironmentalData.recorded_at))
        .first()
    )

    # 2. Latest AI Risk Prediction
    latest_pred = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.location_id == location_id)
        .order_by(desc(RiskPrediction.prediction_time))
        .first()
    )

    # 3. Recent Alerts (last 10)
    alerts = (
        db.query(Alert)
        .filter(Alert.location_id == location_id)
        .order_by(desc(Alert.created_at))
        .limit(10)
        .all()
    )
    alerts_payload = [
        AlertResponse(
            id=a.id,
            location_id=a.location_id,
            risk_prediction_id=a.risk_prediction_id,
            alert_type=a.alert_type,
            severity=a.severity,
            message=a.message,
            status=a.status,
            created_at=a.created_at,
            resolved_at=a.resolved_at,
            location_name=location.name,
            state=location.state
        )
        for a in alerts
    ]

    # 4. Recent Risk History (last 20 predictions)
    risk_history = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.location_id == location_id)
        .order_by(desc(RiskPrediction.prediction_time))
        .limit(20)
        .all()
    )

    # 5. Historical Landslide Events at or near this location
    events = (
        db.query(LandslideEvent)
        .filter(LandslideEvent.location_id == location_id)
        .order_by(desc(LandslideEvent.event_date))
        .all()
    )
    events_payload = [
        LandslideEventResponse(
            id=e.id,
            location_id=e.location_id,
            event_date=e.event_date,
            latitude=e.latitude,
            longitude=e.longitude,
            severity=e.severity,
            cause=e.cause,
            rainfall_before_event=e.rainfall_before_event,
            description=e.description,
            source=e.source,
            created_at=e.created_at,
            location_name=location.name,
            state=location.state
        )
        for e in events
    ]

    return LocationDetailResponse(
        id=location.id,
        name=location.name,
        state=location.state,
        district=location.district,
        latitude=location.latitude,
        longitude=location.longitude,
        elevation=location.elevation,
        slope=location.slope,
        vegetation_index=location.vegetation_index,
        risk_score=location.risk_score,
        risk_level=location.risk_level,
        created_at=location.created_at,
        updated_at=location.updated_at,
        latest_environmental_data=EnvironmentalDataResponse.model_validate(latest_env) if latest_env else None,
        latest_risk_prediction=PredictionResponse.model_validate(latest_pred) if latest_pred else None,
        recent_alerts=alerts_payload,
        recent_risk_history=[PredictionResponse.model_validate(p) for p in risk_history],
        historical_events=events_payload
    )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Location",
    description="Remove a monitored location from the system."
)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )
    db.delete(location)
    db.commit()
    return None
