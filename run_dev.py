import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_gui()

    def start_gui(self):
        # Kill proses lama kalau ada
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("\n🔄 File berubah — restart GUI...\n")
        
        # Jalankan GUI baru
        self.process = subprocess.Popen(
            [sys.executable, "testGUI.py"],
            env={**__import__('os').environ, 'QT_QPA_PLATFORM': 'xcb'}
        )

    def on_modified(self, event):
        # Hanya react ke perubahan testGUI.py
        if event.src_path.endswith("testGUI.py"):
            time.sleep(0.3)  # delay kecil biar file selesai ditulis
            self.start_gui()

if __name__ == "__main__":
    handler = ReloadHandler()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=False)
    observer.start()

    print("👀 Watching testGUI.py — simpan file untuk reload otomatis")
    print("   Ctrl+C untuk berhenti\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
    observer.join()
