import time
import logging
import threading
import requests
from sim_interface import SimInterface
from speech_engine import SpeechEngine
from copilot import Copilot
from dashboard import start_dashboard_thread, update_telemetry, get_speech_request

# Public Relay URL (User will update this after deploying to Render)
RELAY_URL = "https://fs-companion-relay.onrender.com" 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def push_to_relay(data):
    """Pushes telemetry data to the public relay server."""
    if not RELAY_URL:
        return
    try:
        requests.post(f"{RELAY_URL}/api/update", json=data, timeout=1)
    except Exception as e:
        logging.debug(f"Failed to push to relay: {e}")

def main():
    """Main application loop."""
    speech = SpeechEngine()
    sim = SimInterface()
    co = Copilot(speech)

    logging.info("Virtual Copilot for MSFS 24 starting...")
    co.welcome()

    # Start the local web dashboard
    start_dashboard_thread(port=5000)
    logging.info("Local Dashboard available at http://localhost:5000")

    connection_attempted = False

    try:
        while True:
            if not sim.connected:
                # If not connected, try to connect every 5 seconds
                if not connection_attempted or int(time.time()) % 5 == 0:
                    if sim.connect():
                        speech.say("Simulator connection established.")
                    connection_attempted = True
                else:
                    logging.info("Waiting for MSFS to start...")
                    time.sleep(1)
                    continue

            # Read telemetry
            data = sim.get_basic_telemetry()
            
            if data and data.get("altitude") is not None:
                # Update local dashboard
                update_telemetry(data)
                
                # Push to public relay in background
                threading.Thread(target=push_to_relay, args=(data,), daemon=True).start()
                
                # Check for manual speech request
                if get_speech_request():
                    logging.info("Processing manual speech request...")
                    co.report_status(data)

                # Process logic
                co.process_telemetry(data)
            else:
                # If we get None, the connection might have dropped
                logging.warning("Failed to retrieve telemetry. Connection may have dropped.")
                sim.connected = False
                speech.say("Lost connection to simulator. Re-arming.")

            # Main loop interval (e.g., 2 times per second)
            time.sleep(0.5)

    except KeyboardInterrupt:
        logging.info("Shutting down...")
        speech.say("Virtual Copilot shutting down. Goodbye.")
    finally:
        sim.close()
        speech.stop()

if __name__ == "__main__":
    main()
