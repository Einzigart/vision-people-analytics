# SQL Scripts Documentation

This document provides detailed information about the SQL scripts included in the project for database management, testing, and diagnostics.

## Overview

The SQL scripts in the `sql_scripts/` directory are designed to help with database setup, testing, and maintenance tasks. These scripts can be used for development, testing, and production environments.

## Script Index

### 1. Data Generation Scripts
- `01_generate_today_data.sql` - Generate sample data for today
- `02_generate_week_data.sql` - Generate sample data for the past week
- `04_quick_test_data.sql` - Generate minimal test data
- `05_flexible_date_range_generator.sql` - Generate data for custom date ranges
- `07_generate_1_year_data.sql` - Generate one year of historical data

### 2. Data Management Scripts
- `03_clear_data.sql` - Clear detection data within a date range
- `06_clear_all_data.sql` - Clear all detection data

### 3. Diagnostic Scripts
- `08_check_aggregation_status.sql` - Check the status of data aggregation processes

### 4. Documentation
- `README.md` - Overview and usage instructions

## Detailed Script Descriptions

### 01_generate_today_data.sql
**Purpose**: Generate realistic sample data for today's date for testing purposes.

**Usage**:
```sql
-- Run the script to generate sample data for today
\i sql_scripts/01_generate_today_data.sql
```

**Features**:
- Generates data for each hour of the current day
- Creates realistic demographic distributions
- Populates all age groups for both genders
- Sets appropriate timestamps

**Sample Output**:
- Creates 24 records (one per hour)
- Varies counts throughout the day to simulate realistic traffic patterns

### 02_generate_week_data.sql
**Purpose**: Generate a full week of sample data for testing historical analytics.

**Usage**:
```sql
-- Run the script to generate sample data for the past week
\i sql_scripts/02_generate_week_data.sql
```

**Features**:
- Generates data for the past 7 days
- Creates daily patterns with variations
- Includes weekend vs. weekday differences
- Populates all demographic fields

**Sample Output**:
- Creates 168 records (24 hours × 7 days)
- Weekend days may have different patterns than weekdays

### 03_clear_data.sql
**Purpose**: Remove detection data within a specified date range.

**Usage**:
```sql
-- Run the script to clear data
\i sql_scripts/03_clear_data.sql
```

**Features**:
- Interactive script that prompts for date range
- Safe deletion with confirmation
- Maintains aggregation data
- Useful for testing and development

**Parameters**:
- Start date (inclusive)
- End date (inclusive)

### 04_quick_test_data.sql
**Purpose**: Generate minimal test data for quick testing.

**Usage**:
```sql
-- Run the script to generate minimal test data
\i sql_scripts/04_quick_test_data.sql
```

**Features**:
- Creates only a few records for fast testing
- Minimal demographic data
- Quick execution time
- Useful for unit tests

**Sample Output**:
- Creates 3-5 records with basic demographic data

### 05_flexible_date_range_generator.sql
**Purpose**: Generate sample data for any custom date range.

**Usage**:
```sql
-- Run the script to generate data for custom ranges
\i sql_scripts/05_flexible_date_range_generator.sql
```

**Features**:
- Highly configurable date range
- Parameterized queries
- Flexible demographic distribution
- Useful for specific testing scenarios

**Parameters**:
- Start date
- End date
- Data density (records per day)
- Demographic distribution patterns

### 06_clear_all_data.sql
**Purpose**: Remove all detection data from the database.

**Usage**:
```sql
-- Run the script to clear all detection data
\i sql_scripts/06_clear_all_data.sql
```

**Features**:
- Completely clears detection data table
- Requires confirmation before execution
- Maintains table structure
- Useful for fresh starts in development

**Warning**: This script will permanently delete all detection data.

### 07_generate_1_year_data.sql
**Purpose**: Generate a full year of historical data for long-term analytics testing.

**Usage**:
```sql
-- Run the script to generate one year of data
\i sql_scripts/07_generate_1_year_data.sql
```

**Features**:
- Creates daily aggregated data for one year
- Seasonal variations in data patterns
- Monthly trend simulations
- Comprehensive demographic coverage

**Sample Output**:
- Creates 365 records (one per day)
- May include special events or holidays

### 08_check_aggregation_status.sql
**Purpose**: Diagnose the current state of data aggregation processes.

**Usage**:
```sql
-- Run the script to check aggregation status
\i sql_scripts/08_check_aggregation_status.sql
```

**Features**:
- Provides comprehensive status report
- Shows unaggregated vs. aggregated data counts
- Displays recent records for verification
- Checks data consistency between raw and aggregated data

**Information Provided**:
- Total records count
- Aggregated vs. unaggregated records
- Date range of data
- Sample of recent records
- Data consistency verification
- Troubleshooting information

## Usage Instructions

### Running Scripts with psql
```bash
# Connect to database and run script
psql -d your_database_name -f sql_scripts/script_name.sql

# Or from within psql
\i sql_scripts/script_name.sql
```

### Running Scripts with Django
```bash
# From Django shell
python manage.py shell < sql_scripts/script_name.sql

# Or using dbshell
python manage.py dbshell
```

## Best Practices

### For Development
1. Use `04_quick_test_data.sql` for unit tests
2. Use `01_generate_today_data.sql` for UI testing
3. Use `02_generate_week_data.sql` for feature testing
4. Clear data regularly with `03_clear_data.sql`

### For Testing
1. Always verify data generation with `08_check_aggregation_status.sql`
2. Use appropriate data volumes for test scenarios
3. Document data states for reproducible tests

### For Production
1. Review scripts carefully before running
2. Backup data before running destructive scripts
3. Test scripts in staging environment first
4. Monitor performance impact of data generation scripts

## Script Customization

### Modifying Data Patterns
Most scripts use parameterized approaches that allow customization:
- Adjust demographic distributions
- Modify data density
- Change temporal patterns
- Add special events or anomalies

### Adding New Scripts
When creating new scripts:
1. Follow the naming convention (numbered sequence)
2. Include clear comments and documentation
3. Add error handling and validation
4. Test thoroughly before committing

## Troubleshooting

### Common Issues
1. **Permission denied**: Ensure database user has appropriate permissions
2. **Data conflicts**: Check for constraint violations
3. **Performance issues**: Monitor execution time for large data sets
4. **Incomplete execution**: Check for errors in script output

### Diagnostic Steps
1. Run `08_check_aggregation_status.sql` to verify current state
2. Check database logs for error messages
3. Verify database connectivity and permissions
4. Test with smaller data sets first

## Security Considerations

### Production Use
1. Review all scripts before running in production
2. Ensure proper backups before destructive operations
3. Limit database user permissions as appropriate
4. Audit script execution in production environments

### Data Privacy
1. Sample data scripts generate synthetic data only
2. No real personal information is included
3. Follow organizational data privacy policies
4. Ensure compliance with relevant regulations

## Maintenance

### Regular Updates
1. Update scripts when database schema changes
2. Review and optimize performance regularly
3. Add new scripts for emerging needs
4. Remove deprecated scripts

### Version Control
1. Include all script changes in version control
2. Document changes in commit messages
3. Tag major script updates
4. Coordinate with application version updates