# Detection Model (Realtime & Dummy Simulations)

This folder contains the detection model utilities used by the TAProject web stack: realtime live-detection scripts (multiple backbones), a dummy data generator for development, lightweight integration helpers, model weights, and test scripts. The code is designed to integrate with the Django backend API and the React frontend (Settings / Dashboard / Analytics).

## Contents
- `dummytestscript.py` — Dummy detection data generator and sender (development/testing).
- `live_detection_with_api.py` — Live detection client that sends detection results to the backend API.
- `live_detection_efficientnet.py` — Live detection example using EfficientNet-lite backbone.
- `live_detection_mobilenet.py` — Live detection example using MobileNetV3 backbone.
- `live_detection_shufflenet.py` — Live detection example using ShuffleNetV2 backbone.
- `test_script.py` — Small test harness for checking detection pipeline.
- `check_webcam_ids.py` — Utility to enumerate available webcam IDs on the host.
- `create_public_settings_endpoint.py` — Helper to expose current settings for external monitoring (used by some deployments).
- `weights/` — Pretrained model weights (for inference).
- `results/` — Local output (logs, sample outputs).
- `requirements.txt` — Python dependencies for this folder.

## Purpose
This module suite provides:
- A lightweight, modular runtime for realtime person & face detection and age/gender inference.
- Tools for local development: a dummy data generator that mimics real-world patterns and integrates with the project's backend.
- Multiple example backends and model variants to experiment with accuracy/latency trade-offs.
- Easy integration points for the Django backend and React frontend via simple HTTP endpoints.

## Features
- Real-time face/person detection and simple age/gender demographics (inference-only).
- Multiple model backbones available (EfficientNet-lite, MobileNetV3, ShuffleNetV2, YOLO variants) with ready-to-use weights.
- Dummy data generator that:
  - Simulates time-of-day patterns (rush hours, lunch, night).
  - Sends JSON-formatted detection payloads to the API at configurable intervals.
  - Automatically picks up runtime settings from the backend (no restart required).
- Live-detection scripts that:
  - Capture from webcam or video source.
  - Optionally send detections to the backend API.
  - Support CPU and GPU execution (if PyTorch + CUDA available).
- Robust logging with daily log files and various log levels.
- Utilities for enumerating webcams and running quick local tests.

## Installation & Setup

Prerequisites
- Python 3.8+ (recommended 3.9/3.10)
- pip
- Optional: CUDA toolkit and GPU-compatible PyTorch if you plan to use GPU acceleration.

Install
1. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install detectionmodel dependencies
   ```bash
   cd detectionmodel
   pip install -r requirements.txt
   ```

3. Ensure the main backend is running (default expects `http://localhost:8000/api/`). See `../backend/README.md` for backend setup.

