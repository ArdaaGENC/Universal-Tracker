import flet as ft
import asyncio
from ui.components.show_card import ShowCard

class FavoritesTab(ft.Container):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.expand = True
        self.padding = 20
        self._pending_posters = []
        self.state.subscribe(self._on_message)

        self.filter_drop = ft.Dropdown(
            label="Filter",
            options=[
                ft.DropdownOption(key="all", text="All"),
                ft.DropdownOption(key="movie", text="Movies"),
                ft.DropdownOption(key="show", text="Shows")
            ],
            value="all", width=200, on_select=self._refresh_view
        )

        self.group_drop = ft.Dropdown(
            label="Group By",
            options=[
                ft.DropdownOption(key="none", text="None"),
                ft.DropdownOption(key="universe", text="Universe")
            ],
            value="none", width=200, on_select=self._refresh_view
        )

        self.controls_row = ft.Row([self.filter_drop, self.group_drop], alignment=ft.MainAxisAlignment.CENTER)
        self.content_col = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=20)
        self.content = ft.Column([self.controls_row, self.content_col], expand=True)

    def _on_message(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._build_view()

    def did_mount(self):
        self._build_view()

    def _refresh_view(self, e=None):
        if e: e.control.value = e.data
        self._build_view()

    def _build_view(self):
        favs = self.state.db.load_favorites()
        timeline = self.state.db.load_timeline()
        self.content_col.controls.clear()
        self._pending_posters.clear()

        f_val = self.filter_drop.value
        filtered_favs = {}
        for k, v in favs.items():
            current_uni = self._get_current_universe(k, timeline)
            v["universe"] = current_uni
            if f_val == "all" or v.get("type", "show") == f_val:
                filtered_favs[k] = v

        if not filtered_favs:
            self.content_col.controls.append(ft.Container(content=ft.Text("No favorites found.", color=ft.Colors.WHITE70, size=16), alignment=ft.Alignment(0, 0), expand=True))
            self.update()
            return

        g_val = self.group_drop.value
        
        if g_val == "none":
            grid = ft.GridView(max_extent=160, child_aspect_ratio=0.6, spacing=15, run_spacing=15)
            for k, v in filtered_favs.items():
                grid.controls.append(self._create_card(v))
            self.content_col.controls.append(grid)
        else:
            grouped = {}
            for k, v in filtered_favs.items():
                uni = v.get("universe", "Unknown")
                if uni not in grouped: grouped[uni] = []
                grouped[uni].append(v)
            
            for uni, items in grouped.items():
                self.content_col.controls.append(ft.Text(uni, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER))
                grid = ft.GridView(max_extent=160, child_aspect_ratio=0.6, spacing=15, run_spacing=15)
                for v in items:
                    grid.controls.append(self._create_card(v))
                self.content_col.controls.append(grid)

        self.update()
        if self._pending_posters:
            self.state.page.run_task(self._load_pending_posters)

    def _get_current_universe(self, title, timeline):
        for uni, items in timeline.items():
            for item in items:
                item_title = item if isinstance(item, str) else item.get("title")
                if item_title == title: return uni
        return "Unknown"

    def _create_card(self, item):
        title = item["title"]
        cached_det = self.state.api._cache.get(title)

        card = ShowCard(
            state=self.state,
            title=title,
            item_type=item.get("type", "show"),
            universe=item.get("universe", "Unknown"),
            is_fav=True,
            score=self.state.db.get_rating(title),
            width=120,
            height=180,
            initial_img_src=cached_det.get("local_image_path") or cached_det.get("image_url") if cached_det else None,
            show_skeleton=not bool(cached_det)
        )

        if cached_det and not card.img.src:
            card.icon.visible = True
        elif not cached_det:
            self._pending_posters.append((title, card))

        return card

    async def _load_pending_posters(self):
        pending = list(self._pending_posters)
        self._pending_posters.clear()

        results = await asyncio.gather(
            *[asyncio.to_thread(self.state.api.fetch_show_details, title) for title, card in pending]
        )

        for (title_str, card), det in zip(pending, results):
            card.set_image(det)

        self.update()