-- ==============================================================================
-- AI-Based Landslide Risk Monitoring System
-- Demo Seed Data (Northeast India - 24 Locations)
-- ==============================================================================

-- Clear existing data
TRUNCATE TABLE alerts, landslide_events, risk_predictions, environmental_data, locations RESTART IDENTITY CASCADE;

-- ------------------------------------------------------------------------------
-- 1. Insert Locations
-- ------------------------------------------------------------------------------
INSERT INTO locations (id, name, state, district, latitude, longitude, elevation, slope, vegetation_index, risk_score, risk_level, created_at, updated_at) VALUES
-- Assam
(1, 'Haflong Hill Sector 4', 'Assam', 'Dima Hasao', 25.176400, 93.023400, 960.00, 38.50, 0.620, 84.50, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(2, 'Guwahati Kamakhya Hillside', 'Assam', 'Kamrup Metropolitan', 26.166200, 91.705800, 245.00, 28.00, 0.480, 52.00, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),
(3, 'Diphu Ridge Line', 'Assam', 'Karbi Anglong', 25.843600, 93.432600, 186.00, 22.50, 0.710, 31.20, 'LOW', NOW() - INTERVAL '30 days', NOW()),

-- Meghalaya
(4, 'Cherrapunji Sohra Cliff', 'Meghalaya', 'East Khasi Hills', 25.270200, 91.732300, 1430.00, 44.00, 0.540, 92.40, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(5, 'Shillong Peak Slopes', 'Meghalaya', 'East Khasi Hills', 25.534800, 91.853200, 1965.00, 34.00, 0.680, 68.30, 'HIGH', NOW() - INTERVAL '30 days', NOW()),
(6, 'Mawsynram Valley Escarpment', 'Meghalaya', 'East Khasi Hills', 25.297400, 91.582600, 1400.00, 42.00, 0.510, 88.00, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(7, 'Nongstoin Western Gradient', 'Meghalaya', 'West Khasi Hills', 25.522200, 91.268500, 1409.00, 24.00, 0.760, 28.50, 'LOW', NOW() - INTERVAL '30 days', NOW()),

-- Sikkim
(8, 'Gangtok Vajra Cinema Ridge', 'Sikkim', 'East Sikkim', 27.338900, 88.606500, 1650.00, 36.50, 0.590, 74.00, 'HIGH', NOW() - INTERVAL '30 days', NOW()),
(9, 'Mangan North Transit Corridor', 'Sikkim', 'Mangan', 27.505600, 88.528400, 1310.00, 41.00, 0.640, 86.80, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(10, 'Namchi Central Slope', 'Sikkim', 'South Sikkim', 27.166700, 88.350000, 1315.00, 26.00, 0.690, 45.00, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),
(11, 'Singtam Teesta Valley Margin', 'Sikkim', 'East Sikkim', 27.234600, 88.498400, 400.00, 31.00, 0.520, 62.10, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),

-- Arunachal Pradesh
(12, 'Tawang Pass Hill Track', 'Arunachal Pradesh', 'Tawang', 27.586100, 91.859400, 3048.00, 39.00, 0.420, 79.50, 'HIGH', NOW() - INTERVAL '30 days', NOW()),
(13, 'Itanagar Ganga Lake Rim', 'Arunachal Pradesh', 'Papum Pare', 27.084400, 93.605300, 750.00, 29.50, 0.730, 41.00, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),
(14, 'Bomdila West Kameng Crest', 'Arunachal Pradesh', 'West Kameng', 27.264500, 92.422800, 2217.00, 37.00, 0.610, 71.30, 'HIGH', NOW() - INTERVAL '30 days', NOW()),
(15, 'Ziro Pine Ridge Foothills', 'Arunachal Pradesh', 'Lower Subansiri', 27.545000, 93.829000, 1572.00, 18.00, 0.820, 22.00, 'LOW', NOW() - INTERVAL '30 days', NOW()),

-- Nagaland
(16, 'Kohima Bypass National Highway 29', 'Nagaland', 'Kohima', 25.675100, 94.108600, 1444.00, 43.00, 0.570, 91.20, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(17, 'Mokokchung Outer Ring', 'Nagaland', 'Mokokchung', 26.325600, 94.520000, 1325.00, 30.00, 0.650, 58.70, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),
(18, 'Wokha Doyang Catchment Bluff', 'Nagaland', 'Wokha', 26.098400, 94.261200, 1313.00, 33.00, 0.670, 64.00, 'MODERATE', NOW() - INTERVAL '30 days', NOW()),

-- Manipur
(19, 'Tamenglong Barak River Bank', 'Manipur', 'Tamenglong', 24.985600, 93.492500, 1260.00, 40.50, 0.660, 83.00, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(20, 'Senapati Hill Highway Segment', 'Manipur', 'Senapati', 25.267800, 94.016700, 1140.00, 32.00, 0.630, 66.50, 'HIGH', NOW() - INTERVAL '30 days', NOW()),
(21, 'Imphal Langol Reserve Border', 'Manipur', 'Imphal West', 24.817000, 93.936800, 785.00, 21.00, 0.750, 29.80, 'LOW', NOW() - INTERVAL '30 days', NOW()),

-- Mizoram
(22, 'Aizawl Bawngkawn Ridge', 'Mizoram', 'Aizawl', 23.753800, 92.737800, 1132.00, 45.00, 0.530, 94.00, 'CRITICAL', NOW() - INTERVAL '30 days', NOW()),
(23, 'Lunglei Chanmari Slope', 'Mizoram', 'Lunglei', 22.887200, 92.748300, 1222.00, 35.00, 0.620, 70.50, 'HIGH', NOW() - INTERVAL '30 days', NOW()),

-- Tripura
(24, 'Jampui Hills Orange Valley', 'Tripura', 'North Tripura', 23.820000, 92.270000, 930.00, 25.00, 0.790, 27.50, 'LOW', NOW() - INTERVAL '30 days', NOW());

SELECT setval('locations_id_seq', 24, true);

-- ------------------------------------------------------------------------------
-- 2. Insert Environmental Data (Sensor readings)
-- ------------------------------------------------------------------------------
INSERT INTO environmental_data (location_id, rainfall, rainfall_duration, soil_moisture, temperature, humidity, slope, elevation, vegetation_index, recorded_at) VALUES
-- Location 1 (Haflong Hill - Critical)
(1, 142.50, 18.00, 89.20, 21.50, 96.00, 38.50, 960.00, 0.620, NOW()),
(1, 110.00, 12.00, 81.00, 22.00, 93.00, 38.50, 960.00, 0.620, NOW() - INTERVAL '6 hours'),
(1, 75.20, 8.00, 72.40, 23.00, 88.00, 38.50, 960.00, 0.620, NOW() - INTERVAL '12 hours'),
(1, 35.00, 4.00, 60.00, 24.50, 80.00, 38.50, 960.00, 0.620, NOW() - INTERVAL '24 hours'),

-- Location 2 (Guwahati Kamakhya - Moderate)
(2, 45.00, 5.00, 56.00, 28.00, 82.00, 28.00, 245.00, 0.480, NOW()),
(2, 30.00, 3.00, 50.00, 29.00, 79.00, 28.00, 245.00, 0.480, NOW() - INTERVAL '12 hours'),

-- Location 3 (Diphu - Low)
(3, 12.00, 1.50, 35.00, 27.50, 68.00, 22.50, 186.00, 0.710, NOW()),

-- Location 4 (Cherrapunji - Critical)
(4, 210.00, 24.00, 94.50, 18.20, 99.00, 44.00, 1430.00, 0.540, NOW()),
(4, 180.00, 20.00, 91.00, 18.50, 98.00, 44.00, 1430.00, 0.540, NOW() - INTERVAL '6 hours'),
(4, 130.00, 14.00, 84.00, 19.00, 95.00, 44.00, 1430.00, 0.540, NOW() - INTERVAL '18 hours'),

-- Location 5 (Shillong Peak - High)
(5, 78.00, 9.00, 71.00, 16.00, 90.00, 34.00, 1965.00, 0.680, NOW()),
(5, 62.00, 7.00, 65.00, 17.00, 86.00, 34.00, 1965.00, 0.680, NOW() - INTERVAL '12 hours'),

-- Location 6 (Mawsynram - Critical)
(6, 195.00, 22.00, 92.00, 18.00, 98.00, 42.00, 1400.00, 0.510, NOW()),

-- Location 8 (Gangtok Vajra - High)
(8, 88.00, 11.00, 76.50, 15.00, 91.00, 36.50, 1650.00, 0.590, NOW()),

-- Location 9 (Mangan - Critical)
(9, 155.00, 19.00, 88.50, 14.20, 97.00, 41.00, 1310.00, 0.640, NOW()),

-- Location 12 (Tawang - High)
(12, 65.00, 8.00, 73.00, 9.00, 89.00, 39.00, 3048.00, 0.420, NOW()),

-- Location 16 (Kohima NH-29 - Critical)
(16, 165.00, 20.00, 93.00, 19.00, 97.00, 43.00, 1444.00, 0.570, NOW()),
(16, 120.00, 14.00, 86.00, 20.00, 94.00, 43.00, 1444.00, 0.570, NOW() - INTERVAL '8 hours'),

-- Location 19 (Tamenglong - Critical)
(19, 135.00, 16.00, 87.00, 22.00, 94.00, 40.50, 1260.00, 0.660, NOW()),

-- Location 22 (Aizawl Bawngkawn - Critical)
(22, 175.00, 21.00, 95.00, 21.00, 98.00, 45.00, 1132.00, 0.530, NOW()),
(22, 130.00, 15.00, 88.00, 22.00, 95.00, 45.00, 1132.00, 0.530, NOW() - INTERVAL '10 hours');

-- ------------------------------------------------------------------------------
-- 3. Insert Risk Predictions
-- ------------------------------------------------------------------------------
INSERT INTO risk_predictions (location_id, risk_score, risk_level, confidence, rainfall_impact, soil_moisture_impact, slope_impact, elevation_impact, vegetation_impact, prediction_time) VALUES
-- Haflong
(1, 84.50, 'CRITICAL', 0.920, 35.00, 28.00, 16.50, 3.00, 2.00, NOW()),
(1, 76.00, 'HIGH', 0.880, 29.00, 24.50, 16.50, 3.00, 3.00, NOW() - INTERVAL '6 hours'),
(1, 65.00, 'MODERATE', 0.850, 21.00, 20.50, 16.50, 3.00, 4.00, NOW() - INTERVAL '12 hours'),

-- Cherrapunji
(4, 92.40, 'CRITICAL', 0.950, 42.00, 29.50, 17.50, 2.00, 1.40, NOW()),
(4, 85.00, 'CRITICAL', 0.930, 36.00, 27.50, 17.50, 2.00, 2.00, NOW() - INTERVAL '8 hours'),

-- Shillong
(5, 68.30, 'HIGH', 0.870, 26.00, 22.00, 14.30, 3.50, 2.50, NOW()),

-- Mawsynram
(6, 88.00, 'CRITICAL', 0.940, 39.00, 28.00, 16.80, 2.20, 2.00, NOW()),

-- Gangtok
(8, 74.00, 'HIGH', 0.890, 28.00, 23.50, 15.20, 4.30, 3.00, NOW()),

-- Mangan
(9, 86.80, 'CRITICAL', 0.930, 37.00, 27.00, 17.00, 3.20, 2.60, NOW()),

-- Kohima
(16, 91.20, 'CRITICAL', 0.940, 40.0, 28.80, 17.20, 3.20, 2.00, NOW()),

-- Tamenglong
(19, 83.00, 'CRITICAL', 0.910, 34.00, 26.50, 16.40, 3.10, 3.00, NOW()),

-- Aizawl
(22, 94.00, 'CRITICAL', 0.960, 43.00, 30.00, 17.80, 2.20, 1.00, NOW()),

-- Others
(2, 52.00, 'MODERATE', 0.820, 18.00, 17.00, 11.20, 2.80, 3.00, NOW()),
(3, 31.20, 'LOW', 0.850, 8.00, 10.00, 8.20, 1.50, 3.50, NOW()),
(10, 45.00, 'MODERATE', 0.800, 14.00, 15.00, 10.50, 2.50, 3.00, NOW()),
(12, 79.50, 'HIGH', 0.900, 30.00, 25.00, 16.00, 5.00, 3.50, NOW()),
(21, 29.80, 'LOW', 0.860, 7.00, 9.00, 7.50, 2.30, 4.00, NOW()),
(24, 27.50, 'LOW', 0.840, 6.00, 8.50, 7.20, 1.80, 4.00, NOW());

-- ------------------------------------------------------------------------------
-- 4. Insert Landslide Events (Historical Records)
-- ------------------------------------------------------------------------------
INSERT INTO landslide_events (location_id, event_date, latitude, longitude, severity, cause, rainfall_before_event, description, source, created_at) VALUES
(1, '2024-05-28 04:30:00+05:30', 25.176400, 93.023400, 'CRITICAL', 'Heavy Monsoon Inundation & Slope Over-saturation', 185.40, 'Massive mudslide along Haflong railway junction track severing south Assam train connections.', 'Assam State Disaster Management Authority (ASDMA)', NOW()),
(4, '2023-06-17 14:15:00+05:30', 25.270200, 91.732300, 'CRITICAL', 'Extreme Flash Rainfall & Cliff Instability', 312.00, 'Debris flow near Sohra-Shella highway leading to rockslides blocking border logistics.', 'Meghalaya SDMA & GSI', NOW()),
(9, '2023-10-04 02:00:00+05:30', 27.505600, 88.528400, 'CRITICAL', 'Glacial Lake Outburst & Severe River Bank Erosion', 140.00, 'Flash flood surge along Teesta river causing slope toes collapse across Mangan highway stretch.', 'Sikkim Disaster Management Authority', NOW()),
(16, '2024-07-12 18:45:00+05:30', 25.675100, 94.108600, 'HIGH', 'Continuous Precipitation & Hill Cutting', 124.60, 'Substantial soil slippage along National Highway 29 halting interstate trucking corridor.', 'Nagaland NSDMA Report', NOW()),
(22, '2024-05-29 06:10:00+05:30', 23.753800, 92.737800, 'CRITICAL', 'Cyclone Remal Remnant Downpour', 210.50, 'Severe rockfall and landslide at multiple quarry and hillside zones around Aizawl town periphery.', 'Mizoram Disaster Management', NOW()),
(5, '2022-08-19 11:20:00+05:30', 25.534800, 91.853200, 'MODERATE', 'Prolonged Seepage on Steep Cut Slope', 82.00, 'Minor earth slide along upper Shillong arterial bypass causing traffic detour.', 'PWD Meghalaya', NOW()),
(8, '2023-07-02 09:00:00+05:30', 27.338900, 88.606500, 'HIGH', 'Toe Erosion and Saturated Debris', 115.00, 'Slope failure near Burtuk area blocking North Sikkim highway access.', 'BRO Swastik', NOW()),
(19, '2022-07-08 07:45:00+05:30', 24.985600, 93.492500, 'CRITICAL', 'Non-stop Torrents and Saturated Shale Formations', 160.00, 'Widespread hillside subsidence cutting off remote Tamenglong villages.', 'Manipur SDRF', NOW());

-- ------------------------------------------------------------------------------
-- 5. Insert Alerts
-- ------------------------------------------------------------------------------
INSERT INTO alerts (location_id, risk_prediction_id, alert_type, severity, message, status, created_at, resolved_at) VALUES
-- Active Alerts
(22, 9, 'CRITICAL', 'CRITICAL', 'EVACUATION WARNING: Extreme landslide hazard detected at Aizawl Bawngkawn Ridge (Risk: 94%). Soil moisture exceeds 95%.', 'ACTIVE', NOW() - INTERVAL '45 minutes', NULL),
(4, 2, 'CRITICAL', 'CRITICAL', 'RED ALERT: Extreme precipitation (>210mm) and high cliff instability at Cherrapunji Sohra Cliff. High risk of rockfalls.', 'ACTIVE', NOW() - INTERVAL '2 hours', NULL),
(16, 7, 'LANDSLIDE', 'CRITICAL', 'ROAD CLOSURE ALERT: Impending slope failure detected along NH-29 Kohima Bypass corridor. Traffic diverted.', 'ACTIVE', NOW() - INTERVAL '3 hours', NULL),
(1, 1, 'WARNING', 'HIGH', 'HIGH HAZARD: Haflong Hill Sector 4 risk score elevated to 84.5%. Continuous heavy rain forecast for next 12 hours.', 'ACTIVE', NOW() - INTERVAL '4 hours', NULL),
(9, 6, 'CRITICAL', 'CRITICAL', 'TEESTA BASIN ADVISORY: Mangan North Transit corridor shows critical ground deformation and high saturation.', 'ACTIVE', NOW() - INTERVAL '5 hours', NULL),
(8, 5, 'WEATHER', 'HIGH', 'WEATHER ALERT: Sustained heavy monsoon downpour approaching Gangtok Vajra ridge. Monitoring sensors online.', 'ACTIVE', NOW() - INTERVAL '6 hours', NULL),

-- Resolved Alerts
(5, 3, 'WARNING', 'MODERATE', 'Precautionary advisory for Shillong Peak road segment due to moderate earth slippage.', 'RESOLVED', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day'),
(2, 10, 'WEATHER', 'LOW', 'Continuous shower alert for Guwahati Kamakhya foothill area.', 'RESOLVED', NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days'),
(12, 11, 'WARNING', 'MODERATE', 'Slope freeze-thaw warning for Tawang pass transit sector.', 'RESOLVED', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days');
