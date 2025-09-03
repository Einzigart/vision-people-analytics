"""
Custom test runner for Supabase that handles connection issues.
"""
from django.test.runner import DiscoverRunner
from django.db import connections


class SupabaseTestRunner(DiscoverRunner):
    """
    Custom test runner for Supabase that avoids database creation/destruction issues.
    """
    
    def setup_databases(self, **kwargs):
        """
        Set up databases for testing.
        Instead of creating new databases, we'll use a test schema.
        """
        # Get the default database connection
        connection = connections['default']
        
        # Create the test schema if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS test")
            
            # Clear any existing data in the test schema
            cursor.execute("""
                DO $$ 
                DECLARE 
                    r RECORD; 
                BEGIN 
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'test') LOOP 
                        EXECUTE 'DROP TABLE IF EXISTS test.' || quote_ident(r.tablename) || ' CASCADE'; 
                    END LOOP; 
                END $$;
            """)
        
        # Return the normal setup result
        return super().setup_databases(**kwargs)
    
    def teardown_databases(self, old_config, **kwargs):
        """
        Teardown databases after testing.
        Instead of dropping databases, we'll just clear the test schema.
        """
        # Get the default database connection
        connection = connections['default']
        
        # Clear the test schema instead of dropping the database
        with connection.cursor() as cursor:
            cursor.execute("""
                DO $$ 
                DECLARE 
                    r RECORD; 
                BEGIN 
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'test') LOOP 
                        EXECUTE 'DROP TABLE IF EXISTS test.' || quote_ident(r.tablename) || ' CASCADE'; 
                    END LOOP; 
                END $$;
            """)
        
        # Don't call super().teardown_databases to avoid connection issues