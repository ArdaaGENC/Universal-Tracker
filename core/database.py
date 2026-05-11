import json
import os

class DatabaseManager:
    def __init__(self):
        self._timeline_file = os.path.join("data", "timeline.json")
        self._progress_file = os.path.join("data", "progress.json")

    def load_timeline(self):
        try:
            with open(self._timeline_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"HATA: {self._timeline_file} bulunamadı!")
            return {}

    def load_progress(self):
        if os.path.exists(self._progress_file):
            with open(self._progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_progress(self, universe_name, show_name):
        progress_data = self.load_progress()
        progress_data[universe_name] = show_name
        os.makedirs("data", exist_ok=True)
        with open(self._progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=4)