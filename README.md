# PCB Defect Detection System

A professional PCB inspection system that uses **YOLOv8 object detection** to identify common manufacturing defects in printed circuit boards. It is designed for both rapid visual inspection and demonstration-ready deployment through a desktop interface and a browser-based web application.

## Overview

This project helps automate PCB quality inspection by detecting localized defects directly from board images and returning annotated results for review. It is suitable for academic demonstrations, manufacturing-focused computer vision projects, and practical defect-analysis workflows.

## Highlights

- YOLOv8-based object detection pipeline for PCB defect localization.
- Dual deployment modes: desktop application and web application.
- Image upload, inference, annotation, and result export workflow.
- Professional dark and light theme support.
- Clean interface for demos, internal tools, and project showcases.

## Defects Detected

The trained model is configured to detect the following PCB defect categories:

- Missing Hole
- Mouse Bite
- Open Circuit
- Short
- Spur
- Spurious Copper

## System Architecture

The system is organized into two user-facing applications that share the same trained YOLO model:

1. **Desktop App (`yolo_gui.py`)**  
   Built with Tkinter for local execution and quick offline testing.
2. **Web App (`app.py`)**  
   Built with Flask for browser-based access and easier demonstrations.
3. **Model File (`best.pt`)**  
   Contains the trained YOLOv8 weights used during inference.

## Core Workflow

1. User selects or uploads a PCB image.
2. The application loads the `best.pt` model.
3. YOLOv8 performs object detection on the input image.
4. Detected defects are rendered on the image with visual annotations.
5. The user reviews the results and saves the annotated output if needed.

## Project Structure

```text
project-root/
├── app.py                  # Flask web application
├── yolo_gui.py             # Tkinter desktop application
├── best.pt                 # Trained YOLOv8 model weights
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates for the web app
├── static/                 # CSS, JavaScript, images, and assets
└── README.md               # Project documentation
```

## Technology Stack

- **Python** for the application logic.
- **Ultralytics YOLOv8** for defect detection.
- **OpenCV** for image handling and annotation workflows.
- **NumPy** for numerical operations.
- **Pillow** for image processing and GUI compatibility.
- **Flask** for the web interface.
- **Tkinter** for the desktop interface.

## Prerequisites

Before running the project, ensure the following are installed:

- Python 3.7 or newer
- pip package manager

## Installation

```bash
git clone <repository-url>
cd yulo
pip install -r requirements.txt
```

Then place the trained model file below in the project root:

```text
best.pt
```

## Running the Desktop Application

```bash
python yolo_gui.py
```

### Desktop Usage

- Click **Select Image** to load a PCB image.
- Click **Detect Defects** to run inference.
- Review the annotated output in the results area.
- Click **Save Results** to export the processed image.
- Click **Clear** to reset the session.

## Running the Web Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

### Web Usage

- Upload a PCB image using file selection or drag-and-drop.
- Start detection with the **Detect Defects** action.
- Inspect highlighted defect regions in the output preview.
- Download the annotated result image.
- Start a fresh session with **New Detection**.

## Recommended Improvements

To make the project stronger for internships, GitHub, research demos, or startup-style presentations, consider adding:

- Confidence score display for each predicted defect.
- Per-class defect counts in the UI.
- Batch inspection for multiple PCB images.
- Inference timing and performance metrics.
- Upload validation and error-state handling.
- Model/version metadata in the interface.
- Sample test images for one-click demonstration.
- Docker support for reproducible deployment.
- API endpoints for integration with factory systems.

## Example Use Cases

- Academic major project or final-year demonstration.
- Computer vision portfolio project.
- Prototype for smart manufacturing quality inspection.
- Industrial defect-monitoring proof of concept.
- Dataset and model evaluation interface for PCB research.

## Requirements

A typical `requirements.txt` may include:

```text
ultralytics
opencv-python
pillow
numpy
flask
```

> `tkinter` is usually bundled with standard Python installations on many systems, but availability can vary by platform.

## Troubleshooting

- Ensure `best.pt` is present in the root folder before starting inference.
- Verify that all dependencies are installed in the active Python environment.
- If the GUI does not open, check whether Tkinter is available in your Python installation.
- If the web app does not load, confirm that Flask is installed and port `5000` is free.
- If detections are poor, validate image quality, model compatibility, and class mapping.


## License

Add your preferred license here, such as MIT, Apache-2.0, or a custom academic/research license.
