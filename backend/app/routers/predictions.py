from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import Location, RiskPrediction, Alert
from ..schemas import PredictionInput, PredictionResponse
from ..services.risk_service import calculate_landslide_risk

router = APIRouter(
    prefix="/api/v1",
    tags=["Risk Predictions"]
)


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compute Landslide Risk Prediction",
    description="Run the AI risk prediction engine with incoming environmental and topographical parameters, persist the inference, and update location state."
)
def predict_risk(input_data: PredictionInput, db: Session = Depends(get_db)):
    # 1. Run inference using the decoupled risk service engine
    calc_results = calculate_landslide_risk(input_data.model_dump())

    # 2. Check if this is associated with a tracked location
    target_location = None
    if input_data.location_id:
        target_location = db.query(Location).filter(Location.id == input_data.location_id).first()
        if not target_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target location with ID {input_data.location_id} not found."
            )

    # 3. Create and persist RiskPrediction record
    db_pred = RiskPrediction(
        location_id=target_location.id if target_location else None,
        risk_score=calc_results["risk_score"],
        risk_level=calc_results["risk_level"],
        confidence=calc_results["confidence"],
        rainfall_impact=calc_results["rainfall_impact"],
        soil_moisture_impact=calc_results["soil_moisture_impact"],
        slope_impact=calc_results["slope_impact"],
        elevation_impact=calc_results["elevation_impact"],
        vegetation_impact=calc_results["vegetation_impact"],
        prediction_time=calc_results.get("prediction_time", datetime.now(timezone.utc))
    )

    if target_location:
        # Update location current risk profile
        target_location.risk_score = calc_results["risk_score"]
        target_location.risk_level = calc_results["risk_level"]
        target_location.updated_at = datetime.now(timezone.utc)
        db.add(target_location)

    # Note: If target_location is not provided, we only store in risk_predictions if a default location or null FK allows it.
    # Because risk_predictions.location_id is NOT NULL in the schema, if location_id is not given, we can link to first location or raise validation.
    if not target_location:
        # Default to first location if not provided
        first_loc = db.query(Location).first()
        if first_loc:
            db_pred.location_id = first_loc.id

    if db_pred.location_id is not None:
        db.add(db_pred)
        db.commit()
        db.refresh(db_pred)

        # 4. Trigger automated alerts if hazard level is elevated
        if calc_results["risk_level"] in ("CRITICAL", "HIGH") and target_location:
            # Check if there is already an active alert for this location
            existing_alert = (
                db.query(Alert)
                .filter(Alert.location_id == target_location.id, Alert.status == "ACTIVE")
                .first()
            )
            if not existing_alert:
                alert_type = "CRITICAL" if calc_results["risk_level"] == "CRITICAL" else "WARNING"
                auto_alert = Alert(
                    location_id=target_location.id,
                    risk_prediction_id=db_pred.id,
                    alert_type=alert_type,
                    severity=calc_results["risk_level"],
                    message=(
                        f"Automated Alert: Landslide hazard {calc_results['risk_level']} "
                        f"detected at {target_location.name} (Risk Score: {calc_results['risk_score']}%). "
                        f"Primary factors: Rainfall impact ({calc_results['rainfall_impact']}), "
                        f"Soil moisture impact ({calc_results['soil_moisture_impact']})."
                    ),
                    status="ACTIVE",
                    created_at=datetime.now(timezone.utc)
                )
                db.add(auto_alert)
                db.commit()

    return PredictionResponse(
        id=db_pred.id if db_pred.id else None,
        location_id=db_pred.location_id if db_pred.location_id else None,
        risk_score=calc_results["risk_score"],
        risk_level=calc_results["risk_level"],
        confidence=calc_results["confidence"],
        rainfall_impact=calc_results["rainfall_impact"],
        soil_moisture_impact=calc_results["soil_moisture_impact"],
        slope_impact=calc_results["slope_impact"],
        elevation_impact=calc_results["elevation_impact"],
        vegetation_impact=calc_results["vegetation_impact"],
        prediction_time=calc_results["prediction_time"]
    )


@router.get(
    "/locations/{location_id}/predictions",
    response_model=List[PredictionResponse],
    summary="Get Location Risk Predictions History",
    description="Retrieve historical risk predictions for a specific location."
)
def get_location_predictions(
    location_id: int,
    limit: int = Query(50, ge=1, le=500, description="Max predictions to retrieve"),
    db: Session = Depends(get_db)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    preds = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.location_id == location_id)
        .order_by(desc(RiskPrediction.prediction_time))
        .limit(limit)
        .all()
    )
    return preds
