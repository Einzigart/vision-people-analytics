-- Quick Test Data Generator
-- This script generates a small amount of test data for immediate testing

-- Clear today's data first
DELETE FROM api_detectiondata WHERE DATE(timestamp) = CURRENT_DATE;

-- Generate just a few records for immediate testing
INSERT INTO api_detectiondata (
    timestamp,
    male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
    female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
    is_aggregated
) VALUES 
-- Morning rush hour (8 AM)
(CURRENT_DATE + INTERVAL '8 hours', 2, 5, 12, 8, 4, 1, 1, 4, 10, 7, 3, 2, false),
(CURRENT_DATE + INTERVAL '8 hours 15 minutes', 1, 3, 8, 6, 3, 1, 2, 3, 9, 5, 2, 1, false),
(CURRENT_DATE + INTERVAL '8 hours 30 minutes', 3, 4, 10, 7, 5, 2, 1, 5, 11, 6, 4, 1, false),

-- Lunch time (12 PM)
(CURRENT_DATE + INTERVAL '12 hours', 1, 2, 6, 4, 2, 1, 1, 2, 7, 4, 2, 1, false),
(CURRENT_DATE + INTERVAL '12 hours 30 minutes', 2, 3, 8, 5, 3, 1, 0, 3, 6, 5, 3, 2, false),

-- Evening rush hour (6 PM)
(CURRENT_DATE + INTERVAL '18 hours', 2, 6, 15, 10, 6, 2, 1, 5, 13, 8, 4, 2, false),
(CURRENT_DATE + INTERVAL '18 hours 15 minutes', 1, 4, 11, 8, 4, 1, 2, 4, 12, 7, 3, 1, false),
(CURRENT_DATE + INTERVAL '18 hours 30 minutes', 3, 5, 13, 9, 5, 2, 1, 6, 14, 9, 5, 2, false),

-- Current hour (if not in the future)
(
    CASE 
        WHEN EXTRACT(HOUR FROM NOW()) >= 9 THEN 
            DATE_TRUNC('hour', NOW()) + INTERVAL '30 minutes'
        ELSE 
            CURRENT_DATE + INTERVAL '9 hours'
    END,
    1, 2, 5, 3, 2, 1, 1, 3, 6, 4, 2, 1, false
);

-- Show what we just created
SELECT 
    'Test Data Created' AS info,
    COUNT(*) AS records_created,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total_males,
    SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_females,
    SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
        female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total_people
FROM api_detectiondata 
WHERE DATE(timestamp) = CURRENT_DATE;

-- Show the actual records
SELECT 
    timestamp,
    (male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS males,
    (female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS females,
    (male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus + 
     female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total
FROM api_detectiondata 
WHERE DATE(timestamp) = CURRENT_DATE
ORDER BY timestamp;
