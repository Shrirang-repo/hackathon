import pytest
from fastapi.testclient import TestClient

from app.main import app, seed_demo_data_if_empty
from app.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database tables and initial seed data are loaded."""
    Base.metadata.create_all(bind=engine)
    seed_demo_data_if_empty()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ------------------------------------------------------------------------------
# 1. Database Connection & System Health Tests
# ------------------------------------------------------------------------------
def test_root_discovery(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "endpoints" in data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


# ------------------------------------------------------------------------------
# 2. Locations API Tests
# ------------------------------------------------------------------------------
def test_get_locations(client):
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    locations = response.json()
    assert isinstance(locations, list)
    assert len(locations) > 0

    first = locations[0]
    # Check exact field names expected by frontend
    assert "id" in first
    assert "name" in first
    assert "state" in first
    assert "district" in first
    assert "latitude" in first
    assert "longitude" in first
    assert "elevation" in first
    assert "slope" in first
    assert "vegetation_index" in first
    assert "risk_score" in first
    assert "risk_level" in first


def test_get_locations_with_filter(client):
    response = client.get("/api/v1/locations?state=Assam")
    assert response.status_code == 200
    assam_locs = response.json()
    assert len(assam_locs) > 0
    for loc in assam_locs:
        assert "Assam" in loc["state"]


def test_get_location_details_success(client):
    # Retrieve first valid location
    locs = client.get("/api/v1/locations").json()
    loc_id = locs[0]["id"]

    response = client.get(f"/api/v1/locations/{loc_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == loc_id
    assert "name" in detail
    assert "state" in detail
    assert "latest_environmental_data" in detail
    assert "latest_risk_prediction" in detail
    assert "recent_alerts" in detail
    assert "recent_risk_history" in detail
    assert "historical_events" in detail


def test_get_location_details_404(client):
    response = client.get("/api/v1/locations/99999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 3. Environmental Data API Tests
# ------------------------------------------------------------------------------
def test_get_latest_environmental_data(client):
    response = client.get("/api/v1/locations/1/environment")
    assert response.status_code == 200
    env = response.json()
    assert env["location_id"] == 1
    assert "rainfall" in env
    assert "soil_moisture" in env
    assert "humidity" in env
    assert "temperature" in env
    assert "slope" in env
    assert "elevation" in env


def test_get_environmental_history(client):
    response = client.get("/api/v1/locations/1/environment/history?limit=10")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0


def test_get_environmental_data_invalid_location(client):
    response = client.get("/api/v1/locations/99999999/environment")
    assert response.status_code == 404


# ------------------------------------------------------------------------------
# 4. Risk Prediction API Tests
# ------------------------------------------------------------------------------
def test_predict_risk_calculation(client):
    payload = {
        "location_id": 1,
        "rainfall": 150.0,
        "rainfall_duration": 12.0,
        "soil_moisture": 88.0,
        "temperature": 21.0,
        "humidity": 95.0,
        "slope": 42.0,
        "elevation": 1200.0,
        "vegetation_index": 0.45
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 201
    pred = response.json()

    assert pred["risk_score"] >= 0.0 and pred["risk_score"] <= 100.0
    assert pred["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert pred["confidence"] >= 0.0 and pred["confidence"] <= 1.0
    assert "rainfall_impact" in pred
    assert "soil_moisture_impact" in pred
    assert "slope_impact" in pred
    assert "elevation_impact" in pred
    assert "vegetation_impact" in pred
    assert "prediction_time" in pred

    # Verify location was updated
    loc_resp = client.get("/api/v1/locations/1")
    assert loc_resp.status_code == 200
    assert loc_resp.json()["risk_level"] == pred["risk_level"]


def test_predict_validation_error(client):
    # Send negative rainfall which breaks validation constraint
    invalid_payload = {
        "rainfall": -50.0,
        "soil_moisture": 80.0,
        "slope": 30.0,
        "elevation": 500.0,
        "vegetation_index": 0.5
    }
    response = client.post("/api/v1/predict", json=invalid_payload)
    assert response.status_code == 422


# ------------------------------------------------------------------------------
# 5. Alerts API Tests
# ------------------------------------------------------------------------------
def test_get_alerts(client):
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0


def test_get_active_alerts(client):
    response = client.get("/api/v1/alerts/active")
    assert response.status_code == 200
    active = response.json()
    assert isinstance(active, list)
    for a in active:
        assert a["status"] == "ACTIVE"


def test_create_and_resolve_alert(client):
    # 1. Create alert
    new_alert = {
        "location_id": 2,
        "alert_type": "WARNING",
        "severity": "HIGH",
        "message": "Heavy downpour expected in next 2 hours over Kamakhya hills."
    }
    create_resp = client.post("/api/v1/alerts", json=new_alert)
    assert create_resp.status_code == 201
    alert_obj = create_resp.json()
    assert alert_obj["status"] == "ACTIVE"
    alert_id = alert_obj["id"]

    # 2. Resolve alert
    resolve_resp = client.patch(f"/api/v1/alerts/{alert_id}/resolve")
    assert resolve_resp.status_code == 200
    resolved_obj = resolve_resp.json()
    assert resolved_obj["status"] == "RESOLVED"
    assert resolved_obj["resolved_at"] is not None


# ------------------------------------------------------------------------------
# 6. Landslide Events API Tests
# ------------------------------------------------------------------------------
def test_get_landslide_events(client):
    response = client.get("/api/v1/landslide-events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) > 0
    first = events[0]
    assert "event_date" in first
    assert "latitude" in first
    assert "longitude" in first
    assert "severity" in first
    assert "cause" in first


# ------------------------------------------------------------------------------
# 7. Analytics API Tests
# ------------------------------------------------------------------------------
def test_get_analytics(client):
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    analytics = response.json()

    assert analytics["total_monitored_locations"] > 0
    assert analytics["critical_risk_locations"] >= 0
    assert analytics["high_risk_locations"] >= 0
    assert analytics["moderate_risk_locations"] >= 0
    assert analytics["low_risk_locations"] >= 0
    assert analytics["active_alerts"] >= 0
    assert analytics["total_historical_landslide_events"] >= 0
    assert analytics["average_risk_score"] >= 0.0

    assert isinstance(analytics["risk_distribution"], list)
    assert len(analytics["risk_distribution"]) == 4
    assert isinstance(analytics["state_wise_summary"], list)
    assert len(analytics["state_wise_summary"]) > 0
    assert isinstance(analytics["risk_trend_24h"], list)
    assert len(analytics["risk_trend_24h"]) > 0
