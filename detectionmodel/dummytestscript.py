#!/usr/bin/env python3
"""
Dummy Live Detection Model Script

This script simulates a real-time detection model that generates and sends
detection data to the backend API. It can be controlled through the frontend
settings interface for dynamic configuration updates.

Features:
- Generates realistic age-gender detection data
- Sends data to backend API at configurable intervals
- Fetches and applies settings updates from backend in real-time
- Comprehensive logging and error handling
- Graceful shutdown handling
- Realistic daily/hourly patterns simulation
- Windows-compatible logging (no emoji encoding issues)
"""

import os
import sys
import time
import json
import random
import logging
import requests
import threading
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# Configuration Constants
DEFAULT_API_BASE_URL = "http://localhost:8000/api"
DEFAULT_LOG_INTERVAL = 60  # seconds
DEFAULT_CONFIDENCE_PERSON = 0.5
DEFAULT_CONFIDENCE_FACE = 0.5
SETTINGS_CHECK_INTERVAL = 30  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

@dataclass
class ModelSettings:
    """Data class for model settings"""
    confidence_threshold_person: float = DEFAULT_CONFIDENCE_PERSON
    confidence_threshold_face: float = DEFAULT_CONFIDENCE_FACE
    log_interval_seconds: int = DEFAULT_LOG_INTERVAL
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        # Validate settings
        if not (0.0 <= self.confidence_threshold_person <= 1.0):
            raise ValueError("Person confidence threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.confidence_threshold_face <= 1.0):
            raise ValueError("Face confidence threshold must be between 0.0 and 1.0")
        if not (1 <= self.log_interval_seconds <= 3600):
            raise ValueError("Log interval must be between 1 and 3600 seconds")

class DummyDetectionModel:
    """
    Dummy detection model that simulates real-time person detection with age/gender analysis
    """
    
    def __init__(self, api_base_url: str = DEFAULT_API_BASE_URL):
        self.api_base_url = api_base_url.rstrip('/')
        self.settings = ModelSettings()
        self.running = False
        self.settings_thread = None
        self.detection_thread = None
        
        # Check if console supports Unicode
        self.unicode_supported = self._check_unicode_support()
        
        # Setup logging
        self.setup_logging()
        
        # Session for API requests with retry strategy
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DummyDetectionModel/1.0'
        })
        
        # Shutdown event for graceful exit
        self.shutdown_event = threading.Event()
        
        # Track last settings update to avoid unnecessary API calls
        self.last_settings_check = None
        
        self.logger.info("Dummy Detection Model initialized")
        self.logger.info(f"API Base URL: {self.api_base_url}")
    
    def _check_unicode_support(self) -> bool:
        """Check if the console supports Unicode characters"""
        try:
            # Test if we can write Unicode to stdout
            test_str = "🔥"
            sys.stdout.write(test_str)
            sys.stdout.flush()
            return True
        except (UnicodeEncodeError, UnicodeError):
            return False
    
    def _get_emoji(self, emoji: str, fallback: str) -> str:
        """Get emoji if supported, otherwise return fallback text"""
        return emoji if self.unicode_supported else fallback
    
    def setup_logging(self):
        """Setup comprehensive logging with Windows compatibility"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Setup file handler with UTF-8 encoding
        try:
            file_handler = logging.FileHandler(
                f"dummy_detection_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter(log_format))
        except Exception:
            # Fallback if UTF-8 encoding fails
            file_handler = logging.FileHandler(
                f"dummy_detection_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def fetch_settings_from_api(self) -> bool:
        """
        Fetch current settings from the backend API using the public endpoint
        Returns True if settings were updated, False otherwise
        """
        try:
            # Use the new public settings endpoint (no authentication required)
            response = self.session.get(f"{self.api_base_url}/public-settings/", timeout=10)
            
            if response.status_code == 200:
                settings_data = response.json()
                
                # Check if settings have actually changed
                old_settings = (
                    self.settings.confidence_threshold_person,
                    self.settings.confidence_threshold_face,
                    self.settings.log_interval_seconds
                )
                
                new_settings = ModelSettings(
                    confidence_threshold_person=settings_data.get('confidence_threshold_person', DEFAULT_CONFIDENCE_PERSON),
                    confidence_threshold_face=settings_data.get('confidence_threshold_face', DEFAULT_CONFIDENCE_FACE),
                    log_interval_seconds=settings_data.get('log_interval_seconds', DEFAULT_LOG_INTERVAL),
                    last_updated=settings_data.get('last_updated')
                )
                
                new_settings_tuple = (
                    new_settings.confidence_threshold_person,
                    new_settings.confidence_threshold_face,
                    new_settings.log_interval_seconds
                )
                
                if old_settings != new_settings_tuple:
                    self.settings = new_settings
                    gear_emoji = self._get_emoji("⚙️", "[SETTINGS]")
                    self.logger.info(f"{gear_emoji} Settings updated from API: Person={self.settings.confidence_threshold_person}, Face={self.settings.confidence_threshold_face}, Interval={self.settings.log_interval_seconds}s")
                    return True
                
                return False
                
            else:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.warning(f"{x_emoji} Failed to fetch settings: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            x_emoji = self._get_emoji("❌", "[ERROR]")
            self.logger.error(f"{x_emoji} Error fetching settings from API: {e}")
            return False
        except Exception as e:
            x_emoji = self._get_emoji("❌", "[ERROR]")
            self.logger.error(f"{x_emoji} Unexpected error fetching settings: {e}")
            return False
    
    def generate_realistic_detection_data(self) -> Dict[str, Any]:
        """
        Generate realistic detection data based on time of day and current settings
        """
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        # Base detection probability influenced by confidence thresholds
        # Higher confidence = fewer detections but more accurate
        person_modifier = 1.0 - (self.settings.confidence_threshold_person - 0.5) * 0.5
        face_modifier = 1.0 - (self.settings.confidence_threshold_face - 0.5) * 0.3
        
        # Realistic daily patterns
        if 6 <= hour <= 9:  # Morning rush
            base_count = random.randint(15, 30)
        elif 9 <= hour <= 11:  # Morning work hours
            base_count = random.randint(8, 15)
        elif 11 <= hour <= 13:  # Lunch time
            base_count = random.randint(20, 35)
        elif 13 <= hour <= 17:  # Afternoon work hours
            base_count = random.randint(10, 20)
        elif 17 <= hour <= 19:  # Evening rush
            base_count = random.randint(25, 40)
        elif 19 <= hour <= 22:  # Evening leisure
            base_count = random.randint(12, 25)
        elif 22 <= hour <= 24 or 0 <= hour <= 6:  # Night/early morning
            base_count = random.randint(0, 8)
        else:
            base_count = random.randint(5, 15)
        
        # Apply confidence modifiers
        total_detections = max(0, int(base_count * person_modifier))
        
        # If no detections, return empty data
        if total_detections == 0:
            return {
                "timestamp": now.isoformat(),
                "detections": {
                    "male": {
                        "0-9": 0, "10-19": 0, "20-29": 0,
                        "30-39": 0, "40-49": 0, "50+": 0
                    },
                    "female": {
                        "0-9": 0, "10-19": 0, "20-29": 0,
                        "30-39": 0, "40-49": 0, "50+": 0
                    }
                }
            }
        
        # Generate age/gender distribution with realistic patterns
        age_groups = ["0-9", "10-19", "20-29", "30-39", "40-49", "50+"]
        
        # Different distributions based on time of day
        if 9 <= hour <= 17:  # Work hours - more adults
            age_weights = [0.05, 0.15, 0.35, 0.25, 0.15, 0.05]
        elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours - mixed
            age_weights = [0.10, 0.20, 0.30, 0.20, 0.15, 0.05]
        elif 19 <= hour <= 22:  # Evening leisure - varied
            age_weights = [0.15, 0.25, 0.25, 0.15, 0.15, 0.05]
        else:  # Other times - more uniform
            age_weights = [0.15, 0.20, 0.25, 0.20, 0.15, 0.05]
        
        # Gender distribution (slightly more females in retail/shopping contexts)
        gender_ratio = random.uniform(0.45, 0.55)  # Percentage male
        
        male_count = int(total_detections * gender_ratio)
        female_count = total_detections - male_count
        
        # Distribute males across age groups
        male_distribution = np.random.multinomial(male_count, age_weights) if male_count > 0 else [0] * 6
        
        # Distribute females across age groups  
        female_distribution = np.random.multinomial(female_count, age_weights) if female_count > 0 else [0] * 6
        
        # Apply face detection confidence (some people might not have visible faces)
        face_detection_rate = min(0.95, 0.5 + self.settings.confidence_threshold_face * 0.45)
        
        # Reduce counts based on face detection rate
        for i in range(len(male_distribution)):
            if male_distribution[i] > 0:
                male_distribution[i] = np.random.binomial(male_distribution[i], face_detection_rate)
        
        for i in range(len(female_distribution)):
            if female_distribution[i] > 0:
                female_distribution[i] = np.random.binomial(female_distribution[i], face_detection_rate)
        
        # Create the detection payload
        detection_data = {
            "timestamp": now.isoformat(),
            "detections": {
                "male": {
                    age_groups[i]: int(male_distribution[i]) for i in range(len(age_groups))
                },
                "female": {
                    age_groups[i]: int(female_distribution[i]) for i in range(len(age_groups))
                }
            }
        }
        
        return detection_data
    
    def send_detection_data(self, data: Dict[str, Any]) -> bool:
        """
        Send detection data to the backend API with retry logic
        """
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                response = self.session.post(
                    f"{self.api_base_url}/detections/",
                    json=data,
                    timeout=15
                )
                
                if response.status_code == 201:
                    response_data = response.json()
                    total_detected = sum(data["detections"]["male"].values()) + sum(data["detections"]["female"].values())
                    check_emoji = self._get_emoji("✅", "[SUCCESS]")
                    self.logger.info(f"{check_emoji} Detection data sent successfully: {total_detected} people detected")
                    return True
                else:
                    x_emoji = self._get_emoji("❌", "[ERROR]")
                    self.logger.warning(f"{x_emoji} Failed to send detection data: HTTP {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.error(f"{x_emoji} Network error sending detection data (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {e}")
                
            except Exception as e:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.error(f"{x_emoji} Unexpected error sending detection data (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {e}")
            
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                clock_emoji = self._get_emoji("⏳", "[RETRY]")
                self.logger.info(f"{clock_emoji} Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
        
        x_emoji = self._get_emoji("❌", "[ERROR]")
        self.logger.error(f"{x_emoji} Failed to send detection data after {MAX_RETRY_ATTEMPTS} attempts")
        return False
    
    def settings_monitor_thread(self):
        """
        Background thread to monitor and update settings from the API
        """
        while not self.shutdown_event.is_set():
            try:
                self.fetch_settings_from_api()
                
                # Wait for next check or shutdown
                self.shutdown_event.wait(SETTINGS_CHECK_INTERVAL)
                
            except Exception as e:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.error(f"{x_emoji} Error in settings monitor thread: {e}")
                self.shutdown_event.wait(SETTINGS_CHECK_INTERVAL)
    
    def detection_loop_thread(self):
        """
        Main detection loop thread that generates and sends data
        """
        last_interval = self.settings.log_interval_seconds
        next_detection_time = time.time() + last_interval
        
        while not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Check if interval has changed
                if self.settings.log_interval_seconds != last_interval:
                    last_interval = self.settings.log_interval_seconds
                    next_detection_time = current_time + last_interval
                    cycle_emoji = self._get_emoji("🔄", "[UPDATE]")
                    self.logger.info(f"{cycle_emoji} Detection interval updated to {last_interval} seconds")
                
                # Wait until next detection time
                if current_time < next_detection_time:
                    sleep_time = min(1.0, next_detection_time - current_time)
                    self.shutdown_event.wait(sleep_time)
                    continue
                
                # Generate and send detection data
                detection_data = self.generate_realistic_detection_data()
                success = self.send_detection_data(detection_data)
                
                if success:
                    # Log summary of what was detected
                    male_total = sum(detection_data["detections"]["male"].values())
                    female_total = sum(detection_data["detections"]["female"].values())
                    total = male_total + female_total
                    
                    chart_emoji = self._get_emoji("📊", "[DATA]")
                    if total > 0:
                        self.logger.info(f"{chart_emoji} Generated detection: {total} people (M:{male_total}, F:{female_total})")
                    else:
                        self.logger.info(f"{chart_emoji} Generated detection: No people detected")
                
                # Schedule next detection
                next_detection_time = current_time + self.settings.log_interval_seconds
                
            except Exception as e:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.error(f"{x_emoji} Error in detection loop: {e}")
                # Wait a bit before retrying
                self.shutdown_event.wait(5)
    
    def start(self):
        """
        Start the dummy detection model
        """
        if self.running:
            warning_emoji = self._get_emoji("⚠️", "[WARNING]")
            self.logger.warning(f"{warning_emoji} Detection model is already running")
            return
        
        rocket_emoji = self._get_emoji("🚀", "[START]")
        self.logger.info(f"{rocket_emoji} Starting Dummy Detection Model...")
        
        # Test API connection
        search_emoji = self._get_emoji("🔍", "[TEST]")
        self.logger.info(f"{search_emoji} Testing API connection...")
        if not self.test_api_connection():
            x_emoji = self._get_emoji("❌", "[ERROR]")
            self.logger.error(f"{x_emoji} Failed to connect to API. Please ensure the backend is running.")
            return
        
        # Fetch initial settings
        gear_emoji = self._get_emoji("⚙️", "[SETTINGS]")
        self.logger.info(f"{gear_emoji} Fetching initial settings...")
        self.fetch_settings_from_api()
        
        self.running = True
        
        # Start background threads
        self.settings_thread = threading.Thread(target=self.settings_monitor_thread, daemon=True)
        self.detection_thread = threading.Thread(target=self.detection_loop_thread, daemon=True)
        
        self.settings_thread.start()
        self.detection_thread.start()
        
        check_emoji = self._get_emoji("✅", "[SUCCESS]")
        self.logger.info(f"{check_emoji} Dummy Detection Model started successfully")
        clipboard_emoji = self._get_emoji("📋", "[INFO]")
        self.logger.info(f"{clipboard_emoji} Current settings: Confidence Person={self.settings.confidence_threshold_person}, "
                        f"Face={self.settings.confidence_threshold_face}, Interval={self.settings.log_interval_seconds}s")
    
    def stop(self):
        """
        Stop the dummy detection model gracefully
        """
        if not self.running:
            return
        
        stop_emoji = self._get_emoji("🛑", "[STOP]")
        self.logger.info(f"{stop_emoji} Stopping Dummy Detection Model...")
        
        self.running = False
        self.shutdown_event.set()
        
        # Wait for threads to finish
        if self.settings_thread and self.settings_thread.is_alive():
            self.settings_thread.join(timeout=5)
        
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=5)
        
        check_emoji = self._get_emoji("✅", "[SUCCESS]")
        self.logger.info(f"{check_emoji} Dummy Detection Model stopped successfully")
    
    def test_api_connection(self) -> bool:
        """
        Test connection to the backend API
        """
        try:
            response = self.session.get(f"{self.api_base_url}/", timeout=10)
            if response.status_code == 200:
                check_emoji = self._get_emoji("✅", "[SUCCESS]")
                self.logger.info(f"{check_emoji} API connection successful")
                return True
            else:
                x_emoji = self._get_emoji("❌", "[ERROR]")
                self.logger.error(f"{x_emoji} API connection failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            x_emoji = self._get_emoji("❌", "[ERROR]")
            self.logger.error(f"{x_emoji} API connection failed: {e}")
            return False
    
    def run_forever(self):
        """
        Run the detection model indefinitely until interrupted
        """
        try:
            self.start()
            
            if not self.running:
                return
            
            cycle_emoji = self._get_emoji("🔄", "[RUNNING]")
            self.logger.info(f"{cycle_emoji} Detection model running. Press Ctrl+C to stop...")
            
            # Keep main thread alive
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                    
        except KeyboardInterrupt:
            fire_emoji = self._get_emoji("🔥", "[INTERRUPT]")
            self.logger.info(f"{fire_emoji} Received interrupt signal")
        finally:
            self.stop()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    fire_emoji = "🔥" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else "[SIGNAL]"
    print(f"\n{fire_emoji} Received signal {signum}. Shutting down...")
    # The main loop will handle the actual shutdown
    raise KeyboardInterrupt()

def main():
    """
    Main entry point for the dummy detection script
    """
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments (simple implementation)
    api_url = DEFAULT_API_BASE_URL
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    print("=" * 60)
    print("🤖 DUMMY LIVE DETECTION MODEL" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else "DUMMY LIVE DETECTION MODEL")
    print("=" * 60)
    print(f"📡 API URL: {api_url}" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else f"API URL: {api_url}")
    print(f"⏰ Default Interval: {DEFAULT_LOG_INTERVAL} seconds" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else f"Default Interval: {DEFAULT_LOG_INTERVAL} seconds")
    print(f"🎯 Default Person Confidence: {DEFAULT_CONFIDENCE_PERSON}" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else f"Default Person Confidence: {DEFAULT_CONFIDENCE_PERSON}")
    print(f"👤 Default Face Confidence: {DEFAULT_CONFIDENCE_FACE}" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else f"Default Face Confidence: {DEFAULT_CONFIDENCE_FACE}")
    print("-" * 60)
    print("📝 Features:" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else "Features:")
    print("  • Generates realistic age-gender detection data")
    print("  • Dynamic settings updates from frontend")
    print("  • Realistic daily/hourly patterns")
    print("  • Comprehensive logging and error handling")
    print("  • Graceful shutdown handling")
    print("-" * 60)
    print("🎮 Control this script through the frontend Settings page!" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else "Control this script through the frontend Settings page!")
    print("=" * 60)
    
    # Create and run the detection model
    model = DummyDetectionModel(api_base_url=api_url)
    model.run_forever()
    
    print("\n👋 Dummy Detection Model has been stopped. Goodbye!" if sys.stdout.encoding and 'utf' in sys.stdout.encoding.lower() else "\nDummy Detection Model has been stopped. Goodbye!")

if __name__ == "__main__":
    main()
