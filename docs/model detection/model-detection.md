# Model Detection Documentation

This document provides comprehensive information about the object detection model integration components of the YOLO People Counter Web Interface.

## Overview

The model detection system integrates computer vision algorithms with the web interface to provide real-time people counting and demographic analysis. The system is designed to work with various object detection models, primarily YOLO (You Only Look Once), but can be adapted for other models as well.

## Directory Structure

```
detectionmodel/
├── dummytestscript.py      # Simulation script for testing
├── live_detection.py       # Real YOLO integration template
├── live_detection_with_api.py  # Complete integration with API communication
├── live_detection_mobilenet.py  # MobileNet-SSD implementation
├── live_detection_shufflenet.py  # ShuffleNet implementation
├── live_detection_efficientnet.py  # EfficientNet implementation
├── live_detection_with_api_mobilenet.py  # MobileNet with API integration
├── utils/                  # Utility functions
│   ├── camera.py          # Camera handling utilities
│   ├── visualization.py   # Visualization helpers
│   └── preprocessing.py   # Image preprocessing functions
├── models/                # Pre-trained models
│   ├── yolov5s.pt         # YOLOv5 small model
│   ├── yolov5m.pt         # YOLOv5 medium model
│   └── mobilenet_v2.pth   # MobileNet V2 model
├── config/                # Configuration files
│   └── model_config.json  # Model configuration parameters
└── README.md             # Model integration guide
```

## Core Components

### 1. Dummy Test Script (`dummytestscript.py`)
A simulation script that generates synthetic detection data for testing purposes.

**Features**:
- Generates realistic demographic data
- Simulates real-time data streaming
- Configurable parameters
- API integration for data submission

**Usage**:
```bash
cd detectionmodel
python dummytestscript.py
```

**Configuration**:
- `API_URL`: Backend API endpoint
- `INTERVAL`: Data generation interval (seconds)
- `CONFIDENCE_THRESHOLD`: Minimum confidence for detections

### 2. Live Detection Template (`live_detection.py`)
Template for integrating real YOLO models with camera input.

**Features**:
- Camera input handling
- YOLO model integration
- Real-time processing
- Visualization capabilities

**Usage**:
```bash
cd detectionmodel
python live_detection.py
```

**Dependencies**:
- OpenCV for camera handling
- PyTorch for YOLO model
- NumPy for numerical operations

### 3. Live Detection with API (`live_detection_with_api.py`)
Complete implementation that integrates YOLO detection with API data submission.

**Features**:
- Real-time detection and counting
- Age and gender classification
- API data submission
- Performance monitoring
- Error handling and retry logic

**Usage**:
```bash
cd detectionmodel
python live_detection_with_api.py
```

**Configuration**:
- `API_URL`: Backend API endpoint
- `CAMERA_INDEX`: Camera input index
- `MODEL_PATH`: Path to YOLO model file
- `CONFIDENCE_THRESHOLD`: Minimum confidence threshold
- `LOG_INTERVAL`: Interval for data logging

## Model Implementations

### YOLOv5 Implementation
The primary implementation uses YOLOv5 for object detection.

**Features**:
- Real-time object detection
- High accuracy for people counting
- Age and gender classification
- Multiple model size options (small, medium, large)

**Model Files**:
- `yolov5s.pt`: Small model (fastest, lower accuracy)
- `yolov5m.pt`: Medium model (balanced speed/accuracy)
- `yolov5l.pt`: Large model (slowest, highest accuracy)

### MobileNet-SSD Implementation
Alternative implementation using MobileNet-SSD for edge devices.

**Features**:
- Lightweight model for edge deployment
- Lower computational requirements
- Good performance on mobile devices
- Faster inference on CPU

**Usage**:
```bash
cd detectionmodel
python live_detection_mobilenet.py
```

### ShuffleNet Implementation
Efficient implementation using ShuffleNet architecture.

**Features**:
- Extremely lightweight
- Pointwise group convolutions
- Good accuracy with low computational cost
- Ideal for resource-constrained environments

### EfficientNet Implementation
Implementation using EfficientNet for optimal accuracy-efficiency tradeoff.

**Features**:
- Compound scaling method
- Better accuracy than MobileNet
- Efficient parameter usage
- Good for deployment with limited resources

## Data Flow Architecture

### Real-time Processing Pipeline
1. **Camera Input**: Capture video frames from camera
2. **Preprocessing**: Resize and normalize images
3. **Object Detection**: Run YOLO model on frames
4. **Classification**: Apply age/gender classification
5. **Aggregation**: Aggregate detections over time intervals
6. **API Submission**: Send data to backend API
7. **Visualization**: Display real-time results

