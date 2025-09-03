/* Check Aggregation Status - Diagnostic Script */
/* Run this to see the current state of your data and aggregation */

/* ======================================== */
/* STEP 1: CHECK DETECTION DATA STATUS     */
/* ======================================== */

SELECT 
    '📊 DETECTION DATA STATUS' AS info,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE is_aggregated = false) AS unaggregated_records,
    COUNT(*) FILTER (WHERE is_aggregated = true) AS aggregated_records,
    MIN(timestamp) AS earliest_record,
    MAX(timestamp) AS latest_record,
    COUNT(DISTINCT DATE(timestamp)) AS days_with_data
FROM api_detectiondata;

/* ======================================== */
/* STEP 2: CHECK AGGREGATION TABLES        */
/* ======================================== */

SELECT 
    '📈 AGGREGATION TABLES STATUS' AS info,
    (SELECT COUNT(*) FROM api_dailyaggregation) AS daily_aggregations,
    (SELECT COUNT(*) FROM api_monthlyaggregation) AS monthly_aggregations,
    (SELECT MIN(date) FROM api_dailyaggregation) AS earliest_daily_agg,
    (SELECT MAX(date) FROM api_dailyaggregation) AS latest_daily_agg,
    (SELECT MIN(year || '-' || LPAD(month::text, 2, '0')) FROM api_monthlyaggregation) AS earliest_monthly_agg,
    (SELECT MAX(year || '-' || LPAD(month::text, 2, '0')) FROM api_monthlyaggregation) AS latest_monthly_agg;

/* ======================================== */
/* STEP 3: SAMPLE DATA CHECK               */
/* ======================================== */

/* Show recent detection data */
SELECT 
    '🔍 RECENT DETECTION DATA (Last 5 records)' AS info,
    timestamp,
    (male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total_males,
    (female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_females,
    is_aggregated
FROM api_detectiondata 
ORDER BY timestamp DESC 
LIMIT 5;

/* Show recent daily aggregations */
SELECT 
    '📅 RECENT DAILY AGGREGATIONS (Last 5 records)' AS info,
    date,
    male_count,
    female_count,
    total_count
FROM api_dailyaggregation 
ORDER BY date DESC 
LIMIT 5;

/* Show recent monthly aggregations */
SELECT 
    '📆 RECENT MONTHLY AGGREGATIONS (Last 5 records)' AS info,
    year,
    month,
    male_count,
    female_count,
    total_count
FROM api_monthlyaggregation 
ORDER BY year DESC, month DESC 
LIMIT 5;

/* ======================================== */
/* STEP 4: DATA CONSISTENCY CHECK          */
/* ======================================== */

/* Check if daily aggregations match detection data for a specific date */
WITH daily_check AS (
    SELECT 
        DATE(timestamp) AS date,
        SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS detection_males,
        SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS detection_females
    FROM api_detectiondata 
    WHERE is_aggregated = true
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    LIMIT 3
),
agg_check AS (
    SELECT 
        date,
        male_count AS agg_males,
        female_count AS agg_females
    FROM api_dailyaggregation
    ORDER BY date DESC
    LIMIT 3
)
SELECT 
    '🔍 DATA CONSISTENCY CHECK (Last 3 days)' AS info,
    COALESCE(dc.date, ac.date) AS date,
    dc.detection_males,
    ac.agg_males,
    dc.detection_females,
    ac.agg_females,
    CASE 
        WHEN dc.detection_males = ac.agg_males AND dc.detection_females = ac.agg_females THEN '✅ Match'
        WHEN dc.date IS NULL THEN '⚠️ No detection data'
        WHEN ac.date IS NULL THEN '⚠️ No aggregation data'
        ELSE '❌ Mismatch'
    END AS status
FROM daily_check dc
FULL OUTER JOIN agg_check ac ON dc.date = ac.date
ORDER BY COALESCE(dc.date, ac.date) DESC;

/* ======================================== */
/* STEP 5: TROUBLESHOOTING INFO            */
/* ======================================== */

/* Show dates with unaggregated data */
SELECT 
    '⚠️ DATES WITH UNAGGREGATED DATA' AS info,
    DATE(timestamp) AS date,
    COUNT(*) AS unaggregated_records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata 
WHERE is_aggregated = false
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 10;

/* ======================================== */
/* STEP 6: NEXT STEPS                      */
/* ======================================== */

/*
🎯 INTERPRETATION GUIDE:

✅ GOOD SIGNS:
- unaggregated_records = 0 (all data is aggregated)
- daily_aggregations > 0 (aggregations exist)
- Data consistency check shows "✅ Match"

⚠️ ISSUES TO FIX:
- unaggregated_records > 0: Run aggregation
- daily_aggregations = 0: No aggregations created
- Data consistency shows "❌ Mismatch": Aggregation logic issue

🔧 HOW TO FIX:
1. If you have unaggregated data, trigger aggregation via:
   - Web interface: Settings page → "Run Aggregation" button
   - API: POST to /api/trigger-aggregation/
   - Command line: python manage.py run_aggregation

2. If aggregation fails, check Django logs for errors

3. If data doesn't match, the aggregation logic may need fixing
*/
