import json
import os

class DatabaseManager:
    def __init__(self):
        self._timeline_file = os.path.join("data", "timeline.json")
        self._progress_file = os.path.join("data", "progress.json")
        self._favorites_file = os.path.join("data", "favorites.json")

    def load_timeline(self):
        try:
            with open(self._timeline_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"ERROR: {self._timeline_file} not found!")
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

    def load_favorites(self):
        if os.path.exists(self._favorites_file):
            with open(self._favorites_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_favorites(self, fav_data):
        os.makedirs("data", exist_ok=True)
        with open(self._favorites_file, "w", encoding="utf-8") as f:
            json.dump(fav_data, f, indent=4)

    def toggle_favorite(self, title, item_type, universe):
        favs = self.load_favorites()
        if title in favs:
            del favs[title]
            is_fav = False
        else:
            favs[title] = {"title": title, "type": item_type, "universe": universe}
            is_fav = True
        self.save_favorites(favs)
        return is_fav

    def is_favorite(self, title):
        favs = self.load_favorites()
        return title in favs

    def get_dynamic_stats(self, processed_list, current_show):
        total_items = len(processed_list)
        if total_items == 0:
            return {
                "total_items": 0, "watched_count": 0, "remaining_items": 0,
                "remaining_time_str": "0 Hours 0 Mins", "percentage": 0
            }
            
        current_index = -1
        for i, s in enumerate(processed_list):
            if s.get("title") == current_show:
                current_index = i
                break
                
        if current_index == -1:
            watched_count = 0
            remaining_minutes = sum(s.get("runtime_min", 0) for s in processed_list)
        else:
            watched_count = current_index + 1
            remaining_minutes = sum(s.get("runtime_min", 0) for s in processed_list[current_index+1:])
            
        hours = remaining_minutes // 60
        mins = remaining_minutes % 60
        percentage = (watched_count / total_items) * 100 if total_items > 0 else 0
        
        return {
            "total_items": total_items,
            "watched_count": watched_count,
            "remaining_items": total_items - watched_count,
            "remaining_time_str": f"{hours} Hours {mins} Mins",
            "percentage": percentage
        }