import cv2
from ultralytics import YOLO
import numpy as np
import time
import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision.models import shufflenet_v2_x1_0
import collections 
import json 
from datetime import datetime, timedelta
import os

# --- Configuration ---
PERSON_MODEL_PATH = 'weight/yolo11n.pt'
FACE_MODEL_PATH = 'weight/yolov11n-face.pt'
AGE_GENDER_MODEL_PATH = 'weight/shufflenetv2_multi_task_best.pth' 
WEBCAM_ID = 0
OUTPUT_VIDEO_FPS = 6.0 # FPS for the output recorded video

RESULTS_DIR = "results" # Directory to store all output files

ROI_LINE_THICKNESS = 5
ROI_COLOR = (0, 255, 255)  

PERSON_BOX_COLOR = (0, 255, 0) 
FACE_BOX_COLOR = (255, 0, 0)    
AGE_GENDER_TEXT_COLOR = (0, 255, 255) 
PROCESSED_TEXT_COLOR = (255, 0, 255) 
CONFIDENCE_THRESHOLD_PERSON = 0.5
CONFIDENCE_THRESHOLD_FACE = 0.5
FPS_COLOR = (255, 255, 255) 
COUNTER_TEXT_COLOR = (255, 255, 255) 
TIME_TEXT_COLOR = (255, 255, 255) 
TEXT_PADDING = 10 # Padding for text from frame edges

AGE_GENDER_INPUT_SIZE = 224
AGE_GROUPS = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+'] 
GENDERS = ['Male', 'Female'] 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LOG_INTERVAL_SECONDS = 60  
BASE_LOG_FILE_PATH = "detection_log.json" # Base name, will be in RESULTS_DIR

# FPS Logging Configuration
WARMUP_PERIOD_SECONDS = 2.0 # Exclude first 2 seconds from overall FPS stats
EXPORT_AVERAGE_FPS_PER_SECOND = True # True to log average FPS per sec, False to log all FPS values per sec

# --- Age/Gender Model Definition ---
class ShuffleNetV2MultiTaskAgeGender(nn.Module):
    def __init__(self, num_age_groups=len(AGE_GROUPS), num_genders=len(GENDERS)):
        super(ShuffleNetV2MultiTaskAgeGender, self).__init__()
        self.backbone = shufflenet_v2_x1_0(weights=None) 
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # Updated architecture to match the saved model weights
        self.age_classifier = nn.Sequential(
            nn.Linear(num_ftrs, 512),  # 1024 -> 512
            nn.ReLU(),                                 
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(512, 256),       # 512 -> 256
            nn.ReLU(),
            nn.Dropout(p=0.2, inplace=True),                
            nn.Linear(256, num_age_groups)  # 256 -> 6
        )
        self.gender_classifier = nn.Sequential(
            nn.Linear(num_ftrs, 256),  # 1024 -> 256
            nn.ReLU(),                                  
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(256, 128),       # 256 -> 128
            nn.ReLU(),
            nn.Dropout(p=0.2, inplace=True),                 
            nn.Linear(128, num_genders)  # 128 -> 2
        )
    def forward(self, x):
        features = self.backbone(x) 
        age_logits = self.age_classifier(features) 
        gender_logits = self.gender_classifier(features)
        return age_logits, gender_logits

imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std = [0.229, 0.224, 0.225]
age_gender_preprocess = T.Compose([
    T.ToPILImage(),
    T.Resize((AGE_GENDER_INPUT_SIZE, AGE_GENDER_INPUT_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=imagenet_mean, std=imagenet_std)
])

# --- FPS Export Function ---
def export_fps_data_local(all_fps_list_filtered, fps_by_sec_log, script_start_time_val):
    print("[FPS LOG] Attempting to export FPS data...")
    
    export_data = {}
    export_data["per_second_fps_values"] = {}
    for sec, fps_values_in_sec in fps_by_sec_log.items():
        if EXPORT_AVERAGE_FPS_PER_SECOND:
            avg_fps_for_sec = sum(fps_values_in_sec) / len(fps_values_in_sec) if fps_values_in_sec else 0
            export_data["per_second_fps_values"][str(sec)] = round(avg_fps_for_sec, 2)
        else: # Log all values for that second
            export_data["per_second_fps_values"][str(sec)] = [round(f, 2) for f in fps_values_in_sec]

    if not all_fps_list_filtered:
        print("[FPS LOG] No FPS data collected (after warmup filter) to export for overall stats.")
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
    
    filename = os.path.join(RESULTS_DIR, f"fps_log_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=4)
        print(f"[FPS LOG] FPS data exported to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to export FPS data: {e}")

# --- Main Application ---
def main():
    video_writer = None
    video_output_filename = "" 

    os.makedirs(RESULTS_DIR, exist_ok=True)
    current_log_file_path = os.path.join(RESULTS_DIR, BASE_LOG_FILE_PATH)

    print("Loading models...")
    try:
        person_model = YOLO(PERSON_MODEL_PATH)
        face_model = YOLO(FACE_MODEL_PATH)
        print(f"Loading Age/Gender model from {AGE_GENDER_MODEL_PATH} onto {DEVICE}...")
        age_gender_model = ShuffleNetV2MultiTaskAgeGender()
        try:
            age_gender_model.load_state_dict(torch.load(AGE_GENDER_MODEL_PATH, map_location=DEVICE))
        except FileNotFoundError:
            print(f"ERROR: Age/Gender model file not found at {AGE_GENDER_MODEL_PATH}")
            return
        except Exception as e:
            print(f"Error loading Age/Gender model state_dict: {e}")
            return
        age_gender_model.to(DEVICE)
        age_gender_model.eval()
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    print(f"Starting webcam (ID: {WEBCAM_ID}) using cv2.CAP_DSHOW...")
    cap = cv2.VideoCapture(WEBCAM_ID, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open webcam ID {WEBCAM_ID} with cv2.CAP_DSHOW.")
        print("Trying fallback: cv2.VideoCapture(WEBCAM_ID) without backend...")
        cap = cv2.VideoCapture(WEBCAM_ID)
        if not cap.isOpened():
            print(f"Error: Could not open webcam ID {WEBCAM_ID} with default backend either.")
            return
        else:
            print(f"Webcam ID {WEBCAM_ID} opened with default backend.")
    else:
        print(f"Webcam ID {WEBCAM_ID} opened successfully with cv2.CAP_DSHOW.")

    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    video_output_filename_base = f"output_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    video_output_filename = os.path.join(RESULTS_DIR, video_output_filename_base)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video_writer = cv2.VideoWriter(video_output_filename, fourcc, OUTPUT_VIDEO_FPS, (frame_w, frame_h))
    if not video_writer.isOpened():
        print(f"Error: Could not open video writer for {video_output_filename}. Video will not be saved.")
        video_writer = None 
    else:
        print(f"Recording video to {video_output_filename} at {OUTPUT_VIDEO_FPS:.2f} FPS")

    all_frame_fps_values_for_stats = [] 
    fps_log_by_second = collections.defaultdict(list) 
    script_start_time = time.time()

    processed_track_ids = set() 
    fps_history = collections.deque(maxlen=50) 
    prev_frame_time = 0 
    new_frame_time = 0
    right_to_left_count = 0
    person_previous_side = {} 
    last_log_time = time.time()
    detected_persons_csv = []
    aggregated_detections = {
        gender.lower(): {age_group: 0 for age_group in AGE_GROUPS} for gender in GENDERS
    }
    if 'Male' in GENDERS and 'male' not in aggregated_detections:
        aggregated_detections['male'] = aggregated_detections.pop('Male'.lower(), {})
    if 'Female' in GENDERS and 'female' not in aggregated_detections:
        aggregated_detections['female'] = aggregated_detections.pop('Female'.lower(), {})

    print("Detection started. Press 'q' to quit.")

    try: 
        while True:
            try: 
                current_loop_time = time.time() 

                if current_loop_time - last_log_time >= LOG_INTERVAL_SECONDS:
                    timestamp_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    log_data = {"timestamp": timestamp_str, "detections": aggregated_detections}
                    try:
                        with open(current_log_file_path, 'a') as f: 
                            json.dump(log_data, f, indent=2)
                            f.write("\n") 
                        print(f"Logged detections to {current_log_file_path} at {timestamp_str}")
                    except Exception as log_e:
                        print(f"Error writing to log file {current_log_file_path}: {log_e}")
                    
                    aggregated_detections = {
                        gender.lower(): {age_group: 0 for age_group in AGE_GROUPS} for gender in GENDERS
                    }
                    if 'Male' in GENDERS and 'male' not in aggregated_detections:
                         aggregated_detections['male'] = aggregated_detections.pop('Male'.lower(), {})
                    if 'Female' in GENDERS and 'female' not in aggregated_detections:
                        aggregated_detections['female'] = aggregated_detections.pop('Female'.lower(), {})
                    last_log_time = current_loop_time

                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to grab frame from webcam.")
                    break

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
                
                person_results = person_model.track(frame, persist=True, classes=[0], conf=CONFIDENCE_THRESHOLD_PERSON, verbose=False)
                display_frame = frame.copy()

                active_track_ids_this_frame = set()
                if person_results and person_results[0].boxes.id is not None:
                    active_track_ids_this_frame = set(person_results[0].boxes.id.int().cpu().tolist())

                processed_track_ids.intersection_update(active_track_ids_this_frame)
                keys_to_remove_from_prev_side = [tid for tid in person_previous_side if tid not in active_track_ids_this_frame]
                for tid in keys_to_remove_from_prev_side: del person_previous_side[tid]

                cv2.line(display_frame, (ROI_X_LINE, 0), (ROI_X_LINE, frame_height), ROI_COLOR, ROI_LINE_THICKNESS)
                cv2.putText(display_frame, "ROI Line", (ROI_X_LINE + TEXT_PADDING, frame_height - (TEXT_PADDING*2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, ROI_COLOR, 2)

                avg_fps_text = f"Avg FPS: {avg_fps:.2f}"
                cv2.putText(display_frame, avg_fps_text, (TEXT_PADDING, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, FPS_COLOR, 2)
                counter_text = f"People R->L: {right_to_left_count}"
                cv2.putText(display_frame, counter_text, (TEXT_PADDING, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COUNTER_TEXT_COLOR, 2)

                # Display current time (top-right, dynamically positioned)
                current_time_str_display = datetime.now().strftime("%H:%M:%S")
                time_text_to_draw = f"Time: {current_time_str_display}"
                time_font_scale = 0.7
                time_font_thickness = 2
                (time_text_width, _), _ = cv2.getTextSize(time_text_to_draw, cv2.FONT_HERSHEY_SIMPLEX, time_font_scale, time_font_thickness)
                time_text_x_display = frame_width - time_text_width - TEXT_PADDING
                time_text_x_display = max(TEXT_PADDING, time_text_x_display) # Ensure not off-left
                cv2.putText(display_frame, time_text_to_draw, (time_text_x_display, 30), cv2.FONT_HERSHEY_SIMPLEX, time_font_scale, TIME_TEXT_COLOR, time_font_thickness)


                if person_results and len(person_results[0].boxes) > 0:
                    boxes = person_results[0].boxes.xyxy.cpu().numpy()
                    confs = person_results[0].boxes.conf.cpu().numpy()
                    track_ids = person_results[0].boxes.id.int().cpu().tolist() if person_results[0].boxes.id is not None else [None] * len(boxes)

                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, box)
                        current_track_id = track_ids[i] if track_ids else None
                        person_label = f"Person {current_track_id if current_track_id else ''} ({confs[i]:.2f})"
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), PERSON_BOX_COLOR, 2)
                        cv2.putText(display_frame, person_label, (x1, y1 - TEXT_PADDING), cv2.FONT_HERSHEY_SIMPLEX, 0.5, PERSON_BOX_COLOR, 2)

                        has_crossed_rl_this_frame = False
                        if current_track_id is not None:
                            person_center_x = (x1 + x2) / 2
                            current_actual_side = 'left' if person_center_x < ROI_X_LINE else 'right'
                            last_known_side = person_previous_side.get(current_track_id)
                            if last_known_side == 'right' and current_actual_side == 'left':
                                right_to_left_count += 1
                                has_crossed_rl_this_frame = True
                            if last_known_side != current_actual_side:
                                person_previous_side[current_track_id] = current_actual_side

                        if current_track_id is not None:
                            if has_crossed_rl_this_frame and current_track_id not in processed_track_ids:
                                processed_track_ids.add(current_track_id)
                                cv2.putText(display_frame, "R->L & CROPPING", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, PROCESSED_TEXT_COLOR, 2)
                                
                                person_crop_x1, person_crop_y1 = max(0, x1), max(0, y1)
                                person_crop_x2, person_crop_y2 = min(frame_width, x2), min(frame_height, y2)
                                
                                if person_crop_x1 < person_crop_x2 and person_crop_y1 < person_crop_y2:
                                    cropped_person_img = frame[person_crop_y1:person_crop_y2, person_crop_x1:person_crop_x2]
                                    if cropped_person_img.size != 0:
                                        face_results = face_model(cropped_person_img, conf=CONFIDENCE_THRESHOLD_FACE, verbose=False)
                                        age_gender_info = "" 
                                        for face_res in face_results: 
                                            if len(face_res.boxes) > 0:
                                                face_boxes = face_res.boxes.xyxy.cpu().numpy()
                                                face_confs = face_res.boxes.conf.cpu().numpy()
                                                fx1_rel, fy1_rel, fx2_rel, fy2_rel = map(int, face_boxes[0])
                                                face_conf = face_confs[0]
                                                # Expand the face bounding box by 20% on each side
                                                expand_ratio = 0.2
                                                w = fx2_rel - fx1_rel
                                                h = fy2_rel - fy1_rel
                                                expand_w = int(w * expand_ratio / 2)
                                                expand_h = int(h * expand_ratio / 2)
                                                exp_fx1 = max(0, fx1_rel - expand_w)
                                                exp_fy1 = max(0, fy1_rel - expand_h)
                                                exp_fx2 = min(cropped_person_img.shape[1], fx2_rel + expand_w)
                                                exp_fy2 = min(cropped_person_img.shape[0], fy2_rel + expand_h)

                                                if exp_fx1 < exp_fx2 and exp_fy1 < exp_fy2:
                                                    final_cropped_face_img = cropped_person_img[exp_fy1:exp_fy2, exp_fx1:exp_fx2]
                                                    if final_cropped_face_img.size > 0:
                                                        cv2.imshow(f"R->L Counted Face ID {current_track_id}", final_cropped_face_img)
                                                        try:
                                                            # Classification model runs on the expanded cropped face image
                                                            face_rgb = cv2.cvtColor(final_cropped_face_img, cv2.COLOR_BGR2RGB)
                                                            input_tensor = age_gender_preprocess(face_rgb).unsqueeze(0).to(DEVICE)
                                                            with torch.no_grad():
                                                                age_logits, gender_logits = age_gender_model(input_tensor)
                                                            age_pred_idx = torch.argmax(age_logits, dim=1).item()
                                                            gender_pred_idx = torch.argmax(gender_logits, dim=1).item()
                                                            predicted_age_group = AGE_GROUPS[age_pred_idx]
                                                            predicted_gender = GENDERS[gender_pred_idx]
                                                            age_gender_info = f"Age: {predicted_age_group}, Gender: {predicted_gender}"
                                                            print(f"Track ID {current_track_id} (R->L Counted): {age_gender_info}")
                                                            try:
                                                                gender_key = predicted_gender.lower()
                                                                if gender_key in aggregated_detections and predicted_age_group in aggregated_detections[gender_key]:
                                                                    aggregated_detections[gender_key][predicted_age_group] += 1
                                                                else:
                                                                    print(f"Warning: Could not log detection for {gender_key}, {predicted_age_group}.")
                                                                # Save to CSV buffer
                                                                detected_persons_csv.append({
                                                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                    "track_id": current_track_id,
                                                                    "age_group": predicted_age_group,
                                                                    "gender": predicted_gender
                                                                })
                                                            except Exception as agg_e:
                                                                print(f"Error updating aggregated_detections: {agg_e}")
                                                        except Exception as ag_e:
                                                            print(f"Error during Age/Gender detection for track ID {current_track_id}: {ag_e}")
                                                            age_gender_info = "Age/Gender: Error"
                                                    else: age_gender_info = ""
                                                else: age_gender_info = ""
                                                # Draw the expanded face box on the display frame
                                                abs_exp_fx1 = person_crop_x1 + exp_fx1
                                                abs_exp_fy1 = person_crop_y1 + exp_fy1
                                                abs_exp_fx2 = person_crop_x1 + exp_fx2
                                                abs_exp_fy2 = person_crop_y1 + exp_fy2
                                                cv2.rectangle(display_frame, (abs_exp_fx1, abs_exp_fy1), (abs_exp_fx2, abs_exp_fy2), FACE_BOX_COLOR, 2)
                                                face_label_text = f"Face ({face_conf:.2f})"
                                                if age_gender_info: face_label_text += f" {age_gender_info}"
                                                text_y_pos = abs_exp_fy1 - TEXT_PADDING
                                                if text_y_pos < TEXT_PADDING : text_y_pos = abs_exp_fy1 + TEXT_PADDING + 5 # adjust if too high
                                                cv2.putText(display_frame, face_label_text, (abs_exp_fx1, text_y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.4, AGE_GENDER_TEXT_COLOR, 1) 
                                                break 
                                else: print(f"Warning: Cropped person image is empty for track ID {current_track_id}.")
                            elif current_track_id in processed_track_ids:
                                cv2.putText(display_frame, "Processed (R->L)", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128,128,128), 2)
                
                if video_writer:
                    video_writer.write(display_frame)

                cv2.imshow("Webcam Feed - Person and Face Detection", display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("'q' pressed, exiting...")
                    break
            
            except KeyboardInterrupt:
                print("KeyboardInterrupt detected, exiting...")
                break 
            except Exception as e:
                print(f"An error occurred in the main loop: {e}")
                import traceback
                traceback.print_exc()

    finally: 
        print("Releasing resources...")
        # Export detected persons to CSV
        if detected_persons_csv:
            import csv
            csv_filename = os.path.join(RESULTS_DIR, f"detected_persons_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=["timestamp", "track_id", "age_group", "gender"])
                    writer.writeheader()
                    writer.writerows(detected_persons_csv)
                print(f"Detected persons (age/gender) exported to {csv_filename}")
            except Exception as e:
                print(f"Error exporting detected persons CSV: {e}")

        if video_writer:
            print(f"Releasing video writer. Output saved to {video_output_filename}")
            video_writer.release()
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            print("Webcam released.")
        cv2.destroyAllWindows()
        print("OpenCV windows destroyed.")
        
        export_fps_data_local(all_frame_fps_values_for_stats, fps_log_by_second, script_start_time)
        
        print("Application terminated.")

if __name__ == "__main__":
    print("Reminder: Ensure you have 'ultralytics', 'opencv-python', 'torch', and 'torchvision' installed.")
    print("You can install them using: pip install ultralytics opencv-python torch torchvision")
    print("Ensure your model files (yolo11n.pt, yolov11n-face.pt, shufflenetv2_multi_task_best.pth) are in the 'weight' directory.")
    main()
