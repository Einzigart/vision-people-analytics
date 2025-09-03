#!/usr/bin/env python3
"""
Test script to verify the dummy detection model is working correctly.

This script demonstrates:
1. How to run a quick test of the detection model
2. How to send a single detection manually
3. How to verify API connectivity
"""

import json
import requests
from datetime import datetime
from dummytestscript import DummyDetectionModel, DEFAULT_API_BASE_URL

def test_api_connection(api_url):
    """Test basic API connectivity"""
    print(f"🔍 Testing API connection to {api_url}...")
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ API connection successful!")
            print(f"📝 API Response: {response.json()}")
            return True
        else:
            print(f"❌ API connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_settings_api(api_url):
    """Test settings API endpoint"""
    print(f"\n⚙️ Testing settings API...")
    try:
        response = requests.get(f"{api_url}/settings/", timeout=10)
        if response.status_code == 200:
            settings = response.json()
            print("✅ Settings API working!")
            print(f"📋 Current settings:")
            print(f"   • Person Confidence: {settings.get('confidence_threshold_person', 'N/A')}")
            print(f"   • Face Confidence: {settings.get('confidence_threshold_face', 'N/A')}")
            print(f"   • Log Interval: {settings.get('log_interval_seconds', 'N/A')} seconds")
            return True
        elif response.status_code == 401:
            print("⚠️ Settings API requires authentication (this is normal)")
            return True
        else:
            print(f"❌ Settings API failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Settings API error: {e}")
        return False

def send_test_detection(api_url):
    """Send a single test detection"""
    print(f"\n📊 Sending test detection data...")
    
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "detections": {
            "male": {
                "0-9": 1,
                "10-19": 2,
                "20-29": 3,
                "30-39": 2,
                "40-49": 1,
                "50+": 0
            },
            "female": {
                "0-9": 0,
                "10-19": 1,
                "20-29": 4,
                "30-39": 3,
                "40-49": 2,
                "50+": 1
            }
        }
    }
    
    try:
        response = requests.post(
            f"{api_url}/detections/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 201:
            print("✅ Test detection sent successfully!")
            total_male = sum(test_data["detections"]["male"].values())
            total_female = sum(test_data["detections"]["female"].values())
            print(f"📈 Sent: {total_male + total_female} people (M:{total_male}, F:{total_female})")
            return True
        else:
            print(f"❌ Failed to send detection: HTTP {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending detection: {e}")
        return False

def test_detection_generation():
    """Test the detection data generation"""
    print(f"\n🔬 Testing detection data generation...")
    
    try:
        model = DummyDetectionModel()
        
        # Generate a few sample detections
        for i in range(3):
            detection_data = model.generate_realistic_detection_data()
            male_total = sum(detection_data["detections"]["male"].values())
            female_total = sum(detection_data["detections"]["female"].values())
            total = male_total + female_total
            
            print(f"   Sample {i+1}: {total} people (M:{male_total}, F:{female_total})")
            
        print("✅ Detection generation working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in detection generation: {e}")
        return False

def run_short_test(api_url, duration_seconds=30):
    """Run the dummy model for a short duration"""
    print(f"\n🚀 Running dummy model for {duration_seconds} seconds...")
    print("   (This will send real data to your backend)")
    
    try:
        model = DummyDetectionModel(api_base_url=api_url)
        
        # Override settings for quick testing
        model.settings.log_interval_seconds = 5  # Send every 5 seconds
        
        model.start()
        
        if model.running:
            print(f"⏱️ Model running... (will stop automatically in {duration_seconds}s)")
            import time
            time.sleep(duration_seconds)
            model.stop()
            print("✅ Short test completed!")
            return True
        else:
            print("❌ Failed to start model")
            return False
            
    except Exception as e:
        print(f"❌ Error in short test: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 DUMMY DETECTION MODEL - TEST SCRIPT")
    print("=" * 60)
    
    api_url = DEFAULT_API_BASE_URL
    
    # Test API connectivity
    if not test_api_connection(api_url):
        print("\n❌ Basic API test failed. Please ensure the backend is running.")
        print("   Try: cd backend && python manage.py runserver")
        return
    
    # Test settings API
    test_settings_api(api_url)
    
    # Test detection generation
    if not test_detection_generation():
        print("\n❌ Detection generation test failed.")
        return
    
    # Test sending detection data
    if not send_test_detection(api_url):
        print("\n❌ Detection sending test failed.")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("🎉 Your dummy detection model is ready to use!")
    print("\n📋 Next steps:")
    print("   1. Run: python dummytestscript.py")
    print("   2. Open your frontend and go to Settings page")
    print("   3. Adjust settings and watch them apply automatically")
    print("   4. Check Dashboard and Analytics for real-time data")
    
    # Ask if user wants to run a short live test
    try:
        response = input("\n🤔 Want to run a 30-second live test? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            run_short_test(api_url, 30)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    
    print("\n👋 Test completed!")

if __name__ == "__main__":
    main()
