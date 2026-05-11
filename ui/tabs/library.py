import flet as ft
import threading

class LibraryTab(ft.Container):
    def __init__(self, switch_func, db, api):
        super().__init__()
        self.switch_func = switch_func
        self.db = db
        self.api = api
        self.expand = True
        self.padding = 20

        self.grid = ft.GridView(expand=True, max_extent=160, child_aspect_ratio=0.6, spacing=15)
        
        timeline_data = self.db.load_timeline()
        universes = list(timeline_data.keys())
        initial_uni = universes[0] if universes else None

        self.uni_drop = ft.Dropdown(
            options=[ft.DropdownOption(key=u, text=u) for u in universes],
            value=initial_uni, 
            width=300,
            on_select=self._handle_dropdown_select
        )

        self.content = ft.Column([self.uni_drop, self.grid], horizontal_alignment="center")

        if initial_uni:
            self._build_grid(initial_uni, is_initial=True)

    def _load_posters(self, title_str, img_container):
        det = self.api.fetch_show_details(title_str)
        if det and det.get("image_url"):
            img_container.content = ft.Image(src=det.get("image_url"), fit="contain")
            try:
                if img_container.page:
                    img_container.update()
            except Exception:
                pass

    def _build_grid(self, uni, is_initial=False):
        new_cards = []
        pending_downloads = []
        
        timeline_data = self.db.load_timeline()
        
        for item in timeline_data.get(uni, []):
            title = item if isinstance(item, str) else item.get("title", "")
            
            img_container = ft.Container(width=120, height=180, bgcolor="#333333", border_radius=10)
            
            card = ft.Container(
                content=ft.Column([
                    img_container,
                    ft.Text(
                        title, 
                        weight="bold", 
                        text_align="center",
                        size=13,
                        max_lines=2, 
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], horizontal_alignment="center"),
                on_click=lambda e, s=title: self.switch_func(0, s)
            )
            new_cards.append(card)
            pending_downloads.append((title, img_container))
            
        self.grid.controls = new_cards
        
        if not is_initial:
            if self.grid.page:
                self.grid.update()
                
        for title_str, img_cont in pending_downloads:
            threading.Thread(target=self._load_posters, args=(title_str, img_cont), daemon=True).start()

    def _handle_dropdown_select(self, e):
        e.control.value = e.data
        if e.control.page:
            e.control.update()
            
        self._build_grid(e.data, is_initial=False)