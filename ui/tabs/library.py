import flet as ft
import asyncio

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

class ShimmerSkeleton(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 120
        self.height = 180
        self.bgcolor = "#222222"
        self.border_radius = 10
        self.animate = ft.Animation(duration=800, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.alignment = ft.Alignment(0, 0)
        self.content = ft.Text("🎞️", size=30, color="#444444")
        self._is_mounted = False

    def did_mount(self):
        self._is_mounted = True
        self.page.run_task(self._pulsate)

    def will_unmount(self):
        self._is_mounted = False

    async def _pulsate(self):
        while self._is_mounted:
            self.bgcolor = "#3a3a3a" if self.bgcolor == "#222222" else "#222222"
            try:
                self.update()
            except:
                pass
            await asyncio.sleep(0.8)

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

        self.content = ft.Column([self.uni_drop, self.grid], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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

        for (title_str, skeleton, img, icon), det in zip(pending, results):
            skeleton.visible = False
            
            if det and det.get("local_image_path"):
                img.src = det["local_image_path"]
                img.visible = True
            elif det and det.get("image_url"):
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
            item_type = item.get("type", "show") if isinstance(item, dict) else ("movie" if "(Film)" in item else "show")
            cached_det = self.api._cache.get(title)

            skeleton = ShimmerSkeleton()
            img = ft.Image(src="", fit=ft.BoxFit.COVER, width=120, height=180, visible=False, border_radius=10)
            icon = ft.Text("🎬", size=35, color="white54", visible=False)

            if cached_det:
                skeleton.visible = False
                if cached_det.get("local_image_path"):
                    img.src = cached_det.get("local_image_path")
                    img.visible = True
                elif cached_det.get("image_url"):
                    img.src = cached_det.get("image_url")
                    img.visible = True
                else:
                    icon.visible = True
            else:
                self._pending_posters.append((title, skeleton, img, icon))

            is_fav = self.db.is_favorite(title)
            fav_btn = ft.IconButton(
                icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
                icon_color=ft.Colors.RED if is_fav else ft.Colors.WHITE,
                icon_size=20,
                on_click=lambda e, t=title, typ=item_type, u=uni: self._toggle_fav(e, t, typ, u)
            )
            
            fav_hover = HoverContainer(content=fav_btn)

            stack = ft.Stack(
                controls=[
                    skeleton,
                    img,
                    ft.Container(icon, alignment=ft.Alignment(0, 0), width=120, height=180),
                    ft.Container(fav_hover, alignment=ft.Alignment(1, -1))
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
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=13,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                on_click=lambda e, s=title: self.switch_func(0, s)
            )
            new_cards.append(card)

        self.grid.controls = new_cards

        if not is_initial:
            self.update()
            if self._pending_posters:
                self.page.run_task(self._load_pending_posters)

    def _toggle_fav(self, e, title, item_type, universe):
        is_fav = self.db.toggle_favorite(title, item_type, universe)
        e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        e.control.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
        self.update()

    def _handle_dropdown_select(self, e):
        if e:
            e.control.value = e.data
        self._build_grid(self.uni_drop.value, is_initial=False)