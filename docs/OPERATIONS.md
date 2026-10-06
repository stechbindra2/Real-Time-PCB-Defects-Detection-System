# Operations and API

This system detects visible manufacturing defects in images. It cannot certify electrical
continuity, component values, hidden damage, or board functionality. Model confidence is
not a calibrated probability of board safety. No inference accuracy is established by the
application tests.

## Setup

Use Python 3.10–3.13 (3.12 recommended). Create a virtual environment, then install
`requirements-inference.txt`. Tkinter is an OS/Python distribution component, not a pip
package; on Debian/Ubuntu install `python3-tk` for the desktop app. The web app does not
need Tkinter. Install `requirements-dev.txt` to run tests without PyTorch or weights.
Direct application dependencies are pinned; transitive dependencies and hardware-specific
PyTorch packages are not fully locked. For a deployment, record `pip freeze`, Python version,
OS, PyTorch/device information, and the SHA-256 of trusted weights.

The repository does **not** contain `best.pt`. Obtain the trained PCB weights from the
project author or reproduce training from the notebook. Generic YOLO weights will not
provide the PCB class mapping. Only load trusted weights: PyTorch model artifacts may
execute code. Keep weights out of Git; record provenance and checksum beside a deployment.

## Configuration

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `PCB_MODEL_PATH` | repository `best.pt` | Trusted trained weights |
| `PCB_DATA_DIR` | repository `instance/` | Private writable storage |
| `PCB_CONFIDENCE` | `0.25` | Threshold in [0,1] |
| `PCB_DEVICE` | `cpu` | Ultralytics device, e.g. `0` for CUDA |

Paths for default templates, static assets, weights and storage are independent of the
working directory. Environment paths should be absolute. Factory configuration can also
set `MAX_CONTENT_LENGTH` (16 MiB default) and `MAX_IMAGE_PIXELS` (20 million default).
The first inference or readiness request lazily loads weights. Inference is serialized per
process; multiple server processes each consume their own model memory.

Run locally: `python app.py`. Deploy with `waitress-serve --host=127.0.0.1 --port=8000 app:app`
behind an HTTPS reverse proxy. Debug mode is off. Set proxy body limits and request timeouts.
The service has no authentication or tenant isolation; restrict it to trusted users or add
an authenticated gateway before public exposure. Opaque image identifiers are bearer links,
not access control. Add rate limits and disk quotas at the gateway/infrastructure layer.

Uploads are decoded as PNG/JPEG/BMP, checked for dimensions and corruption, EXIF-oriented,
converted to RGB and re-encoded as PNG without original metadata. Client filenames never
become storage paths. Runtime uploads are outside the public static directory. Results are
served only through validated identifiers and have no-store response headers. Existing
tracked `static/uploads` and `static/results` files are historical README demonstration
assets, not newly uploaded runtime data.

Schedule `flask --app app cleanup --older-than-hours 24` outside peak usage to bound retention.
Cleanup can race a request for an old image; avoid deleting files still needed by clients.
Disk capacity must still be monitored; cleanup does not impose a disk quota.

## API

- `GET /healthz`: process liveness, 200, no model loading.
- `GET /readyz`: attempts model loading, 200 if ready, 503 if unavailable. Does not run an inference warmup.
- `POST /upload`: multipart `file`; returns `{success: true, filename: <opaque-id>.png}`.
- `POST /detect`: JSON `{filename: <upload-id>}`; returns `result_path`, `result_filename`,
  `detections_count`, `detections` (class, confidence, pixel `bbox` in xyxy order),
  `class_counts`, `inference_ms`, `confidence_threshold`, `model`, and `diagnostic`.
- `GET /results/<id>.png`: annotated RGB PNG; use `result_path` from detection.

Errors are JSON: 400 malformed/corrupt input; 404 unknown ID; 413 byte/pixel limit;
415 unsupported image format; 503 missing/broken model; 500 unexpected inference failure.
Detailed inference errors are logged server-side, not returned to the browser.
Timing includes waiting for the model lock and first-load overhead, not just neural network
execution. Bounding boxes refer to the normalized image after EXIF orientation.

## Validation and research reproducibility

Run `python -m pytest -q`. Tests cover upload validation, traversal, limits, private serving,
errors, model readiness, BGR/RGB conversion, metadata, and concurrent model serialization
using fake predictions. They do not establish model accuracy or exercise GPU drivers.
For real validation, supply trusted weights and a held-out annotated dataset; record class
mapping, split manifest, random seed, training configuration, dataset provenance, weight
checksum, mAP@0.5 and mAP@0.5:0.95, per-class recall, and target-device latency. The notebook
is retained as historical research and has not been independently reproduced.
