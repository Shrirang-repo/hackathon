from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    slope = Column(Float, nullable=False)
    vegetation_index = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(20), nullable=False, default="LOW", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("latitude >= -90.0 AND latitude <= 90.0", name="chk_location_latitude"),
        CheckConstraint("longitude >= -180.0 AND longitude <= 180.0", name="chk_location_longitude"),
        CheckConstraint("risk_score >= 0.0 AND risk_score <= 100.0", name="chk_location_risk_score"),
        CheckConstraint("risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')", name="chk_location_risk_level"),
        CheckConstraint("slope >= 0.0 AND slope <= 90.0", name="chk_location_slope"),
        CheckConstraint("vegetation_index >= -1.0 AND vegetation_index <= 1.0", name="chk_location_vegetation"),
        Index("idx_location_lat_long", "latitude", "longitude"),
    )

    # Relationships
    environmental_data = relationship(
        "EnvironmentalData",
        back_populates="location",
        cascade="all, delete-orphan",
        order_by="desc(EnvironmentalData.recorded_at)"
    )
    risk_predictions = relationship(
        "RiskPrediction",
        back_populates="location",
        cascade="all, delete-orphan",
        order_by="desc(RiskPrediction.prediction_time)"
    )
    landslide_events = relationship(
        "LandslideEvent",
        back_populates="location",
        order_by="desc(LandslideEvent.event_date)"
    )
    alerts = relationship(
        "Alert",
        back_populates="location",
        cascade="all, delete-orphan",
        order_by="desc(Alert.created_at)"
    )


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    rainfall = Column(Float, nullable=False)
    rainfall_duration = Column(Float, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    slope = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    vegetation_index = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("rainfall >= 0.0", name="chk_env_rainfall"),
        CheckConstraint("rainfall_duration >= 0.0", name="chk_env_duration"),
        CheckConstraint("soil_moisture >= 0.0", name="chk_env_moisture"),
        CheckConstraint("humidity >= 0.0 AND humidity <= 100.0", name="chk_env_humidity"),
        CheckConstraint("slope >= 0.0 AND slope <= 90.0", name="chk_env_slope"),
        CheckConstraint("vegetation_index >= -1.0 AND vegetation_index <= 1.0", name="chk_env_vegetation"),
        Index("idx_env_loc_time", "location_id", "recorded_at"),
    )

    # Relationship
    location = relationship("Location", back_populates="environmental_data")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    rainfall_impact = Column(Float, nullable=False, default=0.0)
    soil_moisture_impact = Column(Float, nullable=False, default=0.0)
    slope_impact = Column(Float, nullable=False, default=0.0)
    elevation_impact = Column(Float, nullable=False, default=0.0)
    vegetation_impact = Column(Float, nullable=False, default=0.0)
    prediction_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("risk_score >= 0.0 AND risk_score <= 100.0", name="chk_pred_risk_score"),
        CheckConstraint("risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')", name="chk_pred_risk_level"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_pred_confidence"),
        CheckConstraint("rainfall_impact >= 0.0", name="chk_pred_rain_impact"),
        CheckConstraint("soil_moisture_impact >= 0.0", name="chk_pred_soil_impact"),
        CheckConstraint("slope_impact >= 0.0", name="chk_pred_slope_impact"),
        CheckConstraint("elevation_impact >= 0.0", name="chk_pred_elev_impact"),
        CheckConstraint("vegetation_impact >= 0.0", name="chk_pred_veg_impact"),
        Index("idx_pred_loc_time", "location_id", "prediction_time"),
    )

    # Relationships
    location = relationship("Location", back_populates="risk_predictions")
    alerts = relationship("Alert", back_populates="risk_prediction")


class LandslideEvent(Base):
    __tablename__ = "landslide_events"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    cause = Column(String(255), nullable=False)
    rainfall_before_event = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    source = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("latitude >= -90.0 AND latitude <= 90.0", name="chk_event_latitude"),
        CheckConstraint("longitude >= -180.0 AND longitude <= 180.0", name="chk_event_longitude"),
        CheckConstraint("severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')", name="chk_event_severity"),
        CheckConstraint("rainfall_before_event >= 0.0", name="chk_event_rainfall"),
        Index("idx_event_coords", "latitude", "longitude"),
    )

    # Relationship
    location = relationship("Location", back_populates="landslide_events")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_prediction_id = Column(Integer, ForeignKey("risk_predictions.id", ondelete="SET NULL"), nullable=True)
    alert_type = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("alert_type IN ('WARNING', 'CRITICAL', 'WEATHER', 'LANDSLIDE')", name="chk_alert_type"),
        CheckConstraint("severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')", name="chk_alert_severity"),
        CheckConstraint("status IN ('ACTIVE', 'RESOLVED')", name="chk_alert_status"),
        Index("idx_alert_status_created", "status", "created_at"),
    )

    # Relationships
    location = relationship("Location", back_populates="alerts")
    risk_prediction = relationship("RiskPrediction", back_populates="alerts")
