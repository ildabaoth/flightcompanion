from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Shared telemetry data
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/telemetry", methods=["GET"])
def get_telemetry():
    return jsonify(telemetry_data)

@app.route("/api/update", methods=["POST"])
def update_telemetry():
    global telemetry_data
    try:
        data = request.json
        if data:
            telemetry_data.update(data)
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "error", "message": "No data"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
