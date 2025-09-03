#!/usr/bin/env python
"""
Database Reset Script for Django Project
This script will completely reset the database by:
1. Dropping all tables in the database
2. Removing migration files (except __init__.py)
3. Creating fresh migrations
4. Running migrations to recreate all tables
"""

import glob
import os
import shutil
import sys

import django
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings  # noqa: E402
from django.core.management import execute_from_command_line  # noqa: E402


def drop_all_tables():
    """Drop all tables in the PostgreSQL database"""
    print('🗑️  Dropping all tables in the database...')

    db_settings = settings.DATABASES['default']

    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=db_settings['HOST'],
            port=db_settings['PORT'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            database=db_settings['NAME'],
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%'
        """)
        tables = cursor.fetchall()

        if tables:
            # Drop all tables
            for table in tables:
                table_name = table[0]
                print(f'  - Dropping table: {table_name}')
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')

            print(f'✅ Successfully dropped {len(tables)} tables')
        else:
            print('ℹ️  No tables found to drop')

        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print(f'❌ Error connecting to database: {e}')
        sys.exit(1)


def remove_migration_files():
    """Remove all migration files except __init__.py"""
    print('\n🧹 Removing migration files...')

    # Find all migration directories
    for app_dir in glob.glob('*/migrations/', recursive=True):
        print(f'  - Processing {app_dir}')

        # Remove all .py files except __init__.py
        for migration_file in glob.glob(os.path.join(app_dir, '*.py')):
            if not migration_file.endswith('__init__.py'):
                print(f'    - Removing {os.path.basename(migration_file)}')
                os.remove(migration_file)

        # Remove __pycache__ directories
        pycache_dir = os.path.join(app_dir, '__pycache__')
        if os.path.exists(pycache_dir):
            print('    - Removing __pycache__')
            shutil.rmtree(pycache_dir)

    print('✅ Migration files removed')


def create_fresh_migrations():
    """Create fresh migrations for all apps"""
    print('\n📝 Creating fresh migrations...')

    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print('✅ Fresh migrations created')
    except Exception as e:
        print(f'❌ Error creating migrations: {e}')
        sys.exit(1)


def run_migrations():
    """Run migrations to create all tables"""
    print('\n🚀 Running migrations...')

    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print('✅ Migrations applied successfully')
    except Exception as e:
        print(f'❌ Error running migrations: {e}')
        sys.exit(1)


def create_superuser_prompt():
    """Prompt to create a superuser"""
    print('\n👤 Would you like to create a superuser? (y/n): ', end='')
    choice = input().lower().strip()

    if choice in ['y', 'yes']:
        try:
            execute_from_command_line(['manage.py', 'createsuperuser'])
        except KeyboardInterrupt:
            print('\n⏭️  Skipping superuser creation')
        except Exception as e:
            print(f'❌ Error creating superuser: {e}')


def main():
    """Main function to orchestrate the database reset"""
    print('🔄 Starting Database Reset Process')
    print('=' * 50)

    # Confirm with user
    print('⚠️  WARNING: This will completely reset your database!')
    print('All data will be permanently lost.')
    print('\nAre you sure you want to continue? (y/n): ', end='')

    choice = input().lower().strip()
    if choice not in ['y', 'yes']:
        print('❌ Operation cancelled')
        sys.exit(0)

    print('\n🔄 Proceeding with database reset...\n')

    # Step 1: Drop all tables
    drop_all_tables()

    # Step 2: Remove migration files
    remove_migration_files()

    # Step 3: Create fresh migrations
    create_fresh_migrations()

    # Step 4: Run migrations
    run_migrations()

    # Step 5: Optional superuser creation
    create_superuser_prompt()

    print('\n' + '=' * 50)
    print('🎉 Database reset completed successfully!')
    print('Your database is now fresh and ready to use.')


if __name__ == '__main__':
    main()
