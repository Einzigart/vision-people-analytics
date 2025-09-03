#!/usr/bin/env python3
"""
Test script to verify export functionality for gender demographics and age demographics
"""

import os
import sys
from datetime import date, timedelta

import django
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402


def test_api_endpoints():
    """Test the API endpoints for gender and age-gender data"""

    # Get or create a test user and token
    user, created = User.objects.get_or_create(username='testuser')
    if created:
        user.set_password('testpass123')
        user.save()

    token, created = Token.objects.get_or_create(user=user)

    base_url = 'http://localhost:8000/api'
    headers = {'Authorization': f'Token {token.key}'}

    # Test dates - last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    print('Testing Export Functionality for Gender Demographics and Age Demographics')
    print('=' * 70)

    # Test 1: Basic gender data endpoint
    print('\n1. Testing basic gender data endpoint...')
    try:
        response = requests.get(
            f'{base_url}/range/{start_date}/{end_date}/', headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f'   ✓ Basic gender data: {len(data.get("data", {}))} data points')
            print(f'   ✓ Data type: {data.get("type", "unknown")}')

            # Check if data has the required structure
            if data.get('data'):
                sample_key = list(data['data'].keys())[0]
                sample_data = data['data'][sample_key]
                required_fields = ['male', 'female']
                has_required = all(field in sample_data for field in required_fields)
                print(f'   ✓ Required fields present: {has_required}')
            else:
                print('   ⚠ No data found in response')
        else:
            print(f'   ✗ Failed with status {response.status_code}: {response.text}')
    except Exception as e:
        print(f'   ✗ Error: {e}')

    # Test 2: Age-gender data endpoint
    print('\n2. Testing age-gender data endpoint...')
    try:
        response = requests.get(
            f'{base_url}/age-gender-range/{start_date}/{end_date}/', headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f'   ✓ Age-gender data: {len(data.get("data", {}))} data points')
            print(f'   ✓ Data type: {data.get("type", "unknown")}')

            # Check if data has the required structure
            if data.get('data'):
                sample_key = list(data['data'].keys())[0]
                sample_data = data['data'][sample_key]

                # Check for demographics structure
                has_demographics = 'demographics' in sample_data
                has_totals = 'totals' in sample_data
                print(f'   ✓ Demographics structure: {has_demographics}')
                print(f'   ✓ Totals structure: {has_totals}')

                if has_demographics:
                    demographics = sample_data['demographics']
                    has_male_female = (
                        'male' in demographics and 'female' in demographics
                    )
                    print(f'   ✓ Male/Female demographics: {has_male_female}')

                    if has_male_female:
                        # Check for age groups
                        male_age_groups = demographics['male'].keys()
                        female_age_groups = demographics['female'].keys()
                        print(f'   ✓ Male age groups: {list(male_age_groups)}')
                        print(f'   ✓ Female age groups: {list(female_age_groups)}')
            else:
                print('   ⚠ No age-gender data found in response')
        else:
            print(f'   ✗ Failed with status {response.status_code}: {response.text}')
    except Exception as e:
        print(f'   ✗ Error: {e}')

    # Test 3: Today's stats
    print("\n3. Testing today's basic stats...")
    try:
        response = requests.get(f'{base_url}/today/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Today's data available")
            print(f'   ✓ Totals: {data.get("totals", {})}')
            print(
                f'   ✓ Hourly breakdown points: {len(data.get("hourly_breakdown", {}))}'
            )
        else:
            print(f'   ✗ Failed with status {response.status_code}: {response.text}')
    except Exception as e:
        print(f'   ✗ Error: {e}')

    # Test 4: Today's age-gender stats
    print("\n4. Testing today's age-gender stats...")
    try:
        response = requests.get(f'{base_url}/today-age-gender/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Today's age-gender data available")
            print(f'   ✓ Demographics: {bool(data.get("demographics"))}')
            print(f'   ✓ Totals: {data.get("totals", {})}')
            print(
                f'   ✓ Hourly breakdown points: {len(data.get("hourly_breakdown", {}))}'
            )
        else:
            print(f'   ✗ Failed with status {response.status_code}: {response.text}')
    except Exception as e:
        print(f'   ✗ Error: {e}')

    print('\n' + '=' * 70)
    print('Export Functionality Test Summary:')
    print('- Basic gender data should work for CSV/PDF export')
    print('- Age-gender data availability determines if age demographics work')
    print(
        '- If age-gender endpoints fail, run: python manage.py '
        'create_age_gender_dummy_data'
    )
    print('=' * 70)


def check_database_data():
    """Check what data is available in the database"""
    from api.models import AgeGenderDetection, DetectionData

    print('\nDatabase Data Check:')
    print('-' * 30)

    # Check basic detection data
    basic_count = DetectionData.objects.count()
    print(f'Basic detection records: {basic_count}')

    if basic_count > 0:
        latest_basic = DetectionData.objects.latest('timestamp')
        print(f'Latest basic record: {latest_basic.timestamp}')

    # Check age-gender detection data
    age_gender_count = AgeGenderDetection.objects.count()
    print(f'Age-gender records: {age_gender_count}')

    if age_gender_count > 0:
        latest_age_gender = AgeGenderDetection.objects.latest('timestamp')
        print(f'Latest age-gender record: {latest_age_gender.timestamp}')
    else:
        print(
            '⚠ No age-gender data found. Run: python manage.py '
            'create_age_gender_dummy_data'
        )


if __name__ == '__main__':
    print('Testing Export Functionality for Analytics')
    print('This script tests the API endpoints needed for export functionality')
    print()

    # Check database first
    check_database_data()

    # Test API endpoints
    test_api_endpoints()
