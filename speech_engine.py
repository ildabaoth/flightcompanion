import pyttsx3
import threading
import queue
import logging
import pythoncom

class SpeechEngine:
    """
    A wrapper around pyttsx3 to provide an asynchronous speech engine.
    Uses a queue to ensure speech requests don't block the main telemetry loop.
    """
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logging.info("Speech Engine initialized.")

    def _run(self):
        """Worker thread loop to process speech requests."""
        while True:
            # Each item is (text, filename)
            item = self.queue.get()
            if item is None:
                break
            
            text, filename = item
            logging.info(f"DEBUG: Starting fresh speech cycle for: '{text}'" + (f" (Saving to {filename})" if filename else ""))
            
            try:
                pythoncom.CoInitialize()
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[min(1, len(voices)-1)].id)

                if filename:
                    # Save to file
                    engine.save_to_file(text, filename)
                    logging.info(f"DEBUG: Saving to file: {filename}...")
                
                # Still speak it out loud
                engine.say(text)
                engine.runAndWait()
                logging.info("DEBUG: Cycle complete.")
                
                engine.stop()
                del engine
                pythoncom.CoUninitialize()
                
            except Exception as e:
                logging.error(f"DEBUG: Error in speech cycle: {e}")
            
            self.queue.task_done()

    def say(self, text, filename=None):
        """Queue a string to be spoken and optionally saved to a file."""
        if text:
            self.queue.put((text, filename))

    def stop(self):
        """Stop the engine and its worker thread."""
        self.queue.put(None)
        self.thread.join()

if __name__ == "__main__":
    # Test block
    logging.basicConfig(level=logging.INFO)
    se = SpeechEngine()
    se.say("Hello Pilot. Copilot engine online.")
    se.say("Checking systems.")
    import time
    time.sleep(5)
    se.stop()
