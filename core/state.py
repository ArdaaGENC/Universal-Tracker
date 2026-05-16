class AppState:
    def __init__(self, db, api, page):
        self.db = db
        self.api = api
        self.page = page
        self._listeners = []

    def subscribe(self, listener):
        self._listeners.append(listener)

    def navigate(self, tab_index, show_data=None):
        for listener in self._listeners:
            listener({"action": "NAVIGATE", "index": tab_index, "data": show_data})

    def refresh_data(self):
        for listener in self._listeners:
            listener({"action": "DATA_CHANGED"})