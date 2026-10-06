"""Compatibility entry point. Use a WSGI server for deployed environments."""
from pcb_detection.web import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False)
