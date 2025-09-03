import cv2
from ultralytics import YOLO
import numpy as np
import time
import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_small
import collections
import json
import requests
from datetime import datetime
import logging
import sys
import threading
import signal
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os

# --- Configuration Constants ---
PERSON_MODEL_PATH = 'weight/yolov11n.pt'
FACE_MODEL_PATH = 'weight/yolov11n-face.pt'
AGE_GENDER_MODEL_PATH = 'weight/mobilenetv3_small_multi_task_best.pth'
WEBCAM_ID = 0

RESULTS_DIR = "results" # Directory to store all output files
TEXT_PADDING = 10 # Padding for text from frame edges

# API Configuration
DEFAULT_API_BASE_URL = "http://localhost:8000/api"
API_TIMEOUT_SECONDS = 10
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5

# Default Model Settings
DEFAULT_CONFIDENCE_PERSON = 0.5
DEFAULT_CONFIDENCE_FACE = 0.5
DEFAULT_SEND_INTERVAL_SECONDS = 60
SETTINGS_CHECK_INTERVAL_SECONDS = 30

# ROI Line configuration
ROI_LINE_THICKNESS = 5
ROI_COLOR = (0, 255, 255)

PERSON_BOX_COLOR = (0, 255, 0)
FACE_BOX_COLOR = (255, 0, 0)
AGE_GENDER_TEXT_COLOR = (0, 255, 255)
PROCESSED_TEXT_COLOR = (255, 0, 255)
FPS_COLOR = (255, 255, 255)
COUNTER_TEXT_COLOR = (255, 255, 255)
TIME_TEXT_COLOR = (255, 255, 255) # Added for consistency, though FPS_COLOR was used for time

AGE_GENDER_INPUT_SIZE = 224
AGE_GROUPS = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']
GENDERS = ['Male', 'Female']
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_LOCAL_LOG_FILE_PATH = "live_detection_api_backup_log.json" 
# Actual path will be os.path.join(RESULTS_DIR, BASE_LOCAL_LOG_FILE_PATH)

# FPS Logging Configuration
WARMUP_PERIOD_SECONDS = 2.0 # Exclude first 2 seconds from overall FPS stats
EXPORT_AVERAGE_FPS_PER_SECOND = True # True to log average FPS per sec, False to log all FPS values per sec

# --- Global Variables ---
logger: Optional[logging.Logger] = None
http_session: Optional[requests.Session] = None
shutdown_event = threading.Event()
LOG_FILE_PATH = "" 

@dataclass
class ModelSettings:
    confidence_threshold_person: float = DEFAULT_CONFIDENCE_PERSON
    confidence_threshold_face: float = DEFAULT_CONFIDENCE_FACE
    log_interval_seconds: int = DEFAULT_SEND_INTERVAL_SECONDS
    last_updated: Optional[str] = None

    def __post_init__(self):
        if not (0.0 <= self.confidence_threshold_person <= 1.0):
            self.confidence_threshold_person = DEFAULT_CONFIDENCE_PERSON
        if not (0.0 <= self.confidence_threshold_face <= 1.0):
            self.confidence_threshold_face = DEFAULT_CONFIDENCE_FACE
        if not (1 <= self.log_interval_seconds <= 3600):
            self.log_interval_seconds = DEFAULT_SEND_INTERVAL_SECONDS

current_settings = ModelSettings()

def setup_paths_and_logging():
    global logger, LOG_FILE_PATH
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    LOG_FILE_PATH = os.path.join(RESULTS_DIR, BASE_LOCAL_LOG_FILE_PATH)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    script_log_file_base = f"live_detection_api_script_{datetime.now().strftime('%Y%m%d')}.log"
    script_log_file = os.path.join(RESULTS_DIR, script_log_file_base)
    
    try:
        file_handler = logging.FileHandler(script_log_file, encoding='utf-8')
    except Exception:
        file_handler = logging.FileHandler(script_log_file) 
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    logger = logging.getLogger("LiveDetectionModelAPI")
    logger.setLevel(logging.INFO)
    logger.handlers.clear() 
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False 
    
    logger.info(f"[INFO] Results will be saved in: {os.path.abspath(RESULTS_DIR)}")
    logger.info(f"[INFO] Script log file: {script_log_file}")
    logger.info(f"[INFO] Local detection backup log: {LOG_FILE_PATH}")
    logger.info("[INFO] Live Detection Script Logger Initialized.")

