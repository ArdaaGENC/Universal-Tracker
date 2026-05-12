import flet as ft
import asyncio

class LibraryTab(ft.Container):
    def __init__(self, switch_func, db, api):
        super().__init__()
        self.switch_func = switch_func
        self.db = db
        self.api = api
        self.expand = True
        self.padding = 20
        self._pending_posters = []

        self.isolated = True

        self.grid = ft.GridView(expand=True, max_extent=160, child_aspect_ratio=0.6, spacing=15)

        timeline_data = self.db.load_timeline()
        self.universes = list(timeline_data.keys())
        initial_uni = self.universes[0] if self.universes else None

        self.uni_drop = ft.Dropdown(
            label="Universe",
            options=[ft.DropdownOption(key=u, text=u) for u in self.universes],
            value=initial_uni,
            width=300,
            on_select=self._handle_dropdown_select
        )

        self.content = ft.Column([self.uni_drop, self.grid], horizontal_alignment="center")

        if initial_uni:
            self._build_grid(initial_uni, is_initial=True)

    def did_mount(self):
        if self._pending_posters:
            self.page.run_task(self._load_pending_posters)

    async def _load_pending_posters(self):
        pending = list(self._pending_posters)
        self._pending_posters.clear()

        results = await asyncio.gather(
            *[asyncio.to_thread(self.api.fetch_show_details, title) for title, _, _, _ in pending]
        )

        for (title_str, ring, img, icon), det in zip(pending, results):
            ring.visible = False
            if det and det.get("image_url"):
                img.src = det["image_url"]
                img.visible = True
            else:
                icon.visible = True

        self.update()

    def _build_grid(self, uni, is_initial=False):
        new_cards = []
        self._pending_posters = []
        timeline_data = self.db.load_timeline()

        for item in timeline_data.get(uni, []):
            title = item if isinstance(item, str) else item.get("title", "")
            cached_det = self.api._cache.get(title)

            ring = ft.ProgressRing(width=30, height=30, stroke_width=3, color="amber")
            img = ft.Image(src="", fit="contain", width=120, height=180, visible=False)
            icon = ft.Text("🎬", size=35, color="white54", visible=False)

            if cached_det:
                ring.visible = False
                if cached_det.get("image_url"):
                    img.src = cached_det.get("image_url")
                    img.visible = True
                else:
                    icon.visible = True
            else:
                self._pending_posters.append((title, ring, img, icon))

            stack = ft.Stack(
                controls=[
                    ft.Container(ring, alignment=ft.Alignment(0, 0), width=120, height=180),
                    img,
                    ft.Container(icon, alignment=ft.Alignment(0, 0), width=120, height=180)
                ]
            )

            img_container = ft.Container(
                width=120, height=180, bgcolor="#333333", border_radius=10,
                content=stack
            )

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

        self.grid.controls = new_cards

        if not is_initial:
            self.update()
            if self._pending_posters:
                self.page.run_task(self._load_pending_posters)

    def _handle_dropdown_select(self, e):
        if e:
            e.control.value = e.data
        self._build_grid(self.uni_drop.value, is_initial=False)