"""
API Routers Package
"""
from .locations import router as locations_router
from .environmental import router as environmental_router
from .predictions import router as predictions_router
from .alerts import router as alerts_router
from .events import router as events_router
from .analytics import router as analytics_router

__all__ = [
    "locations_router",
    "environmental_router",
    "predictions_router",
    "alerts_router",
    "events_router",
    "analytics_router"
]