class MobileNetV3MultiTaskAgaGender(nn.Module):
    def __init__(self, num_age_groups=len(AGE_GROUPS), num_genders=len(GENDERS)):
        super(MobileNetV3MultiTaskAgaGender, self).__init__()
        self.backbone = mobilenet_v3_small(weights=None)
        num_ftrs = self.backbone.classifier[0].in_features
        self.backbone.classifier = nn.Identity()
        self.age_classifier = nn.Sequential(
            nn.Linear(num_ftrs, 256), nn.Hardswish(),
            nn.Dropout(p=0.2, inplace=True), nn.Linear(256, num_age_groups)
        )
        self.gender_classifier = nn.Sequential(
            nn.Linear(num_ftrs, 128), nn.Hardswish(),
            nn.Dropout(p=0.2, inplace=True), nn.Linear(128, num_genders)
        )
    def forward(self, x):
        features = self.backbone(x)
        return self.age_classifier(features), self.gender_classifier(features)

imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std = [0.229, 0.224, 0.225]
age_gender_preprocess = T.Compose([
    T.ToPILImage(), T.Resize((AGE_GENDER_INPUT_SIZE, AGE_GENDER_INPUT_SIZE)),
    T.ToTensor(), T.Normalize(mean=imagenet_mean, std=imagenet_std)
])

def fetch_settings_from_api(api_base_url: str) -> bool:
    global current_settings, logger, http_session
    if not logger or not http_session: return False
    settings_url = f"{api_base_url.rstrip('/')}/public-settings/"
    try:
        response = http_session.get(settings_url, timeout=API_TIMEOUT_SECONDS)
        if response.status_code == 200:
            data = response.json()
            old_settings_tuple = (current_settings.confidence_threshold_person, current_settings.confidence_threshold_face, current_settings.log_interval_seconds)
            current_settings = ModelSettings(
                confidence_threshold_person=data.get('confidence_threshold_person', DEFAULT_CONFIDENCE_PERSON),
                confidence_threshold_face=data.get('confidence_threshold_face', DEFAULT_CONFIDENCE_FACE),
                log_interval_seconds=data.get('log_interval_seconds', DEFAULT_SEND_INTERVAL_SECONDS),
                last_updated=data.get('last_updated')
            )
            new_settings_tuple = (current_settings.confidence_threshold_person, current_settings.confidence_threshold_face, current_settings.log_interval_seconds)
            if old_settings_tuple != new_settings_tuple:
                logger.info(f"[SETTINGS] Settings updated: PersonConf={current_settings.confidence_threshold_person}, FaceConf={current_settings.confidence_threshold_face}, Interval={current_settings.log_interval_seconds}s")
            return True
        else:
            logger.warning(f"[WARN] Failed to fetch settings: HTTP {response.status_code}. Using current/default settings.")
    except requests.exceptions.RequestException as e:
        logger.error(f"[ERROR] Error fetching settings: {e}. Using current/default settings.")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error fetching settings: {e}. Using current/default settings.")
    return False

def settings_monitor_thread_func(api_base_url: str):
    global logger
    if not logger: return
    logger.info("[INFO] Settings monitor thread started.")
    while not shutdown_event.is_set():
        fetch_settings_from_api(api_base_url)
        shutdown_event.wait(SETTINGS_CHECK_INTERVAL_SECONDS)
    logger.info("[INFO] Settings monitor thread stopped.")

def send_data_to_api(api_base_url: str, data: Dict[str, Any]) -> bool:
    global logger, http_session
    if not logger or not http_session: return False
    api_endpoint = f"{api_base_url.rstrip('/')}/detections/"
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            response = http_session.post(api_endpoint, json=data, timeout=API_TIMEOUT_SECONDS)
            if response.status_code == 201:
                total_detected = sum(data["detections"]["male"].values()) + sum(data["detections"]["female"].values())
                logger.info(f"[SUCCESS] Data sent to API: {total_detected} people. Msg: {response.json().get('message', 'OK')}")
                return True
            else:
                logger.warning(f"[WARN] API send failed (Attempt {attempt+1}/{MAX_RETRY_ATTEMPTS}): HTTP {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Network error sending data (Attempt {attempt+1}/{MAX_RETRY_ATTEMPTS}): {e}")
        if attempt < MAX_RETRY_ATTEMPTS - 1:
            logger.info(f"[RETRY] Retrying in {RETRY_DELAY_SECONDS}s...")
            shutdown_event.wait(RETRY_DELAY_SECONDS) 
            if shutdown_event.is_set(): return False 
    logger.error(f"[ERROR] Failed to send data after {MAX_RETRY_ATTEMPTS} attempts.")
    return False

