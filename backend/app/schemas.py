from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------------------------------------------------
# Environmental Data Schemas
# ------------------------------------------------------------------------------
class EnvironmentalDataBase(BaseModel):
    rainfall: float = Field(..., ge=0.0, description="Precipitation in mm")
    rainfall_duration: float = Field(..., ge=0.0, description="Duration in hours")
    soil_moisture: float = Field(..., ge=0.0, description="Soil saturation percentage")
    temperature: float = Field(..., description="Ambient temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity %")
    slope: float = Field(..., ge=0.0, le=90.0, description="Slope steepness in degrees")
    elevation: float = Field(..., description="Elevation above sea level in meters")
    vegetation_index: float = Field(..., ge=-1.0, le=1.0, description="Normalized Difference Vegetation Index (NDVI)")


class EnvironmentalDataCreate(EnvironmentalDataBase):
    recorded_at: Optional[datetime] = None


class EnvironmentalDataResponse(EnvironmentalDataBase):
    id: int
    location_id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Risk Prediction Schemas
# ------------------------------------------------------------------------------
class PredictionInput(BaseModel):
    location_id: Optional[int] = Field(None, description="Optional target location ID to update")
    rainfall: float = Field(..., ge=0.0, description="Recent rainfall in mm")
    rainfall_duration: float = Field(1.0, ge=0.0, description="Duration of rainfall in hours")
    soil_moisture: float = Field(..., ge=0.0, description="Soil moisture level %")
    temperature: Optional[float] = Field(22.0, description="Temperature in °C")
    humidity: Optional[float] = Field(80.0, ge=0.0, le=100.0, description="Humidity %")
    slope: float = Field(..., ge=0.0, le=90.0, description="Slope inclination in degrees")
    elevation: float = Field(..., description="Elevation in meters")
    vegetation_index: float = Field(..., ge=-1.0, le=1.0, description="Vegetation index / NDVI")


class PredictionResponse(BaseModel):
    id: Optional[int] = None
    location_id: Optional[int] = None
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Landslide risk score (0-100)")
    risk_level: str = Field(..., description="Risk category: LOW, MODERATE, HIGH, CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model prediction confidence")
    rainfall_impact: float = Field(..., description="Rainfall contribution to risk score")
    soil_moisture_impact: float = Field(..., description="Soil moisture contribution")
    slope_impact: float = Field(..., description="Slope steepness contribution")
    elevation_impact: float = Field(..., description="Elevation contribution")
    vegetation_impact: float = Field(..., description="Vegetation mitigating/contributing factor")
    prediction_time: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Location Schemas
# ------------------------------------------------------------------------------
class LocationBase(BaseModel):
    name: str = Field(..., max_length=150, description="Location/Site name")
    state: str = Field(..., max_length=100, description="State (e.g., Assam, Meghalaya)")
    district: str = Field(..., max_length=100, description="District name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Geographic latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Geographic longitude")
    elevation: float = Field(..., description="Elevation in meters")
    slope: float = Field(..., ge=0.0, le=90.0, description="Slope gradient in degrees")
    vegetation_index: float = Field(..., ge=-1.0, le=1.0, description="NDVI vegetation index")


class LocationCreate(LocationBase):
    risk_score: Optional[float] = Field(0.0, ge=0.0, le=100.0)
    risk_level: Optional[str] = Field("LOW")


class LocationResponse(LocationBase):
    id: int
    risk_score: float
    risk_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Alert Schemas
# ------------------------------------------------------------------------------
class AlertBase(BaseModel):
    location_id: int
    risk_prediction_id: Optional[int] = None
    alert_type: str = Field(..., description="WARNING, CRITICAL, WEATHER, LANDSLIDE")
    severity: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")
    message: str = Field(..., description="Alert detail message")


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    status: str = Field("ACTIVE", description="ACTIVE or RESOLVED")
    created_at: datetime
    resolved_at: Optional[datetime] = None
    location_name: Optional[str] = None
    state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Landslide Event Schemas
# ------------------------------------------------------------------------------
class LandslideEventBase(BaseModel):
    location_id: Optional[int] = None
    event_date: datetime
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    severity: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")
    cause: str = Field(..., max_length=255)
    rainfall_before_event: Optional[float] = Field(0.0, ge=0.0)
    description: Optional[str] = None
    source: Optional[str] = None


class LandslideEventCreate(LandslideEventBase):
    pass


class LandslideEventResponse(LandslideEventBase):
    id: int
    created_at: datetime
    location_name: Optional[str] = None
    state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Detailed Location Response (Nested relations for single location page)
# ------------------------------------------------------------------------------
class LocationDetailResponse(LocationResponse):
    latest_environmental_data: Optional[EnvironmentalDataResponse] = None
    latest_risk_prediction: Optional[PredictionResponse] = None
    recent_alerts: List[AlertResponse] = []
    recent_risk_history: List[PredictionResponse] = []
    historical_events: List[LandslideEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Analytics & Dashboard Aggregation Schemas
# ------------------------------------------------------------------------------
class StateRiskSummary(BaseModel):
    state: str
    total_locations: int
    average_risk_score: float
    critical_count: int
    high_count: int
    moderate_count: int
    low_count: int


class RiskDistributionSummary(BaseModel):
    risk_level: str
    count: int
    percentage: float


class RiskTrendPoint(BaseModel):
    timestamp: str
    average_risk_score: float


class AnalyticsSummaryResponse(BaseModel):
    total_monitored_locations: int
    low_risk_locations: int
    moderate_risk_locations: int
    high_risk_locations: int
    critical_risk_locations: int
    active_alerts: int
    total_historical_landslide_events: int
    average_risk_score: float
    risk_distribution: List[RiskDistributionSummary]
    state_wise_summary: List[StateRiskSummary]
    risk_trend_24h: List[RiskTrendPoint]
