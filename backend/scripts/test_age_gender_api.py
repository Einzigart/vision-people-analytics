from datetime import datetime

import requests

# Test data in the new age-gender format
test_data = {
    'timestamp': '2025-05-29T21:20:00',
    'detections': {
        'male': {'0-9': 0, '10-19': 1, '20-29': 3, '30-39': 2, '40-49': 1, '50+': 0},
        'female': {'0-9': 1, '10-19': 2, '20-29': 2, '30-39': 1, '40-49': 0, '50+': 1},
    },
}

# API endpoints
BASE_URL = 'http://localhost:8000/api'
DETECTION_ENDPOINT = (
    f'{BASE_URL}/detections/'  # This is now the primary endpoint for all detections
)
# AGE_GENDER_ENDPOINT = f"{BASE_URL}/age-gender-detections/" # This endpoint is removed
TODAY_AGE_GENDER_ENDPOINT = f'{BASE_URL}/today-age-gender/'

# This function is removed as the dedicated age-gender endpoint is gone.
# def test_age_gender_endpoint():
#     """Test the new age-gender detection endpoint"""
#     print("Testing age-gender detection endpoint...")

#     try:
#         response = requests.post(AGE_GENDER_ENDPOINT, json=test_data)
# AGE_GENDER_ENDPOINT no longer exists
#         print(f"Status Code: {response.status_code}")
#         print(f"Response: {response.json()}")

#         if response.status_code == 201:
#             print("✅ Age-gender data successfully posted!")
#         else:
#             print("❌ Failed to post age-gender data")

#     except Exception as e:
#         print(f"❌ Error testing age-gender endpoint: {e}")


def test_post_detection_data_with_age_gender():
    """Test that the main detections endpoint can handle the detailed age-gender
    format"""
    print('\nTesting POST to /detections/ with detailed age-gender data...')

    try:
        response = requests.post(DETECTION_ENDPOINT, json=test_data)
        print(f'Status Code: {response.status_code}')
        response_json = response.json()
        print(f'Response: {response_json}')

        if response.status_code == 201 and response_json.get('status') == 'success':
            print(
                '✅ Detailed age-gender data successfully posted to /detections/ '
                'endpoint!'
            )
            # Optionally, verify parts of the response structure if needed
            if 'data' in response_json and 'male_0_9' in response_json['data']:
                print('✅ Response contains expected age-gender fields.')
            else:
                print(
                    '⚠️ Response does not contain detailed age-gender fields as '
                    'expected in data.'
                )
        else:
            print(
                '❌ Failed to post detailed age-gender data to /detections/ endpoint.'
            )

    except Exception as e:
        print(f'❌ Error testing POST to /detections/ with age-gender data: {e}')


def test_today_age_gender_stats():
    """Test the today age-gender stats endpoint"""
    print("\nTesting today's age-gender stats...")

    try:
        response = requests.get(TODAY_AGE_GENDER_ENDPOINT)
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print("✅ Today's age-gender stats retrieved successfully!")
            print(f'Demographics: {data.get("demographics", {})}')
            print(f'Totals: {data.get("totals", {})}')
        else:
            print("❌ Failed to get today's age-gender stats")

    except Exception as e:
        print(f"❌ Error testing today's age-gender stats: {e}")


def test_age_gender_range():
    """Test the age-gender date range endpoint"""
    print('\nTesting age-gender date range...')

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        endpoint = f'{BASE_URL}/age-gender-range/{today}/{today}/'
        response = requests.get(endpoint)
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print('✅ Age-gender date range retrieved successfully!')
            print(f'Type: {data.get("type", "N/A")}')
            print(f'Data keys: {list(data.get("data", {}).keys())}')
        else:
            print('❌ Failed to get age-gender date range')

    except Exception as e:
        print(f'❌ Error testing age-gender date range: {e}')


if __name__ == '__main__':
    print('🧪 Testing Detection API (with focus on Age-Gender capabilities)')
    print('=' * 50)

    # Test all endpoints
    # test_age_gender_endpoint() # Removed
    test_post_detection_data_with_age_gender()  # Renamed from
    # test_backward_compatibility
    test_today_age_gender_stats()
    test_age_gender_range()

    print('\n' + '=' * 50)
    print('✨ Testing completed!')
