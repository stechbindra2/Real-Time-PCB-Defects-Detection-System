"""Flask application factory with private, normalized image storage."""
import os
import re
import uuid
import warnings
from pathlib import Path
import click
from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.exceptions import HTTPException
from .inference import Detector, ModelUnavailable
from . import ROOT

TOKEN = re.compile(r"[0-9a-f]{32}\.png\Z")


def create_app(config=None, detector=None):
    app = Flask(__name__, template_folder=str(ROOT / "templates"),
                static_folder=str(ROOT / "static"), instance_path=str(ROOT / "instance"))
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=16 * 1024 * 1024, MAX_IMAGE_PIXELS=20_000_000,
        DATA_DIR=os.getenv("PCB_DATA_DIR", str(ROOT / "instance")),
        MODEL_PATH=os.getenv("PCB_MODEL_PATH", str(ROOT / "best.pt")),
        CONFIDENCE=os.getenv("PCB_CONFIDENCE", "0.25"), DEVICE=os.getenv("PCB_DEVICE", "cpu"))
    if config:
        app.config.update(config)
    storage = Path(app.config["DATA_DIR"]).resolve()
    uploads, results = storage / "uploads", storage / "results"
    for folder in (uploads, results):
        folder.mkdir(parents=True, exist_ok=True)
    engine = detector if detector is not None else Detector(
        app.config["MODEL_PATH"], app.config["CONFIDENCE"], app.config["DEVICE"])
    app.extensions["pcb_detector"] = engine

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(error=exc.description, code=exc.name), exc.code

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        if request.path.startswith(("/upload", "/detect", "/results", "/readyz")):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/healthz")
    def health():
        return jsonify(status="ok")

    @app.get("/readyz")
    def ready():
        try:
            engine.check_ready()
            return jsonify(status="ready")
        except ModelUnavailable as exc:
            app.logger.warning("Model unavailable: %s", exc)
            return jsonify(error=str(exc), code="model_unavailable"), 503

    @app.post("/upload")
    def upload():
        file = request.files.get("file")
        if file is None or not file.filename:
            return jsonify(error="Select a PNG, JPEG, or BMP image."), 400
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(file.stream) as source:
                    if source.format not in {"PNG", "JPEG", "BMP"}:
                        return jsonify(error="Only PNG, JPEG, and BMP images are supported."), 415
                    if source.width * source.height > app.config["MAX_IMAGE_PIXELS"]:
                        return jsonify(error="Image exceeds the pixel limit."), 413
                    source.load()
                    image = ImageOps.exif_transpose(source).convert("RGB")
            filename = uuid.uuid4().hex + ".png"
            image.save(uploads / filename, format="PNG")
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            return jsonify(error="Image exceeds the pixel limit."), 413
        except (UnidentifiedImageError, OSError, ValueError):
            return jsonify(error="Invalid or corrupt image."), 400
        return jsonify(success=True, filename=filename)

    @app.post("/detect")
    def detect():
        data = request.get_json(silent=True)
        filename = data.get("filename") if isinstance(data, dict) else None
        if not isinstance(filename, str) or not TOKEN.fullmatch(filename):
            return jsonify(error="A valid uploaded image ID is required."), 400
        image_path = uploads / filename
        if not image_path.is_file():
            return jsonify(error="Uploaded image not found."), 404
        try:
            image, details = engine.detect(str(image_path))
            result_filename = uuid.uuid4().hex + ".png"
            image.save(results / result_filename, format="PNG")
            return jsonify(success=True, result_filename=result_filename,
                           result_path=url_for("result_image", filename=result_filename), **details)
        except ModelUnavailable as exc:
            app.logger.warning("Model unavailable: %s", exc)
            return jsonify(error=str(exc), code="model_unavailable"), 503
        except Exception:
            app.logger.exception("Inference failed")
            return jsonify(error="Detection failed. Check the server logs.", code="inference_failed"), 500

    @app.get("/results/<filename>")
    def result_image(filename):
        if not TOKEN.fullmatch(filename):
            return jsonify(error="Result not found."), 404
        return send_from_directory(results, filename, mimetype="image/png")

    @app.cli.command("cleanup")
    @click.option("--older-than-hours", default=24.0, type=click.FloatRange(min=0.0))
    def cleanup(older_than_hours):
        """Remove runtime images older than the given retention period."""
        import time
        cutoff = time.time() - older_than_hours * 3600
        count = 0
        for folder in (uploads, results):
            for path in folder.glob("*.png"):
                if TOKEN.fullmatch(path.name) and path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
                    count += 1
        click.echo(f"Removed {count} images")

    return app
