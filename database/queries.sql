-- ==============================================================================
-- AI-Based Landslide Risk Monitoring System
-- Optimized Database Queries
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. All Monitored Locations with Risk Scores and Coordinates
-- Used for Map Views and Locations Tables
-- ------------------------------------------------------------------------------
SELECT 
    l.id,
    l.name,
    l.state,
    l.district,
    l.latitude,
    l.longitude,
    l.elevation,
    l.slope,
    l.vegetation_index,
    l.risk_score,
    l.risk_level,
    l.updated_at
FROM locations l
ORDER BY l.risk_score DESC;

-- ------------------------------------------------------------------------------
-- 2. High and Critical Risk Locations (Hazard Hotspots)
-- ------------------------------------------------------------------------------
SELECT 
    l.id,
    l.name,
    l.state,
    l.district,
    l.latitude,
    l.longitude,
    l.risk_score,
    l.risk_level
FROM locations l
WHERE l.risk_level IN ('HIGH', 'CRITICAL')
ORDER BY l.risk_score DESC;

-- ------------------------------------------------------------------------------
-- 3. Critical Risk Hotspots Only
-- ------------------------------------------------------------------------------
SELECT 
    l.id,
    l.name,
    l.state,
    l.district,
    l.latitude,
    l.longitude,
    l.risk_score,
    l.risk_level
FROM locations l
WHERE l.risk_level = 'CRITICAL'
ORDER BY l.risk_score DESC;

-- ------------------------------------------------------------------------------
-- 4. Active Alerts with Associated Location Metadata
-- Used for Alert Banner and Real-time Hazard Feed
-- ------------------------------------------------------------------------------
SELECT 
    a.id,
    a.location_id,
    l.name AS location_name,
    l.state,
    l.district,
    a.alert_type,
    a.severity,
    a.message,
    a.status,
    a.created_at
FROM alerts a
JOIN locations l ON a.location_id = l.id
WHERE a.status = 'ACTIVE'
ORDER BY 
    CASE a.severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MODERATE' THEN 3
        ELSE 4
    END,
    a.created_at DESC;

-- ------------------------------------------------------------------------------
-- 5. Latest Environmental Sensor Telemetry per Location
-- ------------------------------------------------------------------------------
SELECT DISTINCT ON (e.location_id)
    e.id,
    e.location_id,
    l.name AS location_name,
    e.rainfall,
    e.rainfall_duration,
    e.soil_moisture,
    e.temperature,
    e.humidity,
    e.slope,
    e.elevation,
    e.vegetation_index,
    e.recorded_at
FROM environmental_data e
JOIN locations l ON e.location_id = l.id
ORDER BY e.location_id, e.recorded_at DESC;

-- ------------------------------------------------------------------------------
-- 6. Latest Risk Prediction per Location
-- ------------------------------------------------------------------------------
SELECT DISTINCT ON (p.location_id)
    p.id,
    p.location_id,
    l.name AS location_name,
    p.risk_score,
    p.risk_level,
    p.confidence,
    p.rainfall_impact,
    p.soil_moisture_impact,
    p.slope_impact,
    p.elevation_impact,
    p.vegetation_impact,
    p.prediction_time
FROM risk_predictions p
JOIN locations l ON p.location_id = l.id
ORDER BY p.location_id, p.prediction_time DESC;

-- ------------------------------------------------------------------------------
-- 7. Risk History for a Given Location (e.g., location_id = 1)
-- Used for Frontend Time-Series Line Charts
-- ------------------------------------------------------------------------------
SELECT 
    p.id,
    p.location_id,
    p.risk_score,
    p.risk_level,
    p.confidence,
    p.rainfall_impact,
    p.soil_moisture_impact,
    p.slope_impact,
    p.prediction_time
FROM risk_predictions p
WHERE p.location_id = 1
ORDER BY p.prediction_time DESC
LIMIT 50;

-- ------------------------------------------------------------------------------
-- 8. Historical Landslide Events with Geo-Coordinates
-- ------------------------------------------------------------------------------
SELECT 
    e.id,
    e.location_id,
    l.name AS location_name,
    l.state,
    e.event_date,
    e.latitude,
    e.longitude,
    e.severity,
    e.cause,
    e.rainfall_before_event,
    e.description,
    e.source
FROM landslide_events e
LEFT JOIN locations l ON e.location_id = l.id
ORDER BY e.event_date DESC;

-- ------------------------------------------------------------------------------
-- 9. State-Wise Risk Summary
-- Aggregates count of monitored zones and average risk per state
-- ------------------------------------------------------------------------------
SELECT 
    l.state,
    COUNT(l.id) AS total_locations,
    ROUND(AVG(l.risk_score), 2) AS average_risk_score,
    COUNT(CASE WHEN l.risk_level = 'CRITICAL' THEN 1 END) AS critical_count,
    COUNT(CASE WHEN l.risk_level = 'HIGH' THEN 1 END) AS high_count,
    COUNT(CASE WHEN l.risk_level = 'MODERATE' THEN 1 END) AS moderate_count,
    COUNT(CASE WHEN l.risk_level = 'LOW' THEN 1 END) AS low_count
FROM locations l
GROUP BY l.state
ORDER BY average_risk_score DESC;

-- ------------------------------------------------------------------------------
-- 10. System Risk Distribution
-- Percentage and count breakdown across risk categories
-- ------------------------------------------------------------------------------
SELECT 
    risk_level,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM locations), 2) AS percentage
FROM locations
GROUP BY risk_level
ORDER BY 
    CASE risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MODERATE' THEN 3
        ELSE 4
    END;

-- ------------------------------------------------------------------------------
-- 11. Dashboard Analytics Summary KPI Stats
-- Comprehensive single-query KPI overview
-- ------------------------------------------------------------------------------
SELECT 
    (SELECT COUNT(*) FROM locations) AS total_monitored_locations,
    (SELECT COUNT(*) FROM locations WHERE risk_level = 'LOW') AS low_risk_count,
    (SELECT COUNT(*) FROM locations WHERE risk_level = 'MODERATE') AS moderate_risk_count,
    (SELECT COUNT(*) FROM locations WHERE risk_level = 'HIGH') AS high_risk_count,
    (SELECT COUNT(*) FROM locations WHERE risk_level = 'CRITICAL') AS critical_risk_count,
    (SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE') AS active_alerts_count,
    (SELECT COUNT(*) FROM landslide_events) AS total_historical_events,
    (SELECT ROUND(AVG(risk_score), 2) FROM locations) AS average_system_risk;
