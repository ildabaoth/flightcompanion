from SimConnect import SimConnect, AircraftRequests
import logging
import time

import math

class SimInterface:
    """
    Handles connection and data retrieval from MSFS using SimConnect.
    """
    def __init__(self):
        self.sm = None
        self.aq = None
        self.connected = False
        
    def connect(self):
        """Attempt to connect to the simulator."""
        try:
            logging.info("Connecting to SimConnect...")
            self.sm = SimConnect()
            self.aq = AircraftRequests(self.sm, _time=2000)
            self.connected = True
            logging.info("Connected to MSFS!")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to SimConnect: {e}")
            self.connected = False
            return False

    def get_var(self, name, unit=None):
        """Read a SimVar by name."""
        if not self.connected or not self.aq:
            return None
        try:
            # AircraftRequests.get() returns the value of the variable
            return self.aq.get(name)
        except Exception as e:
            logging.debug(f"Error reading variable {name}: {e}")
            return None

    def get_basic_telemetry(self):
        """Retrieves a dictionary of common telemetry data."""
        if not self.connected:
            return {}
        
        heading_rad = self.get_var("PLANE_HEADING_DEGREES_TRUE")
        
        return {
            "altitude": self.get_var("INDICATED_ALTITUDE"),
            "airspeed": self.get_var("AIRSPEED_INDICATED"),
            "latitude": self.get_var("PLANE_LATITUDE"),
            "longitude": self.get_var("PLANE_LONGITUDE"),
            "ground_speed": self.get_var("GROUND_VELOCITY"),
            "vertical_speed": self.get_var("VERTICAL_SPEED"),
            "on_ground": self.get_var("SIM_ON_GROUND"),
            "heading": math.degrees(heading_rad) if heading_rad is not None else 0
        }

    def close(self):
        """Close the SimConnect connection."""
        if self.sm:
            self.sm.exit()
            self.connected = False
            logging.info("Disconnected from SimConnect.")

if __name__ == "__main__":
    # Simple test loop
    logging.basicConfig(level=logging.INFO)
    sim = SimInterface()
    if sim.connect():
        try:
            for _ in range(5):
                data = sim.get_basic_telemetry()
                print(f"Telemetry: {data}")
                time.sleep(1)
        finally:
            sim.close()
    else:
        print("MSFS not running or SimConnect unavailable.")
