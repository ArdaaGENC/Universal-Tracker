import flet as ft

class ManagerModalOverlay(ft.Stack):
    def __init__(self, state):
        super().__init__(expand=True, visible=False)
        self.state = state
        self._build_ui()

    def open_modal(self):
        self._load_del_drops()
        self.visible = True
        self.update()

    def _close_modal(self, e=None):
        self.visible = False
        self.update()
        self.state.page.floating_action_button.visible = True
        self.state.page.update()

    def _build_ui(self):
        self.search_results_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=15, expand=True)
        self.search_input = ft.TextField(label="Search Movies/Shows", expand=True, on_submit=self._perform_search)
        search_btn = ft.IconButton(icon=ft.Icons.SEARCH, on_click=self._perform_search)
        search_row = ft.Row([self.search_input, search_btn])

        self.search_tab = ft.Container(
            content=ft.Column([search_row, self.search_results_col], expand=True),
            padding=15, expand=True, visible=True
        )

        self.del_uni_drop = ft.Dropdown(label="Select Universe", width=250, on_select=self._on_del_uni_change)
        self.del_show_drop = ft.Dropdown(label="Select Show", width=250)
        self.new_uni_input = ft.TextField(label="New Universe Name", width=200)

        self.manage_tab = ft.Container(
            content=ft.Column([
                ft.Text("Create New Universe", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                ft.Row([self.new_uni_input, ft.ElevatedButton("Add Universe", on_click=self._add_uni_action)]),
                ft.Divider(height=25, color=ft.Colors.OUTLINE_VARIANT),
                ft.Text("Remove Data", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                self.del_uni_drop,
                ft.ElevatedButton("Delete Selected Universe", color=ft.Colors.RED, on_click=self._delete_uni_action),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                self.del_show_drop,
                ft.ElevatedButton("Delete Selected Show", color=ft.Colors.RED, on_click=self._delete_show_action)
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
            padding=15, expand=True, visible=False
        )

        def switch_dialog_tab(e):
            idx = e.control.data
            self.search_tab.visible = (idx == 0)
            self.manage_tab.visible = (idx == 1)
            for i, btn in enumerate(self.dialog_tab_buttons):
                btn.border = ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)) if i == idx else None
                btn.content.color = ft.Colors.AMBER if i == idx else ft.Colors.WHITE70
            self.update()

        self.dialog_tab_buttons = [
            ft.Container(content=ft.Text("Search & Add", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER), data=0, on_click=switch_dialog_tab, padding=10, border=ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)), ink=True),
            ft.Container(content=ft.Text("Manage DB", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70), data=1, on_click=switch_dialog_tab, padding=10, ink=True),
        ]
        dialog_tabs_row = ft.Row(self.dialog_tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        dialog_content_area = ft.Column([self.search_tab, self.manage_tab], expand=True)

        modal_header = ft.Row(
            [ft.Text("Database Manager", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.AMBER),
             ft.IconButton(icon=ft.Icons.CLOSE, icon_color=ft.Colors.WHITE70, on_click=self._close_modal)], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.modal_overlay = ft.Container(
            content=ft.Container(
                width=500, height=550, bgcolor="#2a2a2a", border_radius=15, padding=15,
                content=ft.Column([modal_header, dialog_tabs_row, ft.Divider(height=1, color=ft.Colors.WHITE24), dialog_content_area], expand=True)
            ),
            bgcolor="#CC000000", alignment=ft.Alignment(0, 0), expand=True
        )

        self.confirm_dialog_content = ft.Text("")
        self.confirm_callback_holder = []

        confirm_dialog_box = ft.Container(
            content=ft.Column([
                ft.Text("Confirm Deletion", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.RED),
                self.confirm_dialog_content,
                ft.Row([
                    ft.TextButton("Cancel", on_click=self._close_confirm_dlg),
                    ft.ElevatedButton("Delete", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=self._execute_confirm)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, spacing=20),
            bgcolor="#222222", padding=20, border_radius=10, width=400
        )

        self.confirm_overlay = ft.Container(
            content=confirm_dialog_box, bgcolor="#AA000000", alignment=ft.Alignment(0, 0), expand=True, visible=False
        )

        self.controls = [self.modal_overlay, self.confirm_overlay]

    def _perform_search(self, e=None):
        self.search_results_col.controls.clear()
        self.search_results_col.controls.append(ft.ProgressRing())
        self.update()
        
        query = self.search_input.value
        if not query:
            self.search_results_col.controls.clear()
            self.update()
            return
            
        results = self.state.api.search_tmdb_query(query)
        self.search_results_col.controls.clear()
        
        if not results:
            self.search_results_col.controls.append(ft.Text("No results found on TMDB.", color=ft.Colors.WHITE70))
            self.update()
            return
        
        universes = list(self.state.db.load_timeline().keys())
        
        for res in results:
            uni_dropdown = ft.Dropdown(options=[ft.DropdownOption(key=u, text=u) for u in universes], width=110, hint_text="Universe", text_size=12)
            chrono_input = ft.TextField(label="Order", width=60, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
            
            def add_clicked(e, r=res, d=uni_dropdown, c_inp=chrono_input):
                if not d.value: return
                release_year = int(r['year']) if r['year'] else 0
                c_val = int(c_inp.value) if c_inp.value and c_inp.value.isdigit() else None
                    
                self.state.db.add_show(d.value, r['title'], r['type'], c_val, release_year, 0)
                self.state.refresh_data()
                
                d.disabled = True
                c_inp.disabled = True
                e.control.disabled = True
                e.control.icon = ft.Icons.CHECK
                e.control.icon_color = ft.Colors.GREEN
                self.update()

            add_btn = ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.AMBER, on_click=add_clicked)
            image_control = ft.Image(src=res['image'], width=40, height=60, fit=ft.BoxFit.COVER, border_radius=5) if res['image'] else ft.Container(width=40, height=60, bgcolor="#333333", border_radius=5)
            
            row = ft.Row([
                image_control,
                ft.Column([
                    ft.Text(res['title'], weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{res['type'].capitalize()} • {res['year']}", size=11, color=ft.Colors.WHITE70)
                ], spacing=2, expand=True),
                uni_dropdown, chrono_input, add_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            self.search_results_col.controls.append(row)
        self.update()

    def _load_del_drops(self):
        timeline = self.state.db.load_timeline()
        unis = list(timeline.keys())
        self.del_uni_drop.options = [ft.DropdownOption(key=u, text=u) for u in unis]
        
        if not self.del_uni_drop.value or self.del_uni_drop.value not in unis:
            self.del_uni_drop.value = unis[0] if unis else None
        
        if self.del_uni_drop.value:
            shows = timeline.get(self.del_uni_drop.value, [])
            show_titles = [s["title"] for s in shows] if shows else []
            self.del_show_drop.options = [ft.DropdownOption(key=t, text=t) for t in show_titles]
            if not self.del_show_drop.value or self.del_show_drop.value not in show_titles:
                self.del_show_drop.value = show_titles[0] if show_titles else None
        else:
            self.del_show_drop.options = []
            self.del_show_drop.value = None

    def _on_del_uni_change(self, e):
        if e: e.control.value = e.data
        self._load_del_drops()
        self.update()

    def _show_confirm_dialog(self, content_text, confirm_callback):
        self.confirm_dialog_content.value = content_text
        self.confirm_callback_holder.clear()
        self.confirm_callback_holder.append(confirm_callback)
        self.confirm_overlay.visible = True
        self.update()

    def _close_confirm_dlg(self, e):
        self.confirm_overlay.visible = False
        self.update()

    def _execute_confirm(self, e):
        self.confirm_overlay.visible = False
        if self.confirm_callback_holder:
            self.confirm_callback_holder[0]()
        self.update()

    def _delete_show_action(self, e):
        if self.del_uni_drop.value and self.del_show_drop.value:
            def do_delete():
                self.state.db.delete_show(self.del_uni_drop.value, self.del_show_drop.value)
                self.state.refresh_data()
                self._load_del_drops()
            self._show_confirm_dialog(f"Are you sure you want to delete '{self.del_show_drop.value}'?", do_delete)

    def _delete_uni_action(self, e):
        if self.del_uni_drop.value:
            def do_delete():
                self.state.db.delete_universe(self.del_uni_drop.value)
                self.state.refresh_data()
                self._load_del_drops()
            self._show_confirm_dialog(f"Are you sure you want to delete the entire universe '{self.del_uni_drop.value}'?", do_delete)

    def _add_uni_action(self, e):
        if self.new_uni_input.value:
            self.state.db.add_universe(self.new_uni_input.value)
            self.new_uni_input.value = ""
            self.state.refresh_data()
            self._load_del_drops()
            self.update()