Notes
- If you will use GPU acceleration, install a matching `torch` wheel (see https://pytorch.org/get-started/locally/).
- The `weights/` directory already contains pretrained files used by the live scripts. If you add or replace weights, update file names referenced in the scripts.

## Configuration
- Scripts accept CLI overrides for API base URL and other common parameters.
- Runtime settings (confidence thresholds, logging interval) are fetched from the backend `GET /api/settings/` endpoint by default.
- Environment variables (if used) should be documented/managed in the backend `.env` and the project root. The detection scripts read their parameters from CLI args and the API; they do not depend on project root environment files directly.

## Usage

Run the dummy data generator (development)
```bash
# from project root
cd detectionmodel
python dummytestscript.py               # uses default API: http://localhost:8000/api
python dummytestscript.py http://host:8000/api
```

Run a live detection client (webcam -> backend)
```bash
# run efficientnet-based live detection to send results to backend
cd detectionmodel
python live_detection_with_api.py --model weights/efficientnet_liteb0_multi_task_best.pth --source 0 --api-url http://localhost:8000/api

# run MobileNet live detection
python live_detection_mobilenet.py --model weights/mobilenetv3_small_multi_task_best.pth --source 0

# run ShuffleNet live detection
python live_detection_shufflenet.py --model weights/shufflenetv2_multi_task_best.pth --source 0
```

Common CLI options (script-dependent)
- `--source` — webcam id or path to video file (default `0` for primary webcam).
- `--model` — path to model weights (default loaded from `weights/`).
- `--api-url` — backend API base URL for sending detection payloads.
- `--interval` / `--log-interval` — how often to send aggregated detections (seconds).
- `--confidence` — minimum detection confidence threshold (0.0 - 1.0).
- `--debug` — enable verbose logging / console output.

Example payload sent to backend (JSON)
```json
{
  "timestamp": "2025-01-06T17:10:30.123456",
  "source": "webcam-0",
  "total_people": 23,
  "detections": {
    "male": {
      "0-9": 2,
      "10-19": 5,
      "20-29": 8,
      "30-39": 6,
      "40-49": 4,
      "50+": 1
    },
    "female": {
      "0-9": 1,
      "10-19": 4,
      "20-29": 7,
      "30-39": 5,
      "40-49": 3,
      "50+": 2
    }
  },
  "meta": {
    "model": "efficientnet_liteb0_multi_task_best.pth",
    "fps": 8.6,
    "confidence_threshold": 0.5
  }
}
```

Input formats
- Live scripts: webcam (device id), RTSP/HTTP video stream, or local video file paths.
- Dummy generator: no video input; it synthesizes demographic counts.

Output formats
- JSON detection aggregates (see example above).
- Optional per-frame bounding boxes can be added by the live scripts (subject to script implementation).
- Logs: timestamped plain text in `detectionmodel/results/` by default.

## API / Integration Notes

Endpoints used (project-specific)
- GET /api/ — health check (project backend)
- GET /api/settings/ — fetch current runtime settings (confidence thresholds, intervals)
- POST /api/detections/ — submit aggregated detection payloads (JSON)

Integration tips
- The detection payloads are designed to match the backend serializer in `backend/api/serializers.py`. If you change the payload shape, update the backend serializer accordingly.
- Authentication: current dummy scripts may send unauthenticated requests. If your backend requires authentication, either:
  - Add token support to the scripts (e.g., add `--auth-token` and set HTTP `Authorization` header), or
  - Expose a trusted endpoint that accepts detection data from internal hosts.
- The live scripts include retry logic for temporary network failures. For production, deploy behind a reliable network and consider batching/queueing if the network is unstable.

## Testing

Quick checks
- Enumerate webcams:
  ```bash
  python check_webcam_ids.py
  ```

- Run the small test harness:
  ```bash
  python test_script.py
  ```

- Run the dummy data generator and verify backend receives data:
  ```bash
  python dummytestscript.py http://localhost:8000/api
  # Check backend logs or database for new detection records
  ```

Automated tests
- There are no dedicated pytest suites in this folder; most integration tests live in `backend/api/tests/`.
- For end-to-end tests: start backend + frontend, run `dummytestscript.py`, and verify the dashboard/analytics update.

## Logging & Monitoring
- Logs are written to `detectionmodel/results/` with a daily filename pattern.
- Log levels supported: INFO, WARNING, ERROR. Use `--debug` for verbose output.
- For production deployments, run the script under a process manager (systemd, supervisor, Docker) and configure log rotation.

## Performance & Production Notes
- Recommended intervals for production: 60–300 seconds aggregation to balance timeliness and resource usage.
- Use GPU (PyTorch + CUDA) for higher FPS; check `torch.cuda.is_available()` in the scripts.
- Protect API endpoints with authentication in production.
- Consider containerizing the detection scripts for easier deployment and scaling.

## Troubleshooting
- If scripts cannot connect to backend:
  - Verify backend is running (default `http://localhost:8000/api/`).
  - Check network/firewall settings.
  - Inspect logs in `detectionmodel/results/` and backend logs.
- If models fail to load:
  - Confirm `weights/` contains the correct files and that the script references the right path.
  - Confirm PyTorch version compatibility with weight files.
- If computer cannot open webcam:
  - Confirm webcam device ID with `check_webcam_ids.py`.
  - Ensure no other process is using the device.

## Contributing
- Keep model I/O stable: if you change JSON schema, update backend serializers and frontend consumers.
- Add new model weights to `weights/` and document the expected CLI name in the scripts.
- Write small, focused test scripts when adding new features.

## License & Attribution
Follow the main repository LICENSE. Pretrained weights included here may have separate licensing — check the weight file source before commercial use.

---

This README aims to provide a quick but complete onboarding for contributors and maintainers working with the detection model. For backend or frontend integration specifics, consult `../backend/README.md` and `../frontend/README.md`.
