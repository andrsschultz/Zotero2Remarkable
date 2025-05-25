import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

# Path to your .bib file
BIB_PATH = "/Users/andreasschultz/GitHub/Zotero2Remarkable/send2remarkable.bib"  # Full absolute path
BIB_PATH_ABS = os.path.abspath(BIB_PATH)  # Convert to absolute path

# Your python executable and app.py
PYTHON = "/Users/andreasschultz/GitHub/Zotero2Remarkable/.venv/bin/python"
SCRIPT = "/Users/andreasschultz/GitHub/Zotero2Remarkable/app.py"

class BibChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == BIB_PATH_ABS:
            print(f"Detected change in {BIB_PATH}, running script...")
            try:
                subprocess.run([PYTHON, SCRIPT, BIB_PATH], check=True)
                print("Script finished successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error running script: {e}")

if __name__ == "__main__":
    event_handler = BibChangeHandler()
    observer = Observer()
    # Watch the directory containing the .bib file
    watch_dir = os.path.dirname(BIB_PATH)
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    print(f"Watching {BIB_PATH} for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
