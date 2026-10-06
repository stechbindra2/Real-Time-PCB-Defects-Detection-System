"""Lazy, serialized YOLO inference shared by both interfaces."""
from collections import Counter
from pathlib import Path
from threading import Lock
from time import perf_counter
from PIL import Image


class ModelUnavailable(RuntimeError):
    """Weights or inference dependencies are unavailable."""


class Detector:
    def __init__(self, weights, confidence=0.25, device="cpu", loader=None):
        self.weights = Path(weights).resolve()
        self.confidence = float(confidence)
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        self.device = device
        self._loader = loader
        self._model = None
        self._lock = Lock()

    def _load(self):
        if self._model is None:
            if not self.weights.is_file():
                raise ModelUnavailable("Trained weights are missing. Configure PCB_MODEL_PATH.")
            try:
                if self._loader is None:
                    from ultralytics import YOLO
                    self._loader = YOLO
                self._model = self._loader(str(self.weights))
            except Exception as exc:
                raise ModelUnavailable("Unable to load trained weights or inference dependencies.") from exc

    def check_ready(self):
        with self._lock:
            self._load()

    def detect(self, image):
        start = perf_counter()
        with self._lock:
            self._load()
            result = self._model.predict(source=image, conf=self.confidence,
                                         device=self.device, verbose=False)[0]
            detections = []
            if result.boxes is not None:
                for index, (cls, conf, xyxy) in enumerate(zip(
                    result.boxes.cls.tolist(), result.boxes.conf.tolist(),
                    result.boxes.xyxy.tolist()), 1):
                    detections.append({"id": index, "class": result.names[int(cls)],
                                       "confidence": round(float(conf), 4),
                                       "bbox": [round(float(v), 2) for v in xyxy]})
            # Ultralytics plot() returns BGR; Pillow expects RGB.
            annotated = Image.fromarray(result.plot()[..., ::-1])
        return annotated, {"detections": detections, "detections_count": len(detections),
                           "class_counts": dict(Counter(d["class"] for d in detections)),
                           "inference_ms": round((perf_counter() - start) * 1000, 2),
                           "confidence_threshold": self.confidence,
                           "model": self.weights.name,
                           "diagnostic": "Visible defects detected." if detections else
                           "No visible defects detected; electrical functionality is unverified."}
