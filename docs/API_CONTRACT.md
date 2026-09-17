# Project Sentinel API Contract

## 1. Health Check

GET /health

Response:

{
  "status": "ok"
}

---

## 2. Risk Prediction

POST /api/v1/predict

Request:

{
  "latitude": 26.1445,
  "longitude": 91.7362,
  "rainfall": 120,
  "rainfall_duration": 6,
  "soil_moisture": 75,
  "slope": 38,
  "elevation": 850,
  "vegetation_index": 0.42
}

Response:

{
  "risk_score": 82,
  "risk_level": "HIGH",
  "confidence": 0.84,
  "factors": [],
  "recommended_actions": []
}

---

## 3. Locations

GET /api/v1/locations

Returns the list of monitored locations.

---

## 4. Location Details

GET /api/v1/locations/{location_id}

Returns detailed information about one monitored location.

---

## 5. Alerts

GET /api/v1/alerts

Returns active and historical alerts.

---

## 6. Analytics

GET /api/v1/analytics

Returns dashboard statistics and risk analytics.

---

# Environmental Input Fields

Use these exact names:

latitude

longitude

rainfall

rainfall_duration

soil_moisture

slope

elevation

vegetation_index

---

# Risk Output Fields

Use these exact names:

risk_score

risk_level

confidence

factors

recommended_actions

---

# Risk Levels

LOW = 0-24

MODERATE = 25-49

HIGH = 50-74

CRITICAL = 75-100

These are prototype thresholds and may be changed after model validation.

---

# Integration Flow

Frontend

↓

FastAPI Backend

↓

ML Risk Engine

↓

Database

↓

FastAPI Backend

↓

Frontend
