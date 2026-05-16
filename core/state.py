import flet as ft
import json
import os
from core.themes import THEMES

class AppState:
    def __init__(self, db, api, page):
        self.db = db
        self.api = api
        self.page = page
        self._listeners = []
        self.settings_file = os.path.join("data", "settings.json")
        self.theme_mode = "dark"
        self.theme_name = "gold"
        self._load_preferences()

    def _load_preferences(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theme_mode = data.get("theme_mode", "dark")
                    self.theme_name = data.get("theme_name", "gold")
            except:
                pass
        self.apply_theme()

    def _save_preferences(self):
        data = {
            "theme_mode": self.theme_mode,
            "theme_name": self.theme_name
        }
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except:
            pass

    def subscribe(self, listener):
        self._listeners.append(listener)

    def navigate(self, tab_index, show_data=None):
        for listener in self._listeners:
            listener({"action": "NAVIGATE", "index": tab_index, "data": show_data})

    def refresh_data(self):
        for listener in self._listeners:
            listener({"action": "DATA_CHANGED"})

    def set_theme_mode(self, mode):
        self.theme_mode = mode
        self._save_preferences()
        self.apply_theme()

    def set_theme_name(self, name):
        self.theme_name = name
        self._save_preferences()
        self.apply_theme()

    def apply_theme(self):
        self.page.theme_mode = ft.ThemeMode.DARK if self.theme_mode == "dark" else ft.ThemeMode.LIGHT
        is_dark = (self.theme_mode == "dark")
        theme_data = THEMES.get(self.theme_name, THEMES["gold"])

        custom_scheme = ft.ColorScheme(
            primary=theme_data["primary"],
            on_primary=theme_data["on_primary"],
            surface="#121212" if is_dark else "#FFFFFF",
            on_surface="#FFFFFF" if is_dark else "#000000"
        )

        self.page.theme = ft.Theme(color_scheme=custom_scheme)
        self.page.bgcolor = "#0E0E0E" if is_dark else "#F5F5F5"
        self.page.update()
        self.refresh_data()