# SQL Scripts for Dummy Data Generation

These SQL scripts can be run directly in your Supabase SQL Editor to generate realistic dummy data for your people counting system.

## 📁 Available Scripts

### 1. `04_quick_test_data.sql` ⚡ (Start Here!)
**Best for immediate testing**
- Generates just 9 records for today
- Includes morning rush, lunch, and evening rush patterns
- Perfect for testing the dashboard quickly
- **Run this first to see immediate results**

### 2. `01_generate_today_data.sql` 📅
**Generate full day's data**
- Creates realistic data for today (every 15 minutes)
- Includes rush hour patterns (8-10 AM, 12-2 PM, 5-7 PM)
- Realistic age/gender distributions
- About 96 records for a full day

### 3. `02_generate_week_data.sql` 📊
**Generate week's worth of data**
- Creates data for the last 7 days (every 30 minutes)
- Different patterns for weekdays vs weekends
- Realistic traffic variations
- About 336 records per day × 7 days = ~2,352 records

### 4. `05_flexible_date_range_generator.sql` 🎯 (Most Powerful!)
**Generate data for any date range**
- **Fully customizable start and end dates**
- Configurable time intervals (15, 30, 60 minutes)
- Weekday vs weekend patterns
- Perfect for historical data or specific periods
- **Example: Generate 2 months of data from June 1 to July 31**

### 5. `03_clear_data.sql` 🗑️
**Selective data clearing**
- Multiple clearing options (today, week, month, specific dates)
- Safe options with confirmation
- Shows data summary before/after clearing

### 6. `06_clear_all_data.sql` 🚨
**Complete database reset**
- **⚠️ DANGER: Clears ALL data and aggregations**
- Includes safety checks and confirmations
- Use only for complete fresh start
- Shows comprehensive before/after summaries

## 🚀 Quick Start Guide

### Step 1: Open Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New query"

### Step 2: Run Quick Test (Recommended)
```sql
-- Copy and paste the content of 04_quick_test_data.sql
-- This will give you immediate results to test your dashboard
```

### Step 3: Check Your Dashboard
- Refresh your dashboard page
- You should now see data for today
- Check the "Today's Hourly Traffic" chart
- Verify the "Age Distribution" shows data

### Step 4: Generate More Data (Optional)
If you want more comprehensive data:
```sql
-- Option A: Run 01_generate_today_data.sql for full day
-- Option B: Run 02_generate_week_data.sql for full week
-- Option C: Run 05_flexible_date_range_generator.sql for custom dates
```

### Step 5: Custom Date Range (Advanced)
For specific date ranges, use the flexible generator:
```sql
-- Edit these variables in 05_flexible_date_range_generator.sql:
start_date DATE := '2025-07-01'::DATE;  -- Your start date
end_date DATE := '2025-07-31'::DATE;    -- Your end date
interval_minutes INTEGER := 30;         -- Time between records
```

## 📊 Data Patterns

### Realistic Traffic Patterns
- **Rush Hours (8-10 AM, 5-7 PM)**: High traffic
- **Lunch Time (12-2 PM)**: Moderate traffic  
- **Regular Hours**: Normal traffic
- **Night Hours (10 PM - 6 AM)**: Low traffic
- **Weekends**: Different patterns (later peaks, more leisure traffic)

### Age/Gender Distribution
- **0-9 years**: 8% (children)
- **10-19 years**: 12% (teens)
- **20-29 years**: 25% (young adults - highest)
- **30-39 years**: 22% (adults)
- **40-49 years**: 18% (middle-aged)
- **50+ years**: 15% (seniors)

## 🔧 Customization

### Modify Traffic Levels
To increase/decrease overall traffic, modify the multipliers in the CASE statements:
```sql
-- Change these values to adjust traffic levels
FLOOR(random() * 8 + 2)::int  -- Rush hour: 2-10 people
FLOOR(random() * 4 + 1)::int  -- Normal: 1-5 people
```

### Change Time Intervals
```sql
-- For more frequent data points
generate_series(0, 45, 15) -- Every 15 minutes
generate_series(0, 30, 10) -- Every 10 minutes

-- For less frequent data points  
generate_series(0, 0, 60)  -- Every hour
```

### Adjust Age Distributions
```sql
-- Modify these multipliers to change age group percentages
END * 0.25 AS male_20_29,  -- 25% young adults
END * 0.08 AS male_0_9,    -- 8% children
```

## 🐛 Troubleshooting

### "Table doesn't exist" error
The table name might be different. Check your actual table name:
```sql
-- Check table name
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE '%detection%';

-- Common variations:
-- api_detectiondata
-- detectiondata  
-- detection_data
```

### No data showing in dashboard
1. Check if data was actually inserted:
```sql
SELECT COUNT(*) FROM api_detectiondata WHERE DATE(timestamp) = CURRENT_DATE;
```

2. Check the timestamp format:
```sql
SELECT timestamp FROM api_detectiondata ORDER BY timestamp DESC LIMIT 5;
```

3. Verify your Django timezone settings match your database timezone

### Performance issues
If the scripts are slow:
1. Start with `04_quick_test_data.sql` (fastest)
2. Use smaller time ranges
3. Reduce the frequency of data points

## 📈 Expected Results

After running the quick test script, your dashboard should show:
- **Total People**: ~50-100 people detected today
- **Male/Female**: Roughly 50/50 split
- **Age Distribution**: Realistic bell curve with peak at 20-29 years
- **Hourly Traffic**: Peaks at 8 AM, 12 PM, and 6 PM

## 🎯 Next Steps

1. **Start with quick test** to verify everything works
2. **Generate full day** if you want complete hourly patterns  
3. **Generate full week** for comprehensive analytics testing
4. **Set up real-time data** using the detection model scripts

Happy testing! 🚀
