/* Generate 1 Year of Dummy Data - Ready to Run */
/* This script generates 1 full year of realistic detection data */
/* From July 23, 2024 to July 23, 2025 (365 days) */
/* Hourly intervals for better performance */

/* ======================================== */
/* STEP 1: CLEAR EXISTING DATA (OPTIONAL)  */
/* ======================================== */

/* Uncomment the line below to clear existing data first */
/* DELETE FROM api_detectiondata WHERE timestamp >= '2024-07-23 00:00:00' AND timestamp <= '2025-07-23 23:59:59'; */

/* ======================================== */
/* STEP 2: GENERATE 1 YEAR OF DATA         */
/* ======================================== */

INSERT INTO api_detectiondata (
    timestamp,
    male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
    female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
    is_aggregated
)
SELECT 
    /* Generate timestamps for 1 year, hourly */
    (DATE '2024-07-23' + day_offset) + (hour_num || ' hours')::interval AS timestamp,
    
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
    END * 0.22 AS male_30_39,
    
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
    END * 0.18 AS male_40_49,
    
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
    END * 0.15 AS male_50_plus,
    
    /* Female demographics (same patterns) */
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
    END * 0.08 AS female_0_9,
    
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
    END * 0.12 AS female_10_19,
    
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
    END * 0.25 AS female_20_29,
    
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
    END * 0.22 AS female_30_39,
    
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
    END * 0.18 AS female_40_49,
    
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
    END * 0.15 AS female_50_plus,
    
    false AS is_aggregated
FROM 
    generate_series(0, 365) AS day_offset,  /* 365 days = 1 year */
    generate_series(0, 23) AS hour_num      /* Every hour (24 records per day) */
WHERE 
    /* Don't generate future data */
    (DATE '2024-07-23' + day_offset) + (hour_num || ' hours')::interval <= NOW()
    /* 1 year range */
    AND (DATE '2024-07-23' + day_offset) <= DATE '2025-07-23';

/* ======================================== */
/* STEP 3: VIEW RESULTS                     */
/* ======================================== */

/* Show summary of generated 1 year data */
SELECT
    '🎉 1 YEAR DATA GENERATION SUMMARY' AS info,
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

/* Show monthly breakdown */
SELECT
    TO_CHAR(timestamp, 'YYYY-MM') AS month,
    COUNT(*) AS records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people,
    ROUND(AVG(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
              female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus), 1) AS avg_people_per_hour
FROM api_detectiondata
WHERE timestamp >= '2024-07-23 00:00:00' AND timestamp <= '2025-07-23 23:59:59'
GROUP BY TO_CHAR(timestamp, 'YYYY-MM')
ORDER BY month;

/* Expected Results: */
/* - Total Records: ~8,760 (24 hours × 365 days) */
/* - Total People: ~200,000-500,000 (depending on random generation) */
/* - Date Range: July 23, 2024 to July 23, 2025 */
/* - Perfect for comprehensive analytics testing! */
