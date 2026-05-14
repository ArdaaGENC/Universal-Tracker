import flet as ft

class HoverContainer(ft.Container):
    def __init__(self, content):
        super().__init__()
        self.content = content
        self.shape = ft.BoxShape.CIRCLE
        self.bgcolor = ft.Colors.TRANSPARENT
        self.animate_color = 300
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        self.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.WHITE) if e.data == "true" else ft.Colors.TRANSPARENT
        self.update()

class TrackerTab(ft.Container):
    def __init__(self, switch_func, db, api, auto_select_show=None):
        super().__init__()
        self.switch_func = switch_func
        self.db = db   
        self.api = api 
        self.alignment = ft.Alignment(0, 0)
        self.padding = 30
        self.expand = True

        self.progress_ring = ft.ProgressRing(value=0, stroke_width=8, width=90, height=90, color=ft.Colors.AMBER)
        self.progress_text = ft.Text("0%", size=18, weight=ft.FontWeight.BOLD)
        
        self.stat_watched = ft.Text("Watched: 0 / 0", size=15, weight=ft.FontWeight.BOLD)
        self.stat_remaining = ft.Text("Remaining Shows: 0", size=14, color=ft.Colors.WHITE70)
        self.stat_time = ft.Text("Remaining Time: 0 Hours 0 Mins", size=14, color=ft.Colors.GREEN)

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
        
        self.poster_img = ft.Image(src="", width=170, height=240, fit=ft.BoxFit.COVER, border_radius=10, visible=False)
        self.main_fav_btn = ft.IconButton(
            icon=ft.Icons.FAVORITE_BORDER,
            icon_color=ft.Colors.WHITE,
            icon_size=25,
            on_click=self._toggle_main_fav
        )
        
        self.main_fav_wrapper = HoverContainer(content=self.main_fav_btn)
        self.main_fav_wrapper.visible = False
        
        self.poster_stack = ft.Stack(
            controls=[
                self.poster_img,
                ft.Container(self.main_fav_wrapper, alignment=ft.Alignment(1, -1))
            ],
            width=170, height=240
        )
        
        self.recommendations_container = ft.Container()

        self.content = ft.Column([
            stats_panel,       
            self.uni_drop,     
            filter_sort_row,   
            self.show_drop,    
            self.poster_stack,
            self.recommendations_container 
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, scroll=ft.ScrollMode.ADAPTIVE)

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

    def _toggle_main_fav(self, e):
        title = self.show_drop.value
        uni = self.uni_drop.value
        timeline_data = self.db.load_timeline()
        raw_shows = timeline_data.get(uni, [])
        item_type = "show"
        
        for item in raw_shows:
            if isinstance(item, dict) and item.get("title") == title:
                item_type = item.get("type", "show")
                break
            elif isinstance(item, str) and title in item:
                item_type = "movie" if "(Film)" in item else "show"
                break
                
        is_fav = self.db.toggle_favorite(title, item_type, uni)
        self.main_fav_btn.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        self.main_fav_btn.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
        self.update()

    def _toggle_rec_fav(self, e, title, item_type):
        is_fav = self.db.toggle_favorite(title, item_type, "Unknown")
        e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        e.control.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
        self.update()

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
            is_fav = self.db.is_favorite(self.show_drop.value)
            
            self.main_fav_btn.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
            self.main_fav_btn.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
            self.main_fav_wrapper.visible = True
            
            if det and det.get("image_url"):
                self.poster_img.src = det.get("image_url")
                self.poster_img.visible = True
            else:
                self.poster_img.visible = False
                
            tmdb_id = det.get("tmdb_id")
            media_type = det.get("media_type", "movie")
            self.recommendations_container.content = self._build_recommendations_ui(tmdb_id, media_type)
        else:
            self.recommendations_container.content = ft.Container()
            self.main_fav_wrapper.visible = False
            self.poster_img.visible = False

        if not is_initial:
            try:
                if self.page: self.page.update()
            except Exception: pass

    def _build_recommendations_ui(self, tmdb_id, media_type):
        recs = self.api.get_recommendations(tmdb_id, media_type)
        
        if not recs:
            return ft.Container() 

        rec_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        
        for rec in recs:
            img_src = rec.get("image")
            title = rec.get("title")
            rec_type = rec.get("type", "movie")
            is_fav = self.db.is_favorite(title)
            
            fav_btn = ft.IconButton(
                icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
                icon_color=ft.Colors.RED if is_fav else ft.Colors.WHITE,
                icon_size=16,
                on_click=lambda e, t=title, typ=rec_type: self._toggle_rec_fav(e, t, typ)
            )
            
            fav_hover = HoverContainer(content=fav_btn)
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Stack(
                            controls=[
                                ft.Image(
                                    src=img_src, 
                                    width=100, 
                                    height=150, 
                                    fit=ft.BoxFit.COVER, 
                                    border_radius=8
                                ) if img_src else ft.Container(
                                    width=100, 
                                    height=150, 
                                    bgcolor=ft.Colors.SURFACE_VARIANT, 
                                    border_radius=8
                                ),
                                ft.Container(fav_hover, alignment=ft.Alignment(1, -1))
                            ]
                        ),
                        ft.Text(
                            title, 
                            size=12, 
                            text_align=ft.TextAlign.CENTER, 
                            max_lines=2, 
                            width=100,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                tooltip=title
            )
            rec_row.controls.append(card)

        return ft.Column(
            controls=[
                ft.Divider(height=20, color=ft.Colors.OUTLINE_VARIANT),
                ft.Text("Similar Shows", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                rec_row
            ],
            spacing=10
        )