from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import threading
import time
import numpy as np
import pytest
from pcb_detection.inference import Detector, ModelUnavailable


class Tensor:
    def __init__(self, values):
        self.values = values
    def tolist(self):
        return self.values


def test_shared_results_color_metadata_and_serialization(tmp_path):
    weights = tmp_path / "best.pt"
    weights.touch()
    calls, active = [], []
    result = SimpleNamespace(
        boxes=SimpleNamespace(cls=Tensor([0]), conf=Tensor([0.87654]),
                              xyxy=Tensor([[1, 2, 3, 4]])), names={0: "short"},
        plot=lambda: np.array([[[255, 0, 0]]], dtype=np.uint8))

    class Model:
        def predict(self, **kwargs):
            assert not active, "Concurrent use of shared model"
            active.append(True)
            try:
                calls.append(kwargs)
                time.sleep(0.01)
                return [result]
            finally:
                active.pop()

    loads = []
    def loader(path):
        loads.append(path)
        return Model()

    detector = Detector(weights, loader=loader)
    with ThreadPoolExecutor(max_workers=3) as pool:
        outputs = list(pool.map(detector.detect, ["board.png"] * 3))
    assert len(loads) == 1 and len(calls) == 3
    image, details = outputs[0]
    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert details["class_counts"] == {"short": 1}
    assert details["detections"][0]["bbox"] == [1, 2, 3, 4]
    assert details["detections"][0]["confidence"] == 0.8765
    assert details["inference_ms"] >= 0
    assert calls[0]["device"] == "cpu"


def test_load_failures_and_configuration(tmp_path):
    with pytest.raises(ValueError):
        Detector(tmp_path / "x", confidence=2)
    with pytest.raises(ModelUnavailable):
        Detector(tmp_path / "missing.pt").check_ready()
    weights = tmp_path / "bad.pt"
    weights.touch()
    def fail(path):
        raise RuntimeError("bad weights")
    with pytest.raises(ModelUnavailable):
        Detector(weights, loader=fail).check_ready()


def test_no_boxes_diagnostic(tmp_path):
    weights = tmp_path / "best.pt"
    weights.touch()
    result = SimpleNamespace(boxes=None, plot=lambda: np.zeros((1, 1, 3), dtype=np.uint8))
    detector = Detector(weights, loader=lambda _: SimpleNamespace(predict=lambda **_: [result]))
    _, details = detector.detect("board.png")
    assert details["detections"] == []
    assert "electrical functionality is unverified" in details["diagnostic"]
