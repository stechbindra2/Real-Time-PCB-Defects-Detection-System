# 🔍 PCB Defect Detection System

**Real-time printed circuit board defect detection powered by YOLOv8 — from published research to production-ready application.**

[![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-00FFFF)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Web-Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![IEEE](https://img.shields.io/badge/Published-IEEE%20Xplore-00629B?logo=ieee&logoColor=white)](https://ieeexplore.ieee.org/abstract/document/11241378/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

📄 **Published Research:** *Real-Time PCB Defect Detection Using YOLOv8* — IEEE Xplore
🎓 **Author:** Shashikant Kumar Bind · [Google Scholar](https://scholar.google.com/citations?user=16T6AUYAAAAJ&hl=en&authuser=1) · [IEEE Paper](https://ieeexplore.ieee.org/abstract/document/11241378/)

---

## Table of Contents

- [Overview](#overview)
- [Published Research](#published-research)
- [Results](#results)
- [Defects Detected](#defects-detected)
- [Highlights](#highlights)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Running the Desktop Application](#running-the-desktop-application)
- [Running the Web Application](#running-the-web-application)
- [Requirements](#requirements)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)
- [License](#license)
- [Author](#author)

---

## Overview

This project is the applied, deployable counterpart to a peer-reviewed research paper on automated PCB inspection. It uses a **YOLOv8 object detection model** to localize common manufacturing defects directly from PCB images, and ships as two ready-to-use interfaces — a **desktop app** (Tkinter) and a **web app** (Flask) — so the same trained model can be demoed locally or in a browser with zero extra setup.

It's built for:

- Quality-control proof-of-concepts for electronics manufacturing
- Academic demonstrations and research showcases
- Computer vision portfolio / final-year project use
- A reference implementation to extend toward factory-floor deployment

## Published Research

This system implements the detection pipeline described in the following peer-reviewed publication:

> **Real-Time PCB Defect Detection Using YOLOv8**
> Shashikant Kumar Bind, *et al.*
> IEEE Conference Publication — [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/11241378/)

The paper details the dataset preparation, YOLOv8 training methodology, and evaluation used to build the `best.pt` model shipped in this repository. Full author profile and publication record: [Google Scholar](https://scholar.google.com/citations?user=16T6AUYAAAAJ&hl=en&authuser=1).

See [Citation](#citation) below for how to cite this work.

## Results

Sample inference results from the trained model — each pair shows the raw uploaded PCB image alongside the model's annotated defect output.

<table>
<tr>
<th>Input</th>
<th>Detected Defects</th>
</tr>
<tr>
<td><img src="static/uploads/5ebfc588-0d5d-4975-8c9f-095e5d2d9238.jpg" width="380"/></td>
<td><img src="static/results/result_5ebfc588-0d5d-4975-8c9f-095e5d2d9238.jpg" width="380"/></td>
</tr>
<tr>
<td><img src="static/uploads/8e03beca-fa03-4c37-92aa-c64a435ae100.jpg" width="380"/></td>
<td><img src="static/results/result_8e03beca-fa03-4c37-92aa-c64a435ae100.jpg" width="380"/></td>
</tr>
<tr>
<td><img src="static/uploads/f77adbeb-5e78-4f0f-aee4-5f16476303bd.jpg" width="380"/></td>
<td><img src="static/results/result_f77adbeb-5e78-4f0f-aee4-5f16476303bd.jpg" width="380"/></td>
</tr>
</table>

> **Note:** these images are pulled directly from `static/uploads/` and `static/results/` in this repo. For a cleaner public-facing README, consider copying 3–5 representative pairs into a dedicated `assets/results/` folder with descriptive names (e.g. `sample1_input.jpg` / `sample1_output.jpg`) instead of raw UUID filenames — see [Roadmap](#roadmap).

## Defects Detected

The trained model identifies six standard PCB defect categories:

| Class | Description |
|---|---|
| **Missing Hole** | Absent drill hole where one is required by the design |
| **Mouse Bite** | Small semicircular notches along the board edge/pad |
| **Open Circuit** | Break in a copper trace that interrupts conductivity |
| **Short** | Unintended contact between two conductive paths |
| **Spur** | Excess copper protruding from a trace |
| **Spurious Copper** | Unwanted copper deposits elsewhere on the board |

## Highlights

- YOLOv8-based object detection pipeline for PCB defect localization
- Dual deployment: desktop application and web application, sharing one trained model
- Full image upload → inference → annotation → export workflow
- Professional dark/light theme support
- Grounded in peer-reviewed, IEEE-published research

## System Architecture

| Component | File | Description |
|---|---|---|
| Desktop App | `yolo_gui.py` | Tkinter-based GUI for local, offline testing |
| Web App | `app.py` | Flask-based browser interface for demos and remote access |
| Model | `best.pt` | Trained YOLOv8 weights used for inference |

**Workflow:**

1. User selects or uploads a PCB image
2. The application loads `best.pt`
3. YOLOv8 runs object detection on the input image
4. Detected defects are drawn as annotated bounding boxes
5. The user reviews and optionally exports the annotated result

## Project Structure

```text
project-root/
├── app.py                     # Flask web application
├── yolo_gui.py                 # Tkinter desktop application
├── best.pt                     # Trained YOLOv8 model weights
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── Report.md                   # Project/technical report
├── PCB_defect_detection_with_YOLOv8.ipynb   # Training notebook
├── templates/
│   ├── index.html
│   └── about.html
└── static/
    ├── css/
    ├── js/
    ├── uploads/                 # Original user-uploaded PCB images
    └── results/                 # Annotated inference outputs
```

## Technology Stack

- **Python** — application logic
- **Ultralytics YOLOv8** — defect detection model
- **OpenCV** — image handling and annotation
- **NumPy** — numerical operations
- **Pillow** — image processing / GUI compatibility
- **Flask** — web interface
- **Tkinter** — desktop interface

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

```bash
git clone <repository-url>
cd yulo
pip install -r requirements.txt
```

Place the trained model weights in the project root:

```text
best.pt
```

## Running the Desktop Application

```bash
python yolo_gui.py
```

1. Click **Select Image** to load a PCB image
2. Click **Detect Defects** to run inference
3. Review the annotated output
4. Click **Save Results** to export
5. Click **Clear** to reset the session

## Running the Web Application

```bash
python app.py
```

Open in your browser:

```text
http://127.0.0.1:5000/
```

1. Upload a PCB image (file picker or drag-and-drop)
2. Run **Detect Defects**
3. Inspect the highlighted defect regions
4. Download the annotated result
5. Start a new session with **New Detection**

## Requirements

```text
ultralytics
opencv-python
pillow
numpy
flask
```

> `tkinter` is typically bundled with standard Python installs, but availability varies by platform.

## Roadmap

Planned improvements to strengthen this project for research demos, internships, and startup-style presentations:

- [ ] Confidence score display per predicted defect
- [ ] Per-class defect counts in the UI
- [ ] Batch inspection for multiple PCB images
- [ ] Inference timing / performance metrics panel
- [ ] Upload validation and error-state handling
- [ ] Model/version metadata in the interface
- [ ] Curated sample test images for one-click demos
- [ ] Docker support for reproducible deployment
- [ ] REST API endpoints for factory-system integration
- [ ] Move sample results into `assets/results/` with descriptive filenames

## Troubleshooting

| Issue | Fix |
|---|---|
| Inference fails to start | Ensure `best.pt` is present in the project root |
| Import errors | Verify all dependencies from `requirements.txt` are installed in the active environment |
| GUI won't open | Check that Tkinter is available in your Python installation |
| Web app won't load | Confirm Flask is installed and port `5000` is free |
| Poor detections | Check image quality, model compatibility, and class mapping |

## Citation

If you use this work, please cite the associated IEEE publication:

```bibtex
@inproceedings{bind_pcb_yolov8,
  author  = {Bind, Shashikant Kumar},
  title   = {Real-Time PCB Defect Detection Using YOLOv8},
  booktitle = {IEEE Conference Publication},
  year    = {2025},
  url     = {https://ieeexplore.ieee.org/abstract/document/11241378/}
}
```

> Replace `booktitle`, exact page numbers, and DOI with the final published details from the [IEEE Xplore record](https://ieeexplore.ieee.org/abstract/document/11241378/) — IEEE Xplore provides a ready-made citation export (BibTeX/EndNote/plain text) via the "Cite This" button on the paper page.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details. *(Swap in your preferred license — Apache-2.0 or an academic/research license also fit well here.)*

## Author

**Shashikant Kumar Bind**
B.Tech, Electronics & Communication Engineering (AI/ML) · BS Data Science & Applications, IIT Madras

- 🎓 Google Scholar: [scholar.google.com/citations?user=16T6AUYAAAAJ](https://scholar.google.com/citations?user=16T6AUYAAAAJ&hl=en&authuser=1)
- 📄 IEEE Xplore: [Real-Time PCB Defect Detection Using YOLOv8](https://ieeexplore.ieee.org/abstract/document/11241378/)
