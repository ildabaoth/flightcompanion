import time
import logging
from copilot import Copilot

# Mock Speech Engine for verification
class MockSpeech:
    def __init__(self):
        print("[MOCK] Speech Engine Initialized")
        
    def say(self, text):
        print(f"\n[CO-PILOT SAYS]: \"{text}\"\n")

    def stop(self):
        pass

def verify():
    print("=== MSFS Virtual Copilot Logic Verification ===")
    speech = MockSpeech()
    co = Copilot(speech)

    # 1. Start on ground
    print("Event: Pre-flight")
    co.process_telemetry({"altitude": 14, "on_ground": True, "airspeed": 0})
    time.sleep(1)

    # 2. Takeoff roll and rotation
    print("Event: Rotation and Takeoff")
    co.process_telemetry({"altitude": 100, "on_ground": False, "airspeed": 120})
    time.sleep(1)

    # 3. Climbing through checkpoints
    print("Event: Climbing through 1000ft")
    co.process_telemetry({"altitude": 1050, "on_ground": False, "airspeed": 150})
    time.sleep(1)

    print("Event: Climbing through 2000ft")
    co.process_telemetry({"altitude": 2010, "on_ground": False, "airspeed": 180})
    time.sleep(1)

    # 4. Landing
    print("Event: Landing/Touchdown")
    co.process_telemetry({"altitude": 5, "on_ground": True, "airspeed": 60})
    
    print("=== Verification Complete ===")

if __name__ == "__main__":
    verify()
