import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .database import engine, Base, SessionLocal
from .models import Location, EnvironmentalData, RiskPrediction, Alert, LandslideEvent
from .routers import (
    locations_router,
    environmental_router,
    predictions_router,
    alerts_router,
    events_router,
    analytics_router,
)

# Load configuration
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("landslide_api")


def seed_demo_data_if_empty():
    """
    Automatically populates the database with realistic Northeast India
    locations and hazard telemetry if the database has 0 locations.
    """
    db = SessionLocal()
    try:
        count = db.query(Location).count()
        if count > 0:
            logger.info(f"Database already contains {count} locations. Skipping seed.")
            return

        logger.info("Database is empty. Seeding initial demonstration dataset...")
        now = datetime.now(timezone.utc)

        # 1. Monitored Locations across 8 Northeast States
        locations_data = [
            # Assam
            {"id": 1, "name": "Haflong Hill Sector 4", "state": "Assam", "district": "Dima Hasao", "latitude": 25.1764, "longitude": 93.0234, "elevation": 960.0, "slope": 38.5, "vegetation_index": 0.62, "risk_score": 84.5, "risk_level": "CRITICAL"},
            {"id": 2, "name": "Guwahati Kamakhya Hillside", "state": "Assam", "district": "Kamrup Metropolitan", "latitude": 26.1662, "longitude": 91.7058, "elevation": 245.0, "slope": 28.0, "vegetation_index": 0.48, "risk_score": 52.0, "risk_level": "MODERATE"},
            {"id": 3, "name": "Diphu Ridge Line", "state": "Assam", "district": "Karbi Anglong", "latitude": 25.8436, "longitude": 93.4326, "elevation": 186.0, "slope": 22.5, "vegetation_index": 0.71, "risk_score": 31.2, "risk_level": "LOW"},

            # Meghalaya
            {"id": 4, "name": "Cherrapunji Sohra Cliff", "state": "Meghalaya", "district": "East Khasi Hills", "latitude": 25.2702, "longitude": 91.7323, "elevation": 1430.0, "slope": 44.0, "vegetation_index": 0.54, "risk_score": 92.4, "risk_level": "CRITICAL"},
            {"id": 5, "name": "Shillong Peak Slopes", "state": "Meghalaya", "district": "East Khasi Hills", "latitude": 25.5348, "longitude": 91.8532, "elevation": 1965.0, "slope": 34.0, "vegetation_index": 0.68, "risk_score": 68.3, "risk_level": "HIGH"},
            {"id": 6, "name": "Mawsynram Valley Escarpment", "state": "Meghalaya", "district": "East Khasi Hills", "latitude": 25.2974, "longitude": 91.5826, "elevation": 1400.0, "slope": 42.0, "vegetation_index": 0.51, "risk_score": 88.0, "risk_level": "CRITICAL"},
            {"id": 7, "name": "Nongstoin Western Gradient", "state": "Meghalaya", "district": "West Khasi Hills", "latitude": 25.5222, "longitude": 91.2685, "elevation": 1409.0, "slope": 24.0, "vegetation_index": 0.76, "risk_score": 28.5, "risk_level": "LOW"},

            # Sikkim
            {"id": 8, "name": "Gangtok Vajra Ridge", "state": "Sikkim", "district": "East Sikkim", "latitude": 27.3389, "longitude": 88.6065, "elevation": 1650.0, "slope": 36.5, "vegetation_index": 0.59, "risk_score": 74.0, "risk_level": "HIGH"},
            {"id": 9, "name": "Mangan North Transit Corridor", "state": "Sikkim", "district": "Mangan", "latitude": 27.5056, "longitude": 88.5284, "elevation": 1310.0, "slope": 41.0, "vegetation_index": 0.64, "risk_score": 86.8, "risk_level": "CRITICAL"},
            {"id": 10, "name": "Namchi Central Slope", "state": "Sikkim", "district": "South Sikkim", "latitude": 27.1667, "longitude": 88.3500, "elevation": 1315.0, "slope": 26.0, "vegetation_index": 0.69, "risk_score": 45.0, "risk_level": "MODERATE"},
            {"id": 11, "name": "Singtam Teesta Valley Margin", "state": "Sikkim", "district": "East Sikkim", "latitude": 27.2346, "longitude": 88.4984, "elevation": 400.0, "slope": 31.0, "vegetation_index": 0.52, "risk_score": 62.1, "risk_level": "MODERATE"},

            # Arunachal Pradesh
            {"id": 12, "name": "Tawang Pass Hill Track", "state": "Arunachal Pradesh", "district": "Tawang", "latitude": 27.5861, "longitude": 91.8594, "elevation": 3048.0, "slope": 39.0, "vegetation_index": 0.42, "risk_score": 79.5, "risk_level": "HIGH"},
            {"id": 13, "name": "Itanagar Ganga Lake Rim", "state": "Arunachal Pradesh", "district": "Papum Pare", "latitude": 27.0844, "longitude": 93.6053, "elevation": 750.0, "slope": 29.5, "vegetation_index": 0.73, "risk_score": 41.0, "risk_level": "MODERATE"},
            {"id": 14, "name": "Bomdila West Kameng Crest", "state": "Arunachal Pradesh", "district": "West Kameng", "latitude": 27.2645, "longitude": 92.4228, "elevation": 2217.0, "slope": 37.0, "vegetation_index": 0.61, "risk_score": 71.3, "risk_level": "HIGH"},
            {"id": 15, "name": "Ziro Pine Ridge Foothills", "state": "Arunachal Pradesh", "district": "Lower Subansiri", "latitude": 27.5450, "longitude": 93.8290, "elevation": 1572.0, "slope": 18.0, "vegetation_index": 0.82, "risk_score": 22.0, "risk_level": "LOW"},

            # Nagaland
            {"id": 16, "name": "Kohima Bypass NH-29", "state": "Nagaland", "district": "Kohima", "latitude": 25.6751, "longitude": 94.1086, "elevation": 1444.0, "slope": 43.0, "vegetation_index": 0.57, "risk_score": 91.2, "risk_level": "CRITICAL"},
            {"id": 17, "name": "Mokokchung Outer Ring", "state": "Nagaland", "district": "Mokokchung", "latitude": 26.3256, "longitude": 94.5200, "elevation": 1325.0, "slope": 30.0, "vegetation_index": 0.65, "risk_score": 58.7, "risk_level": "MODERATE"},
            {"id": 18, "name": "Wokha Doyang Catchment Bluff", "state": "Nagaland", "district": "Wokha", "latitude": 26.0984, "longitude": 94.2612, "elevation": 1313.0, "slope": 33.0, "vegetation_index": 0.67, "risk_score": 64.0, "risk_level": "MODERATE"},

            # Manipur
            {"id": 19, "name": "Tamenglong Barak River Bank", "state": "Manipur", "district": "Tamenglong", "latitude": 24.9856, "longitude": 93.4925, "elevation": 1260.0, "slope": 40.5, "vegetation_index": 0.66, "risk_score": 83.0, "risk_level": "CRITICAL"},
            {"id": 20, "name": "Senapati Hill Highway", "state": "Manipur", "district": "Senapati", "latitude": 25.2678, "longitude": 94.0167, "elevation": 1140.0, "slope": 32.0, "vegetation_index": 0.63, "risk_score": 66.5, "risk_level": "HIGH"},
            {"id": 21, "name": "Imphal Langol Reserve Border", "state": "Manipur", "district": "Imphal West", "latitude": 24.8170, "longitude": 93.9368, "elevation": 785.0, "slope": 21.0, "vegetation_index": 0.75, "risk_score": 29.8, "risk_level": "LOW"},

            # Mizoram
            {"id": 22, "name": "Aizawl Bawngkawn Ridge", "state": "Mizoram", "district": "Aizawl", "latitude": 23.7538, "longitude": 92.7378, "elevation": 1132.0, "slope": 45.0, "vegetation_index": 0.53, "risk_score": 94.0, "risk_level": "CRITICAL"},
            {"id": 23, "name": "Lunglei Chanmari Slope", "state": "Mizoram", "district": "Lunglei", "latitude": 22.8872, "longitude": 92.7483, "elevation": 1222.0, "slope": 35.0, "vegetation_index": 0.62, "risk_score": 70.5, "risk_level": "HIGH"},

            # Tripura
            {"id": 24, "name": "Jampui Hills Orange Valley", "state": "Tripura", "district": "North Tripura", "latitude": 23.8200, "longitude": 92.2700, "elevation": 930.0, "slope": 25.0, "vegetation_index": 0.79, "risk_score": 27.5, "risk_level": "LOW"},
        ]

        for loc_dict in locations_data:
            loc = Location(**loc_dict)
            db.add(loc)
        db.commit()

        # 2. Environmental Readings
        env_readings = [
            (1, 142.5, 18.0, 89.2, 21.5, 96.0, 38.5, 960.0, 0.62, 0),
            (1, 110.0, 12.0, 81.0, 22.0, 93.0, 38.5, 960.0, 0.62, 6),
            (1, 75.2, 8.0, 72.4, 23.0, 88.0, 38.5, 960.0, 0.62, 12),
            (2, 45.0, 5.0, 56.0, 28.0, 82.0, 28.0, 245.0, 0.48, 0),
            (3, 12.0, 1.5, 35.0, 27.5, 68.0, 22.5, 186.0, 0.71, 0),
            (4, 210.0, 24.0, 94.5, 18.2, 99.0, 44.0, 1430.0, 0.54, 0),
            (4, 180.0, 20.0, 91.0, 18.5, 98.0, 44.0, 1430.0, 0.54, 6),
            (5, 78.0, 9.0, 71.0, 16.0, 90.0, 34.0, 1965.0, 0.68, 0),
            (6, 195.0, 22.0, 92.0, 18.0, 98.0, 42.0, 1400.0, 0.51, 0),
            (8, 88.0, 11.0, 76.5, 15.0, 91.0, 36.5, 1650.0, 0.59, 0),
            (9, 155.0, 19.0, 88.5, 14.2, 97.0, 41.0, 1310.0, 0.64, 0),
            (12, 65.0, 8.0, 73.0, 9.0, 89.0, 39.0, 3048.0, 0.42, 0),
            (16, 165.0, 20.0, 93.0, 19.0, 97.0, 43.0, 1444.0, 0.57, 0),
            (19, 135.0, 16.0, 87.0, 22.0, 94.0, 40.5, 1260.0, 0.66, 0),
            (22, 175.0, 21.0, 95.0, 21.0, 98.0, 45.0, 1132.0, 0.53, 0),
        ]
        for loc_id, rain, r_dur, soil, temp, hum, slp, elev, veg, hrs_ago in env_readings:
            e = EnvironmentalData(
                location_id=loc_id,
                rainfall=rain,
                rainfall_duration=r_dur,
                soil_moisture=soil,
                temperature=temp,
                humidity=hum,
                slope=slp,
                elevation=elev,
                vegetation_index=veg,
                recorded_at=now - timedelta(hours=hrs_ago)
            )
            db.add(e)
        db.commit()

        # 3. Risk Predictions
        predictions_data = [
            (1, 84.5, "CRITICAL", 0.92, 35.0, 28.0, 16.5, 3.0, 2.0, 0),
            (1, 76.0, "HIGH", 0.88, 29.0, 24.5, 16.5, 3.0, 3.0, 6),
            (4, 92.4, "CRITICAL", 0.95, 42.0, 29.5, 17.5, 2.0, 1.4, 0),
            (5, 68.3, "HIGH", 0.87, 26.0, 22.0, 14.3, 3.5, 2.5, 0),
            (6, 88.0, "CRITICAL", 0.94, 39.0, 28.0, 16.8, 2.2, 2.0, 0),
            (8, 74.0, "HIGH", 0.89, 28.0, 23.5, 15.2, 4.3, 3.0, 0),
            (9, 86.8, "CRITICAL", 0.93, 37.0, 27.0, 17.0, 3.2, 2.6, 0),
            (16, 91.2, "CRITICAL", 0.94, 40.0, 28.8, 17.2, 3.2, 2.0, 0),
            (19, 83.0, "CRITICAL", 0.91, 34.0, 26.5, 16.4, 3.1, 3.0, 0),
            (22, 94.0, "CRITICAL", 0.96, 43.0, 30.0, 17.8, 2.2, 1.0, 0),
        ]
        pred_map = {}
        for idx, (loc_id, r_sc, r_lv, conf, r_imp, s_imp, sl_imp, el_imp, veg_imp, hrs_ago) in enumerate(predictions_data, start=1):
            p = RiskPrediction(
                id=idx,
                location_id=loc_id,
                risk_score=r_sc,
                risk_level=r_lv,
                confidence=conf,
                rainfall_impact=r_imp,
                soil_moisture_impact=s_imp,
                slope_impact=sl_imp,
                elevation_impact=el_imp,
                vegetation_impact=veg_imp,
                prediction_time=now - timedelta(hours=hrs_ago)
            )
            db.add(p)
            pred_map[idx] = p
        db.commit()

        # 4. Landslide Events
        events_data = [
            (1, now - timedelta(days=110), 25.1764, 93.0234, "CRITICAL", "Heavy Monsoon Inundation & Slope Over-saturation", 185.4, "Massive mudslide along Haflong railway junction track severing south Assam train connections.", "Assam State Disaster Management Authority (ASDMA)"),
            (4, now - timedelta(days=450), 25.2702, 91.7323, "CRITICAL", "Extreme Flash Rainfall & Cliff Instability", 312.0, "Debris flow near Sohra-Shella highway leading to rockslides blocking border logistics.", "Meghalaya SDMA & GSI"),
            (9, now - timedelta(days=345), 27.5056, 88.5284, "CRITICAL", "Glacial Lake Outburst & Severe River Bank Erosion", 140.0, "Flash flood surge along Teesta river causing slope toes collapse across Mangan highway stretch.", "Sikkim Disaster Management Authority"),
            (16, now - timedelta(days=65), 25.6751, 94.1086, "HIGH", "Continuous Precipitation & Hill Cutting", 124.6, "Substantial soil slippage along National Highway 29 halting interstate trucking corridor.", "Nagaland NSDMA Report"),
            (22, now - timedelta(days=109), 23.7538, 92.7378, "CRITICAL", "Cyclone Remal Remnant Downpour", 210.5, "Severe rockfall and landslide at multiple quarry and hillside zones around Aizawl town periphery.", "Mizoram Disaster Management"),
            (5, now - timedelta(days=750), 25.5348, 91.8532, "MODERATE", "Prolonged Seepage on Steep Cut Slope", 82.0, "Minor earth slide along upper Shillong arterial bypass causing traffic detour.", "PWD Meghalaya"),
        ]
        for loc_id, dt, lat, lon, sev, cause, rain, desc, src in events_data:
            ev = LandslideEvent(
                location_id=loc_id,
                event_date=dt,
                latitude=lat,
                longitude=lon,
                severity=sev,
                cause=cause,
                rainfall_before_event=rain,
                description=desc,
                source=src,
                created_at=now
            )
            db.add(ev)
        db.commit()

        # 5. Alerts
        alerts_data = [
            (22, 10, "CRITICAL", "CRITICAL", "EVACUATION WARNING: Extreme landslide hazard detected at Aizawl Bawngkawn Ridge (Risk: 94%). Soil moisture exceeds 95%.", "ACTIVE", 1, None),
            (4, 3, "CRITICAL", "CRITICAL", "RED ALERT: Extreme precipitation (>210mm) and high cliff instability at Cherrapunji Sohra Cliff. High risk of rockfalls.", "ACTIVE", 2, None),
            (16, 8, "LANDSLIDE", "CRITICAL", "ROAD CLOSURE ALERT: Impending slope failure detected along NH-29 Kohima Bypass corridor. Traffic diverted.", "ACTIVE", 3, None),
            (1, 1, "WARNING", "HIGH", "HIGH HAZARD: Haflong Hill Sector 4 risk score elevated to 84.5%. Continuous heavy rain forecast for next 12 hours.", "ACTIVE", 4, None),
            (9, 7, "CRITICAL", "CRITICAL", "TEESTA BASIN ADVISORY: Mangan North Transit corridor shows critical ground deformation and high saturation.", "ACTIVE", 5, None),
            (8, 6, "WEATHER", "HIGH", "WEATHER ALERT: Sustained heavy monsoon downpour approaching Gangtok Vajra ridge. Monitoring sensors online.", "ACTIVE", 6, None),
            (5, 4, "WARNING", "MODERATE", "Precautionary advisory for Shillong Peak road segment due to moderate earth slippage.", "RESOLVED", 48, now - timedelta(hours=24)),
        ]
        for loc_id, pred_id, a_type, sev, msg, stat, hrs_ago, res_at in alerts_data:
            alt = Alert(
                location_id=loc_id,
                risk_prediction_id=pred_id,
                alert_type=a_type,
                severity=sev,
                message=msg,
                status=stat,
                created_at=now - timedelta(hours=hrs_ago),
                resolved_at=res_at
            )
            db.add(alt)
        db.commit()

        logger.info("Demonstration data successfully populated.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding demo data: {e}", exc_info=True)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown management."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Checking initial demo dataset...")
    seed_demo_data_if_empty()
    yield
    logger.info("Shutting down application...")


