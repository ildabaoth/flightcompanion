import logging
import math

class Copilot:
    """
    Main logic for the virtual copilot. Analyzes telemetry and decides what to say.
    """
    def __init__(self, speech_engine):
        self.speech = speech_engine
        self.last_altitude = 0
        self.last_on_ground = True
        self.altitude_checkpoints = [1000, 2000, 5000, 10000, 18000]
        self.reached_checkpoints = set()
        
        # Landmarks: {"name": str, "lat": float, "lon": float, "announced": bool}
        self.landmarks = [
            {"name": "Statue of Liberty", "lat": 40.6892, "lon": -74.0445, "announced": False},
            {"name": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "announced": False},
            {"name": "Golden Gate Bridge", "lat": 37.8199, "lon": -122.4783, "announced": False},
            {"name": "London Eye", "lat": 51.5033, "lon": -0.1195, "announced": False},
            {"name": "Sydney Opera House", "lat": -33.8568, "lon": 151.2153, "announced": False}
        ]
        
        self.flight_phase = "PREFLIGHT"

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine formula to calculate distance in Nautical Miles."""
        R = 3440.065 
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        return 2 * R * math.asin(math.sqrt(a))

    def process_telemetry(self, data):
        """Evaluates telemetry data and triggers speech."""
        if not data:
            return

        altitude = data.get("altitude", 0)
        on_ground = data.get("on_ground", True)
        airspeed = data.get("airspeed", 0)
        lat = data.get("latitude")
        lon = data.get("longitude")

        # 1. Detect Takeoff
        if self.last_on_ground and not on_ground:
            self.speech.say("Positive rate. Gear up.")
            self.flight_phase = "CLIMB"
            logging.info("Phase change: CLIMB")

        # 2. Altitude Callouts (climbing)
        if not on_ground and altitude > self.last_altitude:
            for cp in self.altitude_checkpoints:
                if altitude >= cp and cp not in self.reached_checkpoints:
                    self.speech.say(f"Passing {cp} feet.")
                    self.reached_checkpoints.add(cp)

        # 3. Landmark Detection
        if lat is not None and lon is not None:
            for landmark in self.landmarks:
                if not landmark["announced"]:
                    dist = self._calculate_distance(lat, lon, landmark["lat"], landmark["lon"])
                    if dist < 2.0: # Within 2 Nautical Miles
                        self.speech.say(f"Look out to the window. We are passing near the {landmark['name']}.")
                        landmark["announced"] = True
                        logging.info(f"Announced landmark: {landmark['name']}")

        # 4. Landing Detection
        if not self.last_on_ground and on_ground:
            self.speech.say("Touchdown. Welcome home.")
            self.flight_phase = "POSTFLIGHT"
            self.reached_checkpoints.clear()
            # Reset landmarks for next flight
            for l in self.landmarks: l["announced"] = False
            logging.info("Phase change: POSTFLIGHT")

        # Update states
        self.last_altitude = altitude
        self.last_on_ground = on_ground

    def welcome(self):
        self.speech.say("Copilot systems ready. Standing by for flight data.")

    def report_status(self, data):
        """Speaks a summary of the current flight status."""
        if not data:
            self.speech.say("I don't have enough flight data yet, captain.")
            return

        altitude = round(data.get("altitude", 0))
        speed = round(data.get("airspeed", 0))
        heading = round(data.get("heading", 0))

        report = f"Currently at {altitude} feet, airspeed {speed} knots, heading {heading} degrees."
        # Save to static folder for web access
        self.speech.say(report, filename="static/status_report.wav")

if __name__ == "__main__":
    # Mock test
    class MockSpeech:
        def say(self, text): print(f"Speech: {text}")
    
    cp = Copilot(MockSpeech())
    print("Simulating Takeoff...")
    cp.process_telemetry({"altitude": 10, "on_ground": True, "airspeed": 100})
    cp.process_telemetry({"altitude": 100, "on_ground": False, "airspeed": 120})
    print("Simulating Climb...")
    cp.process_telemetry({"altitude": 1100, "on_ground": False, "airspeed": 150})
    print("Simulating Landing...")
    cp.process_telemetry({"altitude": 5, "on_ground": True, "airspeed": 60})
