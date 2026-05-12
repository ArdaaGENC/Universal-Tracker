import flet as ft

class TrackerTab(ft.Container):
    def __init__(self, switch_func, db, api, auto_select_show=None):
        super().__init__()
        self.switch_func = switch_func
        self.db = db   
        self.api = api 
        self.alignment = ft.Alignment(0, 0)
        self.padding = 30

        self.progress_ring = ft.ProgressRing(value=0, stroke_width=8, width=90, height=90, color="amber")
        self.progress_text = ft.Text("0%", size=18, weight="bold")
        
        self.stat_watched = ft.Text("Watched: 0 / 0", size=15, weight="bold")
        self.stat_remaining = ft.Text("Remaining Shows: 0", size=14, color="white70")
        self.stat_time = ft.Text("Remaining Time: 0 Hours 0 Mins", size=14, color="green")

        ring_stack = ft.Stack([
            self.progress_ring,
            ft.Container(self.progress_text, alignment=ft.Alignment(0, 0), width=90, height=90)
        ])

        stats_panel = ft.Container(
            content=ft.Row([
                ring_stack,
                ft.Column([
                    self.stat_watched,
                    self.stat_remaining,
                    self.stat_time
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=25)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=25),
            padding=15, bgcolor="#2a2a2a", border_radius=15, width=400
        )

        self.uni_drop = ft.Dropdown(width=400, label="Universe", on_select=self._on_universe_change)

        self.filter_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="all", text="All Types"),
                ft.DropdownOption(key="movie", text="Movies Only"),
                ft.DropdownOption(key="show", text="Shows Only")
            ],
            value="all", width=190, label="Filter", on_select=self._on_filter_change
        )
        
        self.sort_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="chrono", text="Chronological"),
                ft.DropdownOption(key="release", text="Release Order")
            ],
            value="chrono", width=190, label="Sort", on_select=self._on_filter_change
        )
        
        filter_sort_row = ft.Row([self.filter_drop, self.sort_drop], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        self.show_drop = ft.Dropdown(width=400, label="Last Watched / Current Show", on_select=self._on_show_change)
        self.poster = ft.Image(src="", width=170, height=240, fit="contain", visible=False)

        self.content = ft.Column([
            stats_panel,       
            self.uni_drop,     
            filter_sort_row,   
            self.show_drop,    
            self.poster        
        ], horizontal_alignment="center", spacing=15)

        self._init_data(auto_select_show)

    def _init_data(self, auto_select_show):
        timeline_data = self.db.load_timeline()
        universes = list(timeline_data.keys())
        self.uni_drop.options = [ft.DropdownOption(key=u, text=u) for u in universes]
        
        initial_uni = universes[0] if universes else None
        if auto_select_show:
            for u, shows in timeline_data.items():
                for item in shows:
                    title = item if isinstance(item, str) else item.get("title")
                    if auto_select_show == title:
                        initial_uni = u
                        break
                        
        self.uni_drop.value = initial_uni
        self._update_dashboard(is_initial=True)

    def set_show(self, data):
        timeline_data = self.db.load_timeline()
        for u, shows in timeline_data.items():
            for item in shows:
                title = item if isinstance(item, str) else item.get("title")
                if data == title:
                    self.uni_drop.value = u
                    self.db.save_progress(u, data)
                    self._update_dashboard(is_initial=False)
                    return

    def _on_universe_change(self, e):
        if e: e.control.value = e.data
        self._update_dashboard(is_initial=False)

    def _on_filter_change(self, e):
        if e: e.control.value = e.data
        self._update_dashboard(is_initial=False)

    def _on_show_change(self, e):
        if e: e.control.value = e.data
        self.db.save_progress(self.uni_drop.value, self.show_drop.value)
        self._update_dashboard(is_initial=False)

    def _update_dashboard(self, is_initial=False):
        current_uni = self.uni_drop.value
        if not current_uni: return
        
        timeline_data = self.db.load_timeline()
        raw_shows = timeline_data.get(current_uni, [])
        
        processed = []
        for item in raw_shows:
            if isinstance(item, str):
                processed.append({"title": item, "type": "all", "chrono": 0, "release": 0, "runtime_min": 0})
            else:
                processed.append(item)
                
        current_filter = self.filter_drop.value
        if current_filter and current_filter != "all":
            processed = [s for s in processed if s.get("type", "all").lower() == current_filter]
            
        current_sort = self.sort_drop.value
        if current_sort == "chrono":
            processed = sorted(processed, key=lambda x: x.get("chrono", 0))
        elif current_sort == "release":
            processed = sorted(processed, key=lambda x: x.get("release", 0))
            
        filtered_titles = [s["title"] for s in processed]
        self.show_drop.options = [ft.DropdownOption(key=t, text=t) for t in filtered_titles]
        
        prog = self.db.load_progress()
        saved_show = prog.get(current_uni)
        
        if saved_show and saved_show in filtered_titles:
            self.show_drop.value = saved_show
        else:
            self.show_drop.value = filtered_titles[0] if filtered_titles else None

        stats = self.db.get_dynamic_stats(processed, self.show_drop.value)
        if stats:
            pct = stats["percentage"]
            self.progress_ring.value = pct / 100.0  
            self.progress_text.value = f"{int(pct)}%"
            self.stat_watched.value = f"Watched: {stats['watched_count']} / {stats['total_items']}"
            self.stat_remaining.value = f"Remaining Shows: {stats['remaining_items']}"
            self.stat_time.value = f"Remaining Time: {stats['remaining_time_str']}"

        if self.show_drop.value:
            det = self.api.fetch_show_details(self.show_drop.value)
            if det and det.get("image_url"):
                self.poster.src = det.get("image_url")
                self.poster.visible = True
            else:
                self.poster.visible = False

        if not is_initial:
            try:
                if self.page: self.page.update()
            except Exception: pass