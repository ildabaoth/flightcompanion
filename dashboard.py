from flask import Flask, jsonify, render_template
from flask_cors import CORS
import threading
import logging

app = Flask(__name__)
CORS(app)

# Global telemetry storage
telemetry_data = {
    "altitude": 0,
    "airspeed": 0,
    "latitude": 0,
    "longitude": 0,
    "heading": 0,
    "vertical_speed": 0,
    "ground_speed": 0,
    "on_ground": True
}

speech_requested = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/telemetry")
def get_telemetry():
    return jsonify(telemetry_data)

@app.route("/api/report", methods=["POST"])
def request_report():
    global speech_requested
    logging.info("Status report requested via web button.")
    speech_requested = True
    return jsonify({"status": "requested"})

def get_speech_request():
    """Checks if a speech report was requested and resets the flag."""
    global speech_requested
    if speech_requested:
        speech_requested = False
        return True
    return False

def update_telemetry(data):
    """Updates the global telemetry dictionary with new data."""
    global telemetry_data
    if data:
        telemetry_data.update(data)

def run_server(port=5000):
    """Starts the Flask server in a separate thread."""
    # Disable flask console logging to keep terminal clean
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def start_dashboard_thread(port=5000):
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    return thread
