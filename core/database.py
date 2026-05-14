import sqlite3
import json
import os

class DatabaseManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.db_path = os.path.join("data", "tracker.db")
        self._init_db()
        self._auto_migrate()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS universes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
            c.execute("CREATE TABLE IF NOT EXISTS shows (id INTEGER PRIMARY KEY AUTOINCREMENT, universe_id INTEGER, title TEXT, type TEXT, chrono INTEGER, release INTEGER, runtime_min INTEGER, FOREIGN KEY(universe_id) REFERENCES universes(id))")
            c.execute("CREATE TABLE IF NOT EXISTS progress (universe_name TEXT PRIMARY KEY, show_title TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS favorites (title TEXT PRIMARY KEY, type TEXT, universe TEXT)")
            conn.commit()

    def _auto_migrate(self):
        timeline_file = os.path.join("data", "timeline.json")
        progress_file = os.path.join("data", "progress.json")
        favorites_file = os.path.join("data", "favorites.json")

        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM universes")
            if c.fetchone()[0] == 0 and os.path.exists(timeline_file):
                with open(timeline_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for uni, shows in data.items():
                        c.execute("INSERT OR IGNORE INTO universes (name) VALUES (?)", (uni,))
                        c.execute("SELECT id FROM universes WHERE name = ?", (uni,))
                        uni_id = c.fetchone()[0]
                        for s in shows:
                            if isinstance(s, dict):
                                c.execute("INSERT INTO shows (universe_id, title, type, chrono, release, runtime_min) VALUES (?, ?, ?, ?, ?, ?)",
                                          (uni_id, s.get("title"), s.get("type", "show"), s.get("chrono", 0), s.get("release", 0), s.get("runtime_min", 0)))
                            else:
                                t = "movie" if "(Film)" in s else "show"
                                c.execute("INSERT INTO shows (universe_id, title, type, chrono, release, runtime_min) VALUES (?, ?, ?, ?, ?, ?)",
                                          (uni_id, s, t, 0, 0, 0))

                if os.path.exists(progress_file):
                    with open(progress_file, "r", encoding="utf-8") as f:
                        prog_data = json.load(f)
                        for u, s in prog_data.items():
                            c.execute("INSERT OR REPLACE INTO progress (universe_name, show_title) VALUES (?, ?)", (u, s))

                if os.path.exists(favorites_file):
                    with open(favorites_file, "r", encoding="utf-8") as f:
                        fav_data = json.load(f)
                        for title, details in fav_data.items():
                            c.execute("INSERT OR REPLACE INTO favorites (title, type, universe) VALUES (?, ?, ?)",
                                      (title, details.get("type"), details.get("universe")))
                conn.commit()

    def load_timeline(self):
        data = {}
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM universes")
            universes = c.fetchall()
            for uid, uname in universes:
                c.execute("SELECT title, type, chrono, release, runtime_min FROM shows WHERE universe_id = ? ORDER BY chrono ASC", (uid,))
                shows = c.fetchall()
                data[uname] = []
                for s in shows:
                    data[uname].append({
                        "title": s[0],
                        "type": s[1],
                        "chrono": s[2],
                        "release": s[3],
                        "runtime_min": s[4]
                    })
        return data

    def load_progress(self):
        data = {}
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT universe_name, show_title FROM progress")
            for row in c.fetchall():
                data[row[0]] = row[1]
        return data

    def save_progress(self, universe_name, show_name):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO progress (universe_name, show_title) VALUES (?, ?)", (universe_name, show_name))
            conn.commit()

    def load_favorites(self):
        data = {}
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT title, type, universe FROM favorites")
            for row in c.fetchall():
                data[row[0]] = {"title": row[0], "type": row[1], "universe": row[2]}
        return data

    def toggle_favorite(self, title, item_type, universe):
        is_fav = False
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT title FROM favorites WHERE title = ?", (title,))
            if c.fetchone():
                c.execute("DELETE FROM favorites WHERE title = ?", (title,))
            else:
                c.execute("INSERT INTO favorites (title, type, universe) VALUES (?, ?, ?)", (title, item_type, universe))
                is_fav = True
            conn.commit()
        return is_fav

    def is_favorite(self, title):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT title FROM favorites WHERE title = ?", (title,))
            return c.fetchone() is not None

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

    def add_universe(self, name):
        with self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO universes (name) VALUES (?)", (name,))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def delete_universe(self, name):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM universes WHERE name = ?", (name,))
            row = c.fetchone()
            if row:
                uni_id = row[0]
                c.execute("DELETE FROM shows WHERE universe_id = ?", (uni_id,))
                c.execute("DELETE FROM universes WHERE id = ?", (uni_id,))
                c.execute("DELETE FROM progress WHERE universe_name = ?", (name,))
                conn.commit()

    def add_show(self, universe_name, title, item_type, chrono, release_year, runtime_min):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM universes WHERE name = ?", (universe_name,))
            row = c.fetchone()
            if row:
                uni_id = row[0]
                if chrono is None:
                    c.execute("SELECT MAX(chrono) FROM shows WHERE universe_id = ?", (uni_id,))
                    max_val = c.fetchone()[0]
                    chrono = (max_val or 0) + 1
                else:
                    c.execute("UPDATE shows SET chrono = chrono + 1 WHERE universe_id = ? AND chrono >= ?", (uni_id, chrono))
                    
                c.execute("INSERT INTO shows (universe_id, title, type, chrono, release, runtime_min) VALUES (?, ?, ?, ?, ?, ?)",
                          (uni_id, title, item_type, chrono, release_year, runtime_min))
                conn.commit()

    def delete_show(self, universe_name, title):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM universes WHERE name = ?", (universe_name,))
            row = c.fetchone()
            if row:
                uni_id = row[0]
                c.execute("DELETE FROM shows WHERE universe_id = ? AND title = ?", (uni_id, title))
                conn.commit()