# FastAPI Application instance
app = FastAPI(
    title="AI-Based Landslide Risk Monitoring System",
    description=(
        "Production-grade Backend API & PostgreSQL Database Layer for SIH 2026. "
        "Delivers real-time topographical landslide risk analytics, AI inference, "
        "sensor telemetry, early warning alerts, and historical hazard tracking across Northeast India."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173")
origins: List[str] = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
if "*" not in origins and len(origins) == 0:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    # Sanitize error message to prevent database password or credentials leaking
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing the request."}
    )


# Register Routers
app.include_router(locations_router)
app.include_router(environmental_router)
app.include_router(predictions_router)
app.include_router(alerts_router)
app.include_router(events_router)
app.include_router(analytics_router)


@app.get("/", tags=["System"])
def root_discovery():
    """System health and API discovery overview."""
    return {
        "system": "AI-Based Landslide Risk Monitoring System",
        "edition": "SIH 2026",
        "status": "ONLINE",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "locations": "/api/v1/locations",
            "active_alerts": "/api/v1/alerts/active",
            "analytics_kpi": "/api/v1/analytics",
            "risk_prediction": "/api/v1/predict",
            "historical_events": "/api/v1/landslide-events"
        }
    }


@app.get("/health", tags=["System"])
def health_check():
    """Quick liveness probe."""
    return {"status": "HEALTHY", "timestamp": datetime.now(timezone.utc).isoformat()}
