/* Flexible Date Range Dummy Data Generator - FIXED VERSION */
/* Customize the dates below and run this script */

/* ======================================== */
/* STEP 1: CUSTOMIZE THESE DATES           */
/* ======================================== */

/* Change these dates to your desired range: */
/* start_date: '2024-07-23' (YYYY-MM-DD format) - 1 YEAR AGO */
/* end_date: '2025-07-23' (YYYY-MM-DD format) - TODAY */
/* interval_minutes: 60 (60 minutes for 1 year - better performance) */

/* ======================================== */
/* STEP 2: CLEAR EXISTING DATA (OPTIONAL)  */
/* ======================================== */

/* Uncomment the line below to clear existing data in your date range */
/* DELETE FROM api_detectiondata WHERE timestamp >= '2024-07-23 00:00:00' AND timestamp <= '2025-07-23 23:59:59'; */

/* ======================================== */
/* STEP 3: GENERATE DATA                    */
/* ======================================== */

INSERT INTO api_detectiondata (
    timestamp,
    male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
    female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
    is_aggregated
)
SELECT 
    /* Generate timestamps for your date range */
    (DATE '2024-07-23' + day_offset) + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval AS timestamp,
    
    /* Male age groups with realistic patterns */
    CASE 
        /* Weekend patterns (Saturday = 6, Sunday = 0) */
        WHEN EXTRACT(DOW FROM DATE '2024-07-23' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        /* Weekday patterns */
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.08 AS male_0_9,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2024-07-23' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.12 AS male_10_19,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2024-07-23' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.25 AS male_20_29,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.22 AS male_30_39,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.18 AS male_40_49,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.15 AS male_50_plus,
    
    /* Female demographics (same patterns) */
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.08 AS female_0_9,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.12 AS female_10_19,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.25 AS female_20_29,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.22 AS female_30_39,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.18 AS female_40_49,
    
    CASE 
        WHEN EXTRACT(DOW FROM DATE '2025-07-16' + day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
                    FLOOR(random() * 12 + 6)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 8 + 4)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 2)::int
            END
    END * 0.15 AS female_50_plus,
    
    false AS is_aggregated
FROM 
    generate_series(0, 365) AS day_offset,  /* 365 days for 1 year */
    generate_series(0, 23) AS hour_num,
    generate_series(0, 0, 60) AS minute_num  /* Every 60 minutes (hourly) for performance */
WHERE 
    /* Don't generate future data */
    (DATE '2024-07-23' + day_offset) + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval <= NOW()
    /* Change the date range above to match your start_date */
    AND (DATE '2024-07-23' + day_offset) <= DATE '2025-07-23';  /* 1 year range */

/* ======================================== */
/* STEP 4: VIEW RESULTS                     */
/* ======================================== */

/* Show summary of generated data */
SELECT
    'GENERATION SUMMARY' AS info,
    COUNT(*) AS total_records,
    MIN(timestamp) AS earliest_record,
    MAX(timestamp) AS latest_record,
    COUNT(DISTINCT DATE(timestamp)) AS days_with_data,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total_males,
    SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_females,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata
WHERE timestamp >= '2024-07-23 00:00:00' AND timestamp <= '2025-07-23 23:59:59';

/* Show daily breakdown */
SELECT
    DATE(timestamp) AS date,
    CASE EXTRACT(DOW FROM timestamp)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    COUNT(*) AS records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata
WHERE timestamp >= '2024-07-23 00:00:00' AND timestamp <= '2025-07-23 23:59:59'
GROUP BY DATE(timestamp), EXTRACT(DOW FROM timestamp)
ORDER BY DATE(timestamp);
