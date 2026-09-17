"""
Service Layer for Landslide Risk Modeling and AI Inference
"""
from .risk_service import risk_engine, calculate_landslide_risk

__all__ = ["risk_engine", "calculate_landslide_risk"]
