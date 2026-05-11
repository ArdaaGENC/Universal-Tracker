import flet as ft

class TrackerTab(ft.Container):
    def __init__(self, switch_func, db, api, auto_select_show=None):
        super().__init__()
        self.switch_func = switch_func
        self.db = db   
        self.api = api 
        self.alignment = ft.Alignment(0, 0)
        self.padding = 40

        timeline_data = self.db.load_timeline()
        universes = list(timeline_data.keys())
        initial_uni = universes[0] if universes else None
        
        if auto_select_show:
            for u, shows in timeline_data.items():
                for item in shows:
                    title = item if isinstance(item, str) else item.get("title")
                    if auto_select_show == title:
                        initial_uni = u
                        break

        self.uni_drop = ft.Dropdown(
            options=[ft.DropdownOption(key=u, text=u) for u in universes], 
            value=initial_uni, width=300, label="Universe",
            on_select=self._update_list
        )
        
        self.filter_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="all", text="All Types"),
                ft.DropdownOption(key="movie", text="Movies Only"),
                ft.DropdownOption(key="show", text="Shows Only")
            ],
            value="all", width=145, label="Filter",
            on_select=self._update_list
        )
        
        self.sort_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="chrono", text="Chronological"),
                ft.DropdownOption(key="release", text="Release Order")
            ],
            value="chrono", width=145, label="Sort",
            on_select=self._update_list
        )

        self.show_drop = ft.Dropdown(width=300, label="Show")
        self.res_label = ft.Text("", size=18, weight="bold", color="green")
        self.poster = ft.Image(src="", width=160, height=230, fit="contain", visible=False)

        filter_sort_row = ft.Row([self.filter_drop, self.sort_drop], alignment=ft.MainAxisAlignment.CENTER)

        self.content = ft.Column([
            self.uni_drop, 
            filter_sort_row, 
            self.show_drop,
            ft.ElevatedButton("FIND NEXT", bgcolor="amber", color="black", on_click=self._find_next, width=300),
            self.res_label, self.poster
        ], horizontal_alignment="center", spacing=20)

        self._update_list_internal(force_select=auto_select_show, is_initial=True)

    def set_show(self, data):
        self._update_list_internal(force_select=data)
        try:
            if self.page:
                self.page.update()
        except Exception:
            pass

    def _update_list(self, e):
        if e:
            e.control.value = e.data
        self._update_list_internal()

    def _update_list_internal(self, force_select=None, is_initial=False):
        current_uni = self.uni_drop.value
        if not current_uni: 
            return
            
        timeline_data = self.db.load_timeline()
        raw_shows = timeline_data.get(current_uni, [])
        processed = []
        
        for item in raw_shows:
            if isinstance(item, str):
                processed.append({"title": item, "type": "all", "chrono": 0, "release": 0})
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
        
        self.show_drop.options.clear()
        for t in filtered_titles:
            self.show_drop.options.append(ft.DropdownOption(key=t, text=t))
            
        prog = self.db.load_progress()
        saved_val = prog.get(current_uni, "")
        
        if force_select and force_select in filtered_titles:
            self.show_drop.value = force_select
        elif saved_val in filtered_titles:
            self.show_drop.value = saved_val
        else:
            self.show_drop.value = filtered_titles[0] if filtered_titles else None
            
        self.res_label.value = ""
        self.poster.visible = False
        
        if not is_initial:
            try:
                if self.page:
                    self.page.update()
            except Exception:
                pass

    def _find_next(self, e):
        current_titles = [opt.key for opt in self.show_drop.options]
        
        if self.show_drop.value in current_titles:
            idx = current_titles.index(self.show_drop.value)
            if idx + 1 < len(current_titles):
                nxt = current_titles[idx + 1]
                self.res_label.value = f"Next: {nxt}"
                det = self.api.fetch_show_details(nxt)
                if det and det.get("image_url"):
                    self.poster.src = det.get("image_url")
                    self.poster.visible = True
            else:
                self.res_label.value = "🎉 List Finished!"
                self.poster.visible = False
            
            self.db.save_progress(self.uni_drop.value, self.show_drop.value)
            try:
                if self.page:
                    self.page.update()
            except Exception:
                pass