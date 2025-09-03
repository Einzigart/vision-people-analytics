-- Generate compact, hour-level dummy data for a single day
-- Configure the date below and run in Supabase/Postgres.
-- Numbers per active hour are randomized between 3–6 (inclusive).

/* =========================
   1) CONFIGURE ONCE (GLOBAL PARAMS)
   ========================= */
-- Edit only the VALUES below. All statements read from this temp table.
DROP TABLE IF EXISTS _gen_params;
CREATE TEMP TABLE _gen_params (
  target_date date,
  min_count int,
  max_count int,
  tz_offset_hours int
) ON COMMIT DROP;
INSERT INTO _gen_params (target_date, min_count, max_count, tz_offset_hours)
VALUES (DATE '2025-09-01', 3, 6, 7);  -- change once here

/* =========================
   2) OPTIONAL: CLEAR DATA FOR THAT DATE (by LOCAL date)
   ========================= */
-- DELETE FROM api_detectiondata
-- WHERE DATE(timestamp + make_interval(hours => (SELECT tz_offset_hours FROM _gen_params)))
--       = (SELECT target_date FROM _gen_params);

/* =========================
   3) INSERT HOURLY DATA (3–6 per active hour)
   - Active window: 06:00–18:00 (others = 0) to resemble the screenshot
   - Stronger male proportion to mimic the example
   - Age groups distributed and rebalanced so sums match the hour total
   ========================= */
INSERT INTO api_detectiondata (
  timestamp,
  male_0_9, male_10_19, male_20_29, male_30_39, male_40_49, male_50_plus,
  female_0_9, female_10_19, female_20_29, female_30_39, female_40_49, female_50_plus,
  is_aggregated
)
SELECT
  -- Store timestamps shifted back by tz_offset so the backend's +offset yields desired local time
  (p.target_date::timestamp + make_interval(hours => h.hr)
     - make_interval(hours => p.tz_offset_hours)) AS ts,

  -- Male age splits
  ms.m_0_9,
  ms.m_10_19,
  ms.m_20_29,
  ms.m_30_39,
  ms.m_40_49,
  GREATEST(0, ms.m_total - (ms.m_0_9 + ms.m_10_19 + ms.m_20_29 + ms.m_30_39 + ms.m_40_49)) AS m_50_plus,

  -- Female age splits
  fs.f_0_9,
  fs.f_10_19,
  fs.f_20_29,
  fs.f_30_39,
  fs.f_40_49,
  GREATEST(0, fs.f_total - (fs.f_0_9 + fs.f_10_19 + fs.f_20_29 + fs.f_30_39 + fs.f_40_49)) AS f_50_plus,

  false AS is_aggregated
FROM _gen_params p
JOIN LATERAL (
  SELECT hr FROM generate_series(0, 23) AS hr
) h ON TRUE
-- Build counts/splits per hour
JOIN LATERAL (
  SELECT
    CASE
      WHEN h.hr BETWEEN 6 AND 18 THEN (FLOOR(random() * (p.max_count - p.min_count + 1)) + p.min_count)::int
      ELSE 0
    END AS base_total,
    -- Male share between 0.75 and 0.95 to mirror example
    (0.75 + random() * 0.20) AS male_ratio
) dist ON TRUE
JOIN LATERAL (
  -- Derive total per gender
  SELECT
    dist.base_total AS total,
    ROUND(dist.base_total * dist.male_ratio)::int      AS m_total,
    (dist.base_total - ROUND(dist.base_total * dist.male_ratio))::int AS f_total
) g ON TRUE
-- Probabilistic per-person allocation to avoid over-concentration
-- Male weights: 0-9:0.03, 10-19:0.08, 20-29:0.40, 30-39:0.27, 40-49:0.15, 50+:0.07
JOIN LATERAL (
  SELECT
    COALESCE(SUM(CASE WHEN bucket = '0_9' THEN 1 ELSE 0 END), 0)::int      AS m_0_9,
    COALESCE(SUM(CASE WHEN bucket = '10_19' THEN 1 ELSE 0 END), 0)::int    AS m_10_19,
    COALESCE(SUM(CASE WHEN bucket = '20_29' THEN 1 ELSE 0 END), 0)::int    AS m_20_29,
    COALESCE(SUM(CASE WHEN bucket = '30_39' THEN 1 ELSE 0 END), 0)::int    AS m_30_39,
    COALESCE(SUM(CASE WHEN bucket = '40_49' THEN 1 ELSE 0 END), 0)::int    AS m_40_49,
    COALESCE(SUM(CASE WHEN bucket = '50_plus' THEN 1 ELSE 0 END), 0)::int  AS m_50_plus,
    g.m_total                                                 AS m_total
  FROM (
    SELECT CASE
      WHEN r < 0.03 THEN '0_9'
      WHEN r < 0.03 + 0.08 THEN '10_19'
      WHEN r < 0.03 + 0.08 + 0.40 THEN '20_29'
      WHEN r < 0.03 + 0.08 + 0.40 + 0.27 THEN '30_39'
      WHEN r < 0.03 + 0.08 + 0.40 + 0.27 + 0.15 THEN '40_49'
      ELSE '50_plus'
    END AS bucket
    FROM generate_series(1, GREATEST(g.m_total, 0)) i
    CROSS JOIN LATERAL (SELECT random() AS r) v
  ) picks
) ms ON TRUE