### Data Format
The detection system generates data in the following format:
```json
{
  "timestamp": "2025-01-23T14:30:00Z",
  "male_0_9": 1,
  "male_10_19": 2,
  "male_20_29": 3,
  "male_30_39": 2,
  "male_40_49": 1,
  "male_50_plus": 0,
  "female_0_9": 0,
  "female_10_19": 1,
  "female_20_29": 2,
  "female_30_39": 3,
  "female_40_49": 1,
  "female_50_plus": 1
}
```

## Integration with Backend API

### API Communication
The detection system communicates with the backend using RESTful endpoints:

1. **Data Submission**: `POST /api/detections/`
2. **Settings Retrieval**: `GET /api/public-settings/`
3. **Health Check**: `GET /api/health/`

### Authentication
- Uses API keys or JWT tokens for secure communication
- Automatic token refresh for long-running processes
- Secure credential storage

### Error Handling
- Retry mechanisms for failed API requests
- Exponential backoff for connection issues
- Local data buffering during outages
- Detailed error logging

## Configuration

### Environment Variables
```bash
# API Configuration
API_URL=http://localhost:8000/api
API_KEY=your_api_key_here

# Camera Settings
CAMERA_INDEX=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# Model Configuration
MODEL_PATH=models/yolov5s.pt
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.45

# Processing Settings
LOG_INTERVAL=60  # seconds
BATCH_SIZE=1
```

### Model Configuration File (`config/model_config.json`)
```json
{
  "yolo": {
    "model_path": "models/yolov5s.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "image_size": 640
  },
  "classification": {
    "age_model_path": "models/age_classifier.pth",
    "gender_model_path": "models/gender_classifier.pth",
    "confidence_threshold": 0.7
  },
  "processing": {
    "log_interval": 60,
    "batch_size": 1,
    "max_retries": 3
  }
}
```

## Performance Considerations

### Hardware Requirements
- **CPU**: Multi-core processor (Intel i5 or equivalent)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: CUDA-compatible GPU (optional but recommended)
- **Storage**: 10GB free space for models and logs

### GPU Acceleration
- CUDA support for NVIDIA GPUs
- Automatic fallback to CPU if GPU not available
- Memory optimization for large models

### Optimization Techniques
- Model quantization for faster inference
- Batch processing for multiple frames
- Memory pooling to reduce allocations
- Asynchronous API calls

## Deployment Options

### Edge Deployment
- Run directly on camera-enabled devices
- Minimal hardware requirements
- Local processing with periodic cloud sync
- Ideal for privacy-sensitive environments

### Cloud Deployment
- Centralized processing with multiple camera inputs
- Scalable infrastructure
- Advanced analytics and reporting
- Integration with other systems

### Hybrid Deployment
- Edge processing for real-time counting
- Cloud aggregation for analytics
- Best of both approaches
- Optimized for performance and cost

## Testing and Validation

### Unit Testing
- Test data generation functions
- Validate API communication
- Check model loading and inference
- Verify configuration parsing

### Integration Testing
- End-to-end detection pipeline
- API integration testing
- Performance benchmarking
- Stress testing with high load

### Validation Metrics
- **Accuracy**: Detection accuracy compared to ground truth
- **Precision**: Ratio of true positives to total detections
- **Recall**: Ratio of true positives to actual objects
- **FPS**: Frames per second processing rate
- **Latency**: Time from frame capture to API submission

## Troubleshooting

### Common Issues

1. **Camera Not Detected**
   - Check camera connections
   - Verify camera permissions
   - Test with other applications
   - Update camera drivers

2. **Model Loading Errors**
   - Verify model file paths
   - Check model file integrity
   - Ensure compatible PyTorch version
   - Validate GPU/CUDA setup

3. **API Connection Issues**
   - Check network connectivity
   - Verify API endpoint URL
   - Confirm authentication credentials
   - Review firewall settings

4. **Performance Problems**
   - Monitor CPU/GPU usage
   - Check memory consumption
   - Optimize model settings
   - Consider hardware upgrades

### Diagnostic Tools
- Built-in logging and monitoring
- Performance profiling utilities
- Error reporting mechanisms
- Health check endpoints

## Security Considerations

### Data Privacy
- No personal identification data stored
- Anonymized demographic information only
- Secure transmission with HTTPS
- Compliance with privacy regulations

### Model Security
- Secure model distribution
- Model integrity verification
- Protection against adversarial attacks
- Regular security updates

### API Security
- Authentication and authorization
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure communication channels

## Maintenance and Updates

### Model Updates
- Regular model retraining with new data
- A/B testing for model improvements
- Automatic update mechanisms
- Backward compatibility considerations

### Software Updates
- Dependency version management
- Security patch application
- Feature release coordination
- Migration procedures

### Monitoring and Logging
- Real-time system health monitoring
- Performance metrics collection
- Error tracking and reporting
- Automated alerting for issues

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python code
- Include docstrings for functions and classes
- Write unit tests for new functionality
- Document configuration changes

### Testing Requirements
- All new features must include tests
- Performance benchmarks for critical functions
- Integration tests for API communication
- Cross-platform compatibility verification