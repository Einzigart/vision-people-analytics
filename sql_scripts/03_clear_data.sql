-- Clear Detection Data Scripts
-- Use these scripts to clear existing data before generating new data
-- ⚠️ WARNING: These operations cannot be undone! ⚠️

-- ========================================
-- SHOW CURRENT DATA BEFORE CLEARING
-- ========================================
SELECT
    'CURRENT DATA SUMMARY (Before Clearing)' AS info,
    COUNT(*) AS total_records,
    MIN(timestamp) AS earliest_record,
    MAX(timestamp) AS latest_record,
    COUNT(DISTINCT DATE(timestamp)) AS days_with_data,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people_detected
FROM api_detectiondata;

-- ========================================
-- CLEARING OPTIONS (Uncomment the one you want)
-- ========================================

-- 🚨 1. CLEAR ALL DETECTION DATA (DANGER!)
-- This will delete EVERYTHING - use only if you want to start completely fresh
-- DELETE FROM api_detectiondata;
-- DELETE FROM api_dailyaggregation;
-- DELETE FROM api_monthlyaggregation;

-- 📅 2. Clear only today's data
-- DELETE FROM api_detectiondata WHERE DATE(timestamp) = CURRENT_DATE;

-- 📅 3. Clear yesterday's data
-- DELETE FROM api_detectiondata WHERE DATE(timestamp) = CURRENT_DATE - INTERVAL '1 day';

-- 📅 4. Clear last 7 days of data
-- DELETE FROM api_detectiondata WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';

-- 📅 5. Clear last 30 days of data
-- DELETE FROM api_detectiondata WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days';

-- 📅 6. Clear this week's data (Monday to Sunday)
-- DELETE FROM api_detectiondata
-- WHERE timestamp >= DATE_TRUNC('week', CURRENT_DATE)
-- AND timestamp < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '7 days';

-- 📅 7. Clear this month's data
-- DELETE FROM api_detectiondata
-- WHERE timestamp >= DATE_TRUNC('month', CURRENT_DATE)
-- AND timestamp < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month';

-- 📅 8. Clear specific date range (CUSTOMIZE DATES BELOW)
-- DELETE FROM api_detectiondata
-- WHERE timestamp >= '2025-07-20 00:00:00'::timestamp
-- AND timestamp <= '2025-07-22 23:59:59'::timestamp;

-- 📅 9. Clear data older than X days (e.g., older than 90 days)
-- DELETE FROM api_detectiondata WHERE timestamp < CURRENT_DATE - INTERVAL '90 days';

-- 📅 10. Clear data for specific hours (e.g., night hours for testing)
-- DELETE FROM api_detectiondata
-- WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 22 AND 23
-- OR EXTRACT(HOUR FROM timestamp) BETWEEN 0 AND 5;

-- ========================================
-- CLEAR AGGREGATED DATA (Optional)
-- ========================================

-- Clear daily aggregations for specific date range
-- DELETE FROM api_dailyaggregation
-- WHERE date >= '2025-07-20' AND date <= '2025-07-22';

-- Clear monthly aggregations for specific months
-- DELETE FROM api_monthlyaggregation
-- WHERE (year = 2025 AND month >= 7) OR year > 2025;

-- Clear all aggregations (if you want to regenerate them)
-- DELETE FROM api_dailyaggregation;
-- DELETE FROM api_monthlyaggregation;

-- ========================================
-- SHOW DATA SUMMARY AFTER CLEARING
-- ========================================
SELECT
    'DATA SUMMARY (After Clearing)' AS info,
    COUNT(*) AS total_records,
    MIN(timestamp) AS earliest_record,
    MAX(timestamp) AS latest_record,
    COUNT(DISTINCT DATE(timestamp)) AS days_with_data,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people_detected
FROM api_detectiondata;

-- Show records by date after clearing
SELECT
    DATE(timestamp) AS date,
    COUNT(*) AS records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC
LIMIT 10;
