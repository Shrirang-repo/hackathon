-- ==============================================================================
-- AI-Based Landslide Risk Monitoring System
-- Database Schema (PostgreSQL / Supabase Compatible)
-- ==============================================================================

-- Enable UUID extension if needed (compatible with Supabase standard extensions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables in reverse dependency order for clean reinstalls
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS landslide_events CASCADE;
DROP TABLE IF EXISTS risk_predictions CASCADE;
DROP TABLE IF EXISTS environmental_data CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

-- ------------------------------------------------------------------------------
-- 1. locations Table
-- Stores geographic and topographic metadata for all monitored landslide zones
-- ------------------------------------------------------------------------------
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude NUMERIC(9, 6) NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    elevation NUMERIC(8, 2) NOT NULL, -- meters above sea level
    slope NUMERIC(5, 2) NOT NULL CHECK (slope >= 0.0 AND slope <= 90.0), -- degrees
    vegetation_index NUMERIC(4, 3) NOT NULL CHECK (vegetation_index >= -1.0 AND vegetation_index <= 1.0), -- NDVI (-1 to 1)
    risk_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (risk_score >= 0.0 AND risk_score <= 100.0),
    risk_level VARCHAR(20) NOT NULL DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for locations
CREATE INDEX idx_locations_state ON locations(state);
CREATE INDEX idx_locations_district ON locations(district);
CREATE INDEX idx_locations_risk_level ON locations(risk_level);
CREATE INDEX idx_locations_coords ON locations(latitude, longitude);

-- ------------------------------------------------------------------------------
-- 2. environmental_data Table
-- Telemetry and environmental sensor measurements recorded at monitored sites
-- ------------------------------------------------------------------------------
CREATE TABLE environmental_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    rainfall NUMERIC(6, 2) NOT NULL CHECK (rainfall >= 0.0), -- mm (recent 1-24h)
    rainfall_duration NUMERIC(5, 2) NOT NULL CHECK (rainfall_duration >= 0.0), -- hours
    soil_moisture NUMERIC(5, 2) NOT NULL CHECK (soil_moisture >= 0.0), -- % volumetric or saturation index
    temperature NUMERIC(5, 2) NOT NULL, -- Celsius
    humidity NUMERIC(5, 2) NOT NULL CHECK (humidity >= 0.0 AND humidity <= 100.0), -- %
    slope NUMERIC(5, 2) NOT NULL CHECK (slope >= 0.0 AND slope <= 90.0),
    elevation NUMERIC(8, 2) NOT NULL,
    vegetation_index NUMERIC(4, 3) NOT NULL CHECK (vegetation_index >= -1.0 AND vegetation_index <= 1.0),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for environmental_data
CREATE INDEX idx_env_location_id ON environmental_data(location_id);
CREATE INDEX idx_env_recorded_at ON environmental_data(recorded_at DESC);
CREATE INDEX idx_env_location_time ON environmental_data(location_id, recorded_at DESC);

-- ------------------------------------------------------------------------------
-- 3. risk_predictions Table
-- AI-generated landslide hazard inferences over time with contributing factors
-- ------------------------------------------------------------------------------
CREATE TABLE risk_predictions (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    risk_score NUMERIC(5, 2) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 100.0),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    confidence NUMERIC(4, 3) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    rainfall_impact NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (rainfall_impact >= 0.0),
    soil_moisture_impact NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (soil_moisture_impact >= 0.0),
    slope_impact NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (slope_impact >= 0.0),
    elevation_impact NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (elevation_impact >= 0.0),
    vegetation_impact NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (vegetation_impact >= 0.0),
    prediction_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for risk_predictions
CREATE INDEX idx_predictions_location_id ON risk_predictions(location_id);
CREATE INDEX idx_predictions_time ON risk_predictions(prediction_time DESC);
CREATE INDEX idx_predictions_risk_level ON risk_predictions(risk_level);
CREATE INDEX idx_predictions_location_time ON risk_predictions(location_id, prediction_time DESC);

-- ------------------------------------------------------------------------------
-- 4. landslide_events Table
-- Historical landslide occurrences with causes, rainfall amounts, and impact
-- ------------------------------------------------------------------------------
CREATE TABLE landslide_events (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude NUMERIC(9, 6) NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    cause VARCHAR(255) NOT NULL,
    rainfall_before_event NUMERIC(6, 2) DEFAULT 0.0 CHECK (rainfall_before_event >= 0.0), -- mm
    description TEXT,
    source VARCHAR(150),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for landslide_events
CREATE INDEX idx_events_location_id ON landslide_events(location_id);
CREATE INDEX idx_events_date ON landslide_events(event_date DESC);
CREATE INDEX idx_events_severity ON landslide_events(severity);
CREATE INDEX idx_events_coords ON landslide_events(latitude, longitude);

-- ------------------------------------------------------------------------------
-- 5. alerts Table
-- Warning notifications generated for authorities, responders, and citizens
-- ------------------------------------------------------------------------------
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    risk_prediction_id INTEGER REFERENCES risk_predictions(id) ON DELETE SET NULL,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('WARNING', 'CRITICAL', 'WEATHER', 'LANDSLIDE')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for alerts
CREATE INDEX idx_alerts_location_id ON alerts(location_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_active_created ON alerts(status, created_at DESC);
