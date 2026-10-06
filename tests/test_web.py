from io import BytesIO
from PIL import Image
import pytest
from pcb_detection.web import create_app
from pcb_detection.inference import ModelUnavailable


class FakeDetector:
    def check_ready(self):
        pass

    def detect(self, path):
        return Image.new("RGB", (4, 4), "red"), {
            "detections": [], "detections_count": 0, "class_counts": {},
            "inference_ms": 1.2, "diagnostic": "Electrical functionality unverified."}


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATA_DIR": str(tmp_path)}, FakeDetector())


def upload(client, data=None, filename="board.png"):
    if data is None:
        data = BytesIO()
        Image.new("RGB", (4, 4), "blue").save(data, "PNG")
        data.seek(0)
    return client.post("/upload", data={"file": (data, filename)})


def test_complete_flow(app):
    client = app.test_client()
    response = upload(client, filename="../../unsafe.html")
    assert response.status_code == 200
    assert "file_path" not in response.json
    filename = response.json["filename"]
    assert filename.endswith(".png") and "/" not in filename
    response = client.post("/detect", json={"filename": filename})
    assert response.status_code == 200
    assert response.json["detections_count"] == 0
    result = client.get(response.json["result_path"])
    assert result.status_code == 200 and result.mimetype == "image/png"
    assert result.headers["Cache-Control"] == "no-store"
    assert client.get("/static/uploads/" + filename).status_code == 404


@pytest.mark.parametrize("body", [None, {}, [], {"filename": 3}, {"filename": "../../app.py"},
                                       {"filename": "/etc/passwd"}, {"filename": "x.png"}])
def test_bad_detection_requests(app, body):
    assert app.test_client().post("/detect", json=body).status_code == 400


def test_invalid_uploads(app):
    client = app.test_client()
    assert client.post("/upload").status_code == 400
    assert upload(client, BytesIO(b"<script>evil</script>"), "board.png").status_code == 400
    data = BytesIO()
    Image.new("RGB", (2, 2)).save(data, "GIF")
    data.seek(0)
    assert upload(client, data).status_code == 415
    app.config["MAX_IMAGE_PIXELS"] = 2
    assert upload(client).status_code == 413
    assert list(__import__('pathlib').Path(app.config['DATA_DIR']).joinpath('uploads').iterdir()) == []


def test_size_limit_and_not_found(app):
    client = app.test_client()
    assert client.post("/detect", json={"filename": "a" * 32 + ".png"}).status_code == 404
    assert client.get("/results/bad.png").status_code == 404
    app.config["MAX_CONTENT_LENGTH"] = 10
    response = upload(client)
    assert response.status_code == 413 and "error" in response.json


def test_missing_weights_and_health(tmp_path):
    app = create_app({"TESTING": True, "DATA_DIR": str(tmp_path),
                      "MODEL_PATH": str(tmp_path / "missing.pt")})
    client = app.test_client()
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 503
    filename = upload(client).json["filename"]
    response = client.post("/detect", json={"filename": filename})
    assert response.status_code == 503
    assert response.json["code"] == "model_unavailable"


def test_errors_do_not_leak_server_details(app):
    def fail(path):
        raise RuntimeError("private password and filesystem path")
    app.extensions["pcb_detector"].detect = fail
    client = app.test_client()
    filename = upload(client).json["filename"]
    response = client.post("/detect", json={"filename": filename})
    assert response.status_code == 500
    assert "private" not in response.json["error"]


def test_pages_and_cleanup(app):
    client = app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/about").status_code == 200
    upload(client)
    result = app.test_cli_runner().invoke(args=["cleanup", "--older-than-hours", "0"])
    assert result.exit_code == 0 and "Removed 1 images" in result.output