def save_data_locally(data: Dict[str, Any]):
    global logger, LOG_FILE_PATH
    if not logger: return
    if not LOG_FILE_PATH: 
        logger.error("[ERROR] LOG_FILE_PATH not set for save_data_locally.")
        return
    try:
        with open(LOG_FILE_PATH, 'a') as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        logger.info(f"[INFO] Detection data saved locally to {LOG_FILE_PATH}")
    except Exception as e:
        logger.error(f"[ERROR] Failed to save data locally: {e}")

def export_fps_data(all_fps_list_filtered, fps_by_sec_log, script_start_time_val, loggr_val):
    if not loggr_val:
        print("[WARN] Logger not available for FPS export.")
        return

    export_data = {}
    export_data["per_second_fps_values"] = {}
    for sec, fps_values_in_sec in fps_by_sec_log.items():
        if EXPORT_AVERAGE_FPS_PER_SECOND:
            avg_fps_for_sec = sum(fps_values_in_sec) / len(fps_values_in_sec) if fps_values_in_sec else 0
            export_data["per_second_fps_values"][str(sec)] = round(avg_fps_for_sec, 2)
        else: 
            export_data["per_second_fps_values"][str(sec)] = [round(f, 2) for f in fps_values_in_sec]
    
    if not all_fps_list_filtered:
        loggr_val.info("[FPS LOG] No FPS data collected (after warmup filter) to export for overall stats.")
    else:
        all_fps_list_filtered.sort() 
        one_percent_low_idx = int(len(all_fps_list_filtered) * 0.01)
        
        export_data["one_percent_low_fps"] = round(all_fps_list_filtered[one_percent_low_idx], 2) if len(all_fps_list_filtered) > one_percent_low_idx else (round(all_fps_list_filtered[0], 2) if all_fps_list_filtered else 0)
        export_data["overall_average_fps"] = round(sum(all_fps_list_filtered) / len(all_fps_list_filtered), 2) if all_fps_list_filtered else 0
        export_data["median_fps"] = round(all_fps_list_filtered[len(all_fps_list_filtered) // 2], 2) if all_fps_list_filtered else 0
        export_data["max_fps"] = round(max(all_fps_list_filtered), 2) if all_fps_list_filtered else 0
        export_data["min_fps"] = round(min(all_fps_list_filtered), 2) if all_fps_list_filtered else 0
        export_data["total_frames_processed_for_stats"] = len(all_fps_list_filtered)
    
    export_data["total_duration_seconds"] = round(time.time() - script_start_time_val, 2)
    export_data["warmup_period_excluded_seconds"] = WARMUP_PERIOD_SECONDS
    export_data["per_second_fps_log_mode"] = "average" if EXPORT_AVERAGE_FPS_PER_SECOND else "all_values"
    
    filename_base = f"fps_log_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filename = os.path.join(RESULTS_DIR, filename_base)
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=4)
        loggr_val.info(f"[FPS LOG] FPS data exported to {filename}")
    except Exception as e:
        loggr_val.error(f"[ERROR] Failed to export FPS data: {e}")

def main_detection_loop(api_base_url: str):
    global logger, current_settings, shutdown_event
    if not logger:
        print("Logger not initialized. Exiting.")
        return

    all_frame_fps_values_for_stats = [] 
    fps_log_by_second = collections.defaultdict(list) 
    script_start_time = time.time() 

    logger.info("[INFO] Loading models...")
    try:
        person_model = YOLO(PERSON_MODEL_PATH)
        face_model = YOLO(FACE_MODEL_PATH)
        age_gender_model = MobileNetV3MultiTaskAgaGender().to(DEVICE)
        age_gender_model.load_state_dict(torch.load(AGE_GENDER_MODEL_PATH, map_location=DEVICE))
        age_gender_model.eval()
        logger.info(f"[INFO] Models loaded successfully. Using device: {DEVICE}")
    except FileNotFoundError as e:
        logger.error(f"[ERROR] Model file not found: {e}. Please check paths.")
        return
    except Exception as e:
        logger.error(f"[ERROR] Error loading models: {e}")
        return

    logger.info(f"[INFO] Starting webcam (ID: {WEBCAM_ID}) using cv2.CAP_DSHOW...")
    cap = cv2.VideoCapture(WEBCAM_ID, cv2.CAP_DSHOW)
    if not cap.isOpened():
        logger.error(f"[ERROR] Could not open webcam ID {WEBCAM_ID} with cv2.CAP_DSHOW.")
        logger.info("[INFO] Trying fallback: cv2.VideoCapture(WEBCAM_ID) without backend...")
        cap = cv2.VideoCapture(WEBCAM_ID)
        if not cap.isOpened():
            logger.error(f"[ERROR] Could not open webcam ID {WEBCAM_ID} with default backend either.")
            return
        else:
            logger.info(f"[INFO] Webcam ID {WEBCAM_ID} opened with default backend.")
    else:
        logger.info(f"[INFO] Webcam ID {WEBCAM_ID} opened successfully with cv2.CAP_DSHOW.")

    processed_track_ids = set()
    fps_history = collections.deque(maxlen=50)
    prev_frame_time = 0
    left_to_right_count = 0
    person_previous_side = {}
    last_send_time = time.time()
    aggregated_detections = {'male': {ag: 0 for ag in AGE_GROUPS}, 'female': {ag: 0 for ag in AGE_GROUPS}}

    logger.info("[INFO] Detection started. Press 'q' in OpenCV window to quit.")
    logger.info(f"Initial settings: PersonConf={current_settings.confidence_threshold_person}, FaceConf={current_settings.confidence_threshold_face}, Interval={current_settings.log_interval_seconds}s")

    try: 
        while not shutdown_event.is_set():
            try: 
                loop_start_time = time.time()

                if loop_start_time - last_send_time >= current_settings.log_interval_seconds:
                    timestamp_str = datetime.now().isoformat()
                    api_data = {"timestamp": timestamp_str, "detections": aggregated_detections}
                    logger.info(f"[SENDING] Sending aggregated data. Current: {aggregated_detections}")
                    api_success = send_data_to_api(api_base_url, api_data)
                    save_data_locally(api_data) 
                    if api_success:
                        logger.info(f"[SENT] Data transmission completed at {timestamp_str}")
                    else:
                        logger.warning("[WARN] API transmission failed, data saved locally.")
                    aggregated_detections = {'male': {ag: 0 for ag in AGE_GROUPS}, 'female': {ag: 0 for ag in AGE_GROUPS}}
                    last_send_time = loop_start_time
                    logger.info("[RESET] Detection counters reset for next interval.")

                ret, frame = cap.read()
                if not ret:
                    logger.warning("[WARN] Failed to grab frame from webcam.")
                    shutdown_event.wait(0.1) 
                    if shutdown_event.is_set(): break
                    continue

                frame_height, frame_width = frame.shape[:2]
                ROI_X_LINE = frame_width // 2

                new_frame_time = time.time()
                fps = 1 / (new_frame_time - prev_frame_time) if (new_frame_time - prev_frame_time) > 0 else 0
                prev_frame_time = new_frame_time
                fps_history.append(fps)
                avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0

                current_elapsed_second = int(time.time() - script_start_time)
                fps_log_by_second[current_elapsed_second].append(fps)
                
                if (time.time() - script_start_time) > WARMUP_PERIOD_SECONDS:
                    all_frame_fps_values_for_stats.append(fps)
                
                person_results = person_model.track(frame, persist=True, classes=[0], conf=current_settings.confidence_threshold_person, verbose=False)
                display_frame = frame.copy()

                active_track_ids_this_frame = set()
                if person_results and person_results[0].boxes.id is not None:
                    active_track_ids_this_frame = set(person_results[0].boxes.id.int().cpu().tolist())

                processed_track_ids.intersection_update(active_track_ids_this_frame)
                keys_to_remove_from_prev_side = [tid for tid in person_previous_side if tid not in active_track_ids_this_frame]
                for tid in keys_to_remove_from_prev_side: del person_previous_side[tid]

                cv2.line(display_frame, (ROI_X_LINE, 0), (ROI_X_LINE, frame_height), ROI_COLOR, ROI_LINE_THICKNESS)
                cv2.putText(display_frame, f"Avg FPS: {avg_fps:.2f}", (TEXT_PADDING, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, FPS_COLOR, 2)
                cv2.putText(display_frame, f"L->R Count: {left_to_right_count}", (TEXT_PADDING, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COUNTER_TEXT_COLOR, 2)
                total_agg = sum(aggregated_detections['male'].values()) + sum(aggregated_detections['female'].values())
                cv2.putText(display_frame, f"Aggregated: {total_agg}", (TEXT_PADDING, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COUNTER_TEXT_COLOR, 2)
                time_until_send = current_settings.log_interval_seconds - (loop_start_time - last_send_time)
                cv2.putText(display_frame, f"Next Send: {max(0, time_until_send):.0f}s", (TEXT_PADDING, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COUNTER_TEXT_COLOR, 2)
                
                # Display current time (top-right, dynamically positioned)
                current_time_str = datetime.now().strftime("%H:%M:%S")
                time_text_to_draw = f"Time: {current_time_str}"
                time_font_scale = 0.7
                time_font_thickness = 2
                (time_text_width, _), _ = cv2.getTextSize(time_text_to_draw, cv2.FONT_HERSHEY_SIMPLEX, time_font_scale, time_font_thickness)
                time_text_x = frame_width - time_text_width - TEXT_PADDING
                time_text_x = max(TEXT_PADDING, time_text_x) # Ensure not off-left
                cv2.putText(display_frame, time_text_to_draw, (time_text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, time_font_scale, TIME_TEXT_COLOR, time_font_thickness)


                if person_results and len(person_results[0].boxes) > 0:
                    boxes = person_results[0].boxes.xyxy.cpu().numpy()
                    confs = person_results[0].boxes.conf.cpu().numpy()
                    track_ids = person_results[0].boxes.id.int().cpu().tolist() if person_results[0].boxes.id is not None else [None] * len(boxes)

                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, box)
                        current_track_id = track_ids[i]
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), PERSON_BOX_COLOR, 2)
                        cv2.putText(display_frame, f"P {current_track_id if current_track_id else ''} ({confs[i]:.2f})", (x1, y1 - TEXT_PADDING), cv2.FONT_HERSHEY_SIMPLEX, 0.5, PERSON_BOX_COLOR, 2)
                        has_crossed_lr_this_frame = False
                        if current_track_id is not None:
                            person_center_x = (x1 + x2) / 2
                            current_side = 'left' if person_center_x < ROI_X_LINE else 'right'
                            last_side = person_previous_side.get(current_track_id)
                            if last_side == 'left' and current_side == 'right':
                                left_to_right_count += 1
                                has_crossed_lr_this_frame = True
                            if last_side != current_side: person_previous_side[current_track_id] = current_side
                        if current_track_id is not None and has_crossed_lr_this_frame and current_track_id not in processed_track_ids:
                            processed_track_ids.add(current_track_id)
                            person_crop = frame[max(0, y1):min(frame_height, y2), max(0, x1):min(frame_width, x2)]
                            if person_crop.size > 0:
                                face_results_crop = face_model(person_crop, conf=current_settings.confidence_threshold_face, verbose=False)
                                age_gender_info_str = ""
                                if face_results_crop and len(face_results_crop[0].boxes) > 0:
                                    face_box_rel = face_results_crop[0].boxes.xyxy.cpu().numpy()[0]
                                    face_conf_rel = face_results_crop[0].boxes.conf.cpu().numpy()[0]
                                    fx1_r, fy1_r, fx2_r, fy2_r = map(int, face_box_rel)
                                    final_face_crop = person_crop[max(0, fy1_r):min(person_crop.shape[0], fy2_r), max(0, fx1_r):min(person_crop.shape[1], fx2_r)]
                                    if final_face_crop.size > 0:
                                        try:
                                            face_rgb = cv2.cvtColor(final_face_crop, cv2.COLOR_BGR2RGB)
                                            input_tensor = age_gender_preprocess(face_rgb).unsqueeze(0).to(DEVICE)
                                            with torch.no_grad():
                                                age_logits, gender_logits = age_gender_model(input_tensor)
                                            age_idx = torch.argmax(age_logits, dim=1).item()
                                            gender_idx = torch.argmax(gender_logits, dim=1).item()
                                            pred_age_group = AGE_GROUPS[age_idx]
                                            pred_gender = GENDERS[gender_idx].lower()
                                            age_gender_info_str = f"A:{pred_age_group} G:{pred_gender.capitalize()}"
                                            logger.info(f"[DETECTED] TrackID {current_track_id} (L->R): {age_gender_info_str}")
                                            if pred_gender in aggregated_detections and pred_age_group in aggregated_detections[pred_gender]:
                                                aggregated_detections[pred_gender][pred_age_group] += 1
                                            else:
                                                logger.warning(f"[WARN] Invalid gender/age key for aggregation: {pred_gender}, {pred_age_group}")
                                        except Exception as ag_e:
                                            logger.error(f"[ERROR] Age/Gender processing error for TrackID {current_track_id}: {ag_e}")
                                            age_gender_info_str = "Age/Gender: Error"
                                    abs_fx1, abs_fy1 = x1 + fx1_r, y1 + fy1_r
                                    abs_fx2, abs_fy2 = x1 + fx2_r, y1 + fy2_r
                                    cv2.rectangle(display_frame, (abs_fx1, abs_fy1), (abs_fx2, abs_fy2), FACE_BOX_COLOR, 1)
                                    text_y = abs_fy1 - 5 if abs_fy1 > 15 else abs_fy1 + 15 # Simple y adjustment
                                    cv2.putText(display_frame, f"Face ({face_conf_rel:.2f}) {age_gender_info_str}", (abs_fx1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, AGE_GENDER_TEXT_COLOR, 1)
                        elif current_track_id in processed_track_ids:
                             cv2.putText(display_frame, "Processed", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128,128,128), 1)

                cv2.imshow("Live Age-Gender Detection & API Integration", display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("[STOP] 'q' pressed, initiating shutdown.")
                    shutdown_event.set()
                    break 
            except KeyboardInterrupt:
                logger.info("[STOP] KeyboardInterrupt (inner loop), initiating shutdown.")
                shutdown_event.set()
                break 
            except Exception as e:
                logger.error(f"[CRITICAL] Unhandled error in one loop iteration: {e}", exc_info=True)
                shutdown_event.wait(1) 
                if shutdown_event.is_set(): break
    finally:
        logger.info("[INFO] Main detection loop ending. Releasing resources and exporting FPS data...")
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            logger.info("[INFO] Webcam released.")
        cv2.destroyAllWindows()
        logger.info("[INFO] OpenCV windows destroyed.")
        export_fps_data(all_frame_fps_values_for_stats, fps_log_by_second, script_start_time, logger)
        logger.info("[INFO] Application terminated from main_detection_loop.")

def signal_handler_func(signum, frame):
    global logger, shutdown_event
    if logger:
        logger.info(f"[SIGNAL] Signal {signum} received. Initiating graceful shutdown...")
    else:
        print(f"Signal {signum} received. Initiating graceful shutdown...")
    shutdown_event.set()

if __name__ == "__main__":
    setup_paths_and_logging() 
    if not logger:
        print("FATAL: Logger setup failed. Exiting.")
        sys.exit(1)
    
    http_session = requests.Session()
    http_session.headers.update({'Content-Type': 'application/json', 'User-Agent': 'LiveDetectionModel/1.3.1'}) # Minor patch version bump
    api_url_to_use = DEFAULT_API_BASE_URL
    
    logger.info("[INIT] Live Age-Gender Detection with API Integration")
    logger.info("=" * 60)
    logger.info("Reminder: Ensure required packages are installed.")
    logger.info("Ensure model files are in the 'weight' directory.")
    logger.info(f"Django backend should be running, API base: {api_url_to_use}")
    logger.info("=" * 60)
    
    signal.signal(signal.SIGINT, signal_handler_func)
    signal.signal(signal.SIGTERM, signal_handler_func)
    
    logger.info("[INIT] Fetching initial model settings...")
    fetch_settings_from_api(api_url_to_use) 
    
    settings_thread = threading.Thread(target=settings_monitor_thread_func, args=(api_url_to_use,), daemon=True)
    settings_thread.start()
    
    try:
        main_detection_loop(api_url_to_use)
    except Exception as e: 
        if logger:
            logger.critical(f"[CRITICAL] Unhandled exception in __main__: {e}", exc_info=True)
        else:
            print(f"CRITICAL Unhandled exception in __main__: {e}")
    finally:
        if settings_thread.is_alive():
            logger.info("[SHUTDOWN] Waiting for settings thread to stop...")
            shutdown_event.set() 
            settings_thread.join(timeout=SETTINGS_CHECK_INTERVAL_SECONDS + 2) 
            if settings_thread.is_alive():
                 logger.warning("[SHUTDOWN] Settings thread did not stop in time.")
        if http_session:
            http_session.close()
            logger.info("[SHUTDOWN] HTTP session closed.")
        logger.info("[SHUTDOWN] Main execution block finished.")
