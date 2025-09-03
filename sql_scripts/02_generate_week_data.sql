-- Generate Dummy Detection Data for Last 7 Days
-- Run this script in your Supabase SQL Editor to populate a week's worth of data

-- Optional: Clear existing data for the last 7 days
-- DELETE FROM api_detectiondata WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';

-- Generate realistic detection data for the last 7 days
INSERT INTO api_detectiondata (
    timestamp,
    male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
    female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
    is_aggregated
)
SELECT 
    -- Generate timestamps every 30 minutes for the last 7 days
    (CURRENT_DATE - day_offset) + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval AS timestamp,
    
    -- Calculate base traffic multiplier based on day of week and hour
    CASE 
        -- Weekend patterns (Saturday = 6, Sunday = 0)
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
            CASE 
                WHEN hour_num BETWEEN 10 AND 12 OR hour_num BETWEEN 14 AND 18 THEN -- Weekend peak
                    FLOOR(random() * 6 + 3)::int
                WHEN hour_num BETWEEN 8 AND 9 OR hour_num BETWEEN 13 AND 13 OR hour_num BETWEEN 19 AND 21 THEN
                    FLOOR(random() * 4 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 7 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 3 + 1)::int
            END
        -- Weekday patterns
        ELSE
            CASE 
                WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN -- Rush hours
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN -- Lunch time
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN -- Night
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.08 AS male_0_9, -- 8% children
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.12 AS male_10_19, -- 12% teens
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.25 AS male_20_29, -- 25% young adults
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.22 AS male_30_39, -- 22% adults
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.18 AS male_40_49, -- 18% middle-aged
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.15 AS male_50_plus, -- 15% seniors
    
    -- Female demographics (similar patterns)
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.08 AS female_0_9,
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.12 AS female_10_19,
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.25 AS female_20_29,
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.22 AS female_30_39,
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.18 AS female_40_49,
    
    CASE 
        WHEN EXTRACT(DOW FROM CURRENT_DATE - day_offset) IN (0, 6) THEN
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
                    FLOOR(random() * 10 + 5)::int
                WHEN hour_num BETWEEN 12 AND 14 THEN
                    FLOOR(random() * 7 + 3)::int
                WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
                    FLOOR(random() * 5 + 2)::int
                WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
                    FLOOR(random() * 2)::int
                ELSE 
                    FLOOR(random() * 4 + 1)::int
            END
    END * 0.15 AS female_50_plus,
    
    false AS is_aggregated
FROM 
    generate_series(0, 6) AS day_offset,
    generate_series(0, 23) AS hour_num,
    generate_series(0, 30, 30) AS minute_num -- Every 30 minutes
WHERE 
    -- Don't generate future data
    (CURRENT_DATE - day_offset) + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval <= NOW();

-- Show summary of generated data
SELECT 
    'Week Data Summary' AS info,
    COUNT(*) AS total_records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total_males,
    SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_females,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata 
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';
