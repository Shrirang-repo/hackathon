from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import Alert, Location
from ..schemas import AlertResponse, AlertCreate

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Alerts"]
)


def _enrich_alert_response(alert: Alert) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        location_id=alert.location_id,
        risk_prediction_id=alert.risk_prediction_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        status=alert.status,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
        location_name=alert.location.name if alert.location else None,
        state=alert.location.state if alert.location else None
    )


@router.get(
    "",
    response_model=List[AlertResponse],
    summary="Get Alerts",
    description="Retrieve landslide warnings and hazard alerts with multi-criteria filtering."
)
def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE or RESOLVED"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MODERATE, HIGH, CRITICAL"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    state: Optional[str] = Query(None, description="Filter by state"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Alert).join(Location, Alert.location_id == Location.id)

    if status:
        query = query.filter(Alert.status == status.upper())
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if location_id:
        query = query.filter(Alert.location_id == location_id)
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))

    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    return [_enrich_alert_response(a) for a in alerts]


@router.get(
    "/active",
    response_model=List[AlertResponse],
    summary="Get Active Alerts",
    description="Retrieve all currently active hazard alerts prioritized by severity and recency."
)
def get_active_alerts(
    state: Optional[str] = Query(None, description="Filter active alerts by state"),
    db: Session = Depends(get_db)
):
    query = db.query(Alert).join(Location, Alert.location_id == Location.id).filter(Alert.status == "ACTIVE")
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))

    alerts = query.order_by(
        desc(Alert.severity == "CRITICAL"),
        desc(Alert.severity == "HIGH"),
        desc(Alert.created_at)
    ).all()

    return [_enrich_alert_response(a) for a in alerts]


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Alert",
    description="Dispatch a new landslide or weather hazard alert."
)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == alert_in.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {alert_in.location_id} not found."
        )

    db_alert = Alert(
        location_id=alert_in.location_id,
        risk_prediction_id=alert_in.risk_prediction_id,
        alert_type=alert_in.alert_type.upper(),
        severity=alert_in.severity.upper(),
        message=alert_in.message,
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    return _enrich_alert_response(db_alert)


@router.patch(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve Alert",
    description="Mark an active warning as resolved."
)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found."
        )

    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)

    return _enrich_alert_response(alert)
