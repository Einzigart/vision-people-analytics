# Utility Scripts

This directory contains utility scripts for development and maintenance tasks.

## Scripts

- `check_aggregation_status.py` - Check the current status of data aggregation
- `reset_database.py` - Reset the database (drop all tables, remove migrations, recreate)

## Usage

Most of these scripts should be run from the backend directory:

```bash
# Check aggregation status
python scripts/check_aggregation_status.py

# Reset database
python scripts/reset_database.py
```

Note: These scripts are intended for development use only and should not be used in production.