-- Female weights: 0-9:0.04, 10-19:0.10, 20-29:0.35, 30-39:0.28, 40-49:0.17, 50+:0.06
JOIN LATERAL (
  SELECT
    COALESCE(SUM(CASE WHEN bucket = '0_9' THEN 1 ELSE 0 END), 0)::int      AS f_0_9,
    COALESCE(SUM(CASE WHEN bucket = '10_19' THEN 1 ELSE 0 END), 0)::int    AS f_10_19,
    COALESCE(SUM(CASE WHEN bucket = '20_29' THEN 1 ELSE 0 END), 0)::int    AS f_20_29,
    COALESCE(SUM(CASE WHEN bucket = '30_39' THEN 1 ELSE 0 END), 0)::int    AS f_30_39,
    COALESCE(SUM(CASE WHEN bucket = '40_49' THEN 1 ELSE 0 END), 0)::int    AS f_40_49,
    COALESCE(SUM(CASE WHEN bucket = '50_plus' THEN 1 ELSE 0 END), 0)::int  AS f_50_plus,
    g.f_total                                                 AS f_total
  FROM (
    SELECT CASE
      WHEN r < 0.04 THEN '0_9'
      WHEN r < 0.04 + 0.10 THEN '10_19'
      WHEN r < 0.04 + 0.10 + 0.35 THEN '20_29'
      WHEN r < 0.04 + 0.10 + 0.35 + 0.28 THEN '30_39'
      WHEN r < 0.04 + 0.10 + 0.35 + 0.28 + 0.17 THEN '40_49'
      ELSE '50_plus'
    END AS bucket
    FROM generate_series(1, GREATEST(g.f_total, 0)) i
    CROSS JOIN LATERAL (SELECT random() AS r) v
  ) picks
) fs ON TRUE;

/* =========================
   4) QUICK CHECKS
   ========================= */
-- Hourly totals (male/female/total)
SELECT to_char(
         timestamp + make_interval(hours => (SELECT tz_offset_hours FROM _gen_params)),
         'HH24:00'
       ) AS local_hour,
       SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus)   AS male,
       SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS female,
       SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus +
           female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus) AS total
FROM api_detectiondata
WHERE DATE(timestamp + make_interval(hours => (SELECT tz_offset_hours FROM _gen_params)))
      = (SELECT target_date FROM _gen_params)
GROUP BY 1
ORDER BY 1;

-- Age totals for the day (rows aggregate to day totals like in the screenshot)
SELECT 'Male'   AS gender,
       SUM(male_0_9)  AS "0-9",
       SUM(male_10_19) AS "10-19",
       SUM(male_20_29) AS "20-29",
       SUM(male_30_39) AS "30-39",
       SUM(male_40_49) AS "40-49",
       SUM(male_50_plus) AS "50+",
       SUM(male_0_9 + male_10_19 + male_20_29 + male_30_39 + male_40_49 + male_50_plus) AS total
FROM api_detectiondata WHERE DATE(timestamp + make_interval(hours => (SELECT tz_offset_hours FROM _gen_params)))
      = (SELECT target_date FROM _gen_params)
UNION ALL
SELECT 'Female',
       SUM(female_0_9),
       SUM(female_10_19),
       SUM(female_20_29),
       SUM(female_30_39),
       SUM(female_40_49),
       SUM(female_50_plus),
       SUM(female_0_9 + female_10_19 + female_20_29 + female_30_39 + female_40_49 + female_50_plus)
FROM api_detectiondata WHERE DATE(timestamp + make_interval(hours => (SELECT tz_offset_hours FROM _gen_params)))
      = (SELECT target_date FROM _gen_params);
