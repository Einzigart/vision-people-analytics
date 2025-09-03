-- Generate Dummy Detection Data for Today
-- Run this script in your Supabase SQL Editor to populate today's data

-- First, let's clear any existing data for today (optional)
-- DELETE FROM api_detectiondata WHERE DATE(timestamp) = CURRENT_DATE;

-- Generate realistic detection data for today
INSERT INTO api_detectiondata (
    timestamp,
    male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
    female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
    is_aggregated
)
SELECT 
    -- Generate timestamps every 15 minutes throughout today
    CURRENT_DATE + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval AS timestamp,
    
    -- Male age groups with realistic distributions
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN -- Rush hours
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int -- 2-24 people
        WHEN hour_num BETWEEN 12 AND 14 THEN -- Lunch time
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int -- 1-12 people
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int -- 1-4 people
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN -- Night
            FLOOR(random() * 2)::int -- 0-1 people
        ELSE 
            FLOOR(random() * 3 + 1)::int -- 1-3 people
    END * 0.08 AS male_0_9, -- 8% children
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.12 AS male_10_19, -- 12% teens
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.25 AS male_20_29, -- 25% young adults (highest)
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.22 AS male_30_39, -- 22% adults
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.18 AS male_40_49, -- 18% middle-aged
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.15 AS male_50_plus, -- 15% seniors
    
    -- Female age groups (similar patterns)
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.08 AS female_0_9,
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.12 AS female_10_19,
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.25 AS female_20_29,
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.22 AS female_30_39,
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.18 AS female_40_49,
    
    CASE 
        WHEN hour_num BETWEEN 8 AND 10 OR hour_num BETWEEN 17 AND 19 THEN
            FLOOR(random() * 8 + 2)::int * FLOOR(random() * 3 + 1)::int
        WHEN hour_num BETWEEN 12 AND 14 THEN
            FLOOR(random() * 6 + 1)::int * FLOOR(random() * 2 + 1)::int
        WHEN hour_num BETWEEN 6 AND 7 OR hour_num BETWEEN 15 AND 16 OR hour_num BETWEEN 20 AND 21 THEN
            FLOOR(random() * 4 + 1)::int
        WHEN hour_num BETWEEN 22 AND 23 OR hour_num BETWEEN 0 AND 5 THEN
            FLOOR(random() * 2)::int
        ELSE 
            FLOOR(random() * 3 + 1)::int
    END * 0.15 AS female_50_plus,
    
    false AS is_aggregated
FROM 
    generate_series(0, 23) AS hour_num,
    generate_series(0, 45, 15) AS minute_num -- Every 15 minutes
WHERE 
    -- Only generate data up to current time if today
    (CURRENT_DATE + (hour_num || ' hours')::interval + (minute_num || ' minutes')::interval) <= NOW();

-- Show summary of generated data
SELECT 
    'Today Data Summary' AS info,
    COUNT(*) AS total_records,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total_males,
    SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_females,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata 
WHERE DATE(timestamp) = CURRENT_DATE;
