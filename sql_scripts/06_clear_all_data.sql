-- 🚨 CLEAR ALL DATA - COMPLETE DATABASE RESET
-- ⚠️ WARNING: This will delete ALL detection data and aggregations! ⚠️
-- ⚠️ This action CANNOT be undone! ⚠️

-- ========================================
-- SHOW CURRENT DATA BEFORE CLEARING
-- ========================================
SELECT 
    '🔍 CURRENT DATABASE STATE (Before Clearing)' AS info,
    (SELECT COUNT(*) FROM api_detectiondata) AS detection_records,
    (SELECT COUNT(*) FROM api_dailyaggregation) AS daily_aggregations,
    (SELECT COUNT(*) FROM api_monthlyaggregation) AS monthly_aggregations,
    (SELECT MIN(timestamp) FROM api_detectiondata) AS earliest_detection,
    (SELECT MAX(timestamp) FROM api_detectiondata) AS latest_detection,
    (SELECT SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
                female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) 
     FROM api_detectiondata) AS total_people_detected;

-- Show data distribution by date
SELECT 
    '📅 Data by Date' AS info,
    DATE(timestamp) AS date,
    COUNT(*) AS records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS people
FROM api_detectiondata 
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC
LIMIT 10;

-- ========================================
-- 🚨 DANGER ZONE - UNCOMMENT TO EXECUTE
-- ========================================

-- Step 1: Clear all detection data (raw records)
-- DELETE FROM api_detectiondata;

-- Step 2: Clear all daily aggregations
-- DELETE FROM api_dailyaggregation;

-- Step 3: Clear all monthly aggregations  
-- DELETE FROM api_monthlyaggregation;

-- Step 4: Reset auto-increment sequences (optional)
-- ALTER SEQUENCE api_detectiondata_id_seq RESTART WITH 1;
-- ALTER SEQUENCE api_dailyaggregation_id_seq RESTART WITH 1;
-- ALTER SEQUENCE api_monthlyaggregation_id_seq RESTART WITH 1;

-- ========================================
-- ALTERNATIVE: SAFER CLEARING OPTIONS
-- ========================================

-- Option A: Clear only detection data (keep aggregations)
-- DELETE FROM api_detectiondata;

-- Option B: Clear data older than 30 days
-- DELETE FROM api_detectiondata WHERE timestamp < CURRENT_DATE - INTERVAL '30 days';
-- DELETE FROM api_dailyaggregation WHERE date < CURRENT_DATE - INTERVAL '30 days';

-- Option C: Clear data for specific year
-- DELETE FROM api_detectiondata WHERE EXTRACT(YEAR FROM timestamp) = 2024;
-- DELETE FROM api_dailyaggregation WHERE EXTRACT(YEAR FROM date) = 2024;
-- DELETE FROM api_monthlyaggregation WHERE year = 2024;

-- Option D: Clear test data (if you have a pattern)
-- DELETE FROM api_detectiondata WHERE timestamp >= '2025-07-20 00:00:00';

-- ========================================
-- VERIFY CLEARING RESULTS
-- ========================================
SELECT 
    '✅ DATABASE STATE (After Clearing)' AS info,
    (SELECT COUNT(*) FROM api_detectiondata) AS detection_records,
    (SELECT COUNT(*) FROM api_dailyaggregation) AS daily_aggregations,
    (SELECT COUNT(*) FROM api_monthlyaggregation) AS monthly_aggregations,
    (SELECT MIN(timestamp) FROM api_detectiondata) AS earliest_detection,
    (SELECT MAX(timestamp) FROM api_detectiondata) AS latest_detection,
    (SELECT SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
                female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) 
     FROM api_detectiondata) AS total_people_detected;

-- Show remaining data (if any)
SELECT 
    '📊 Remaining Data Summary' AS info,
    DATE(timestamp) AS date,
    COUNT(*) AS records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS people
FROM api_detectiondata 
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC
LIMIT 10;

-- ========================================
-- 🎯 NEXT STEPS AFTER CLEARING
-- ========================================

/*
After clearing the data, you can:

1. 🚀 Generate quick test data:
   - Run: 04_quick_test_data.sql

2. 📅 Generate today's data:
   - Run: 01_generate_today_data.sql

3. 📊 Generate week's data:
   - Run: 02_generate_week_data.sql

4. 🎯 Generate custom date range:
   - Run: 05_flexible_date_range_generator.sql
   - Customize the start_date and end_date variables

5. ⚙️ Create model settings (if needed):
   INSERT INTO api_modelsettings (id, confidence_threshold_person, confidence_threshold_face, log_interval_seconds, last_updated)
   VALUES (1, 0.5, 0.5, 60, NOW())
   ON CONFLICT (id) DO NOTHING;

6. 👤 Create admin user (if needed):
   - This should be done through Django admin or management commands
*/
