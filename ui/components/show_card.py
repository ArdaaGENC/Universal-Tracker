import flet as ft
import asyncio

class HoverContainer(ft.Container):
    def __init__(self, content, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.shape = ft.BoxShape.CIRCLE
        self.bgcolor = ft.Colors.TRANSPARENT
        self.animate_color = 300
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        self.bgcolor = "#26FFFFFF" if e.data == "true" else ft.Colors.TRANSPARENT
        self.update()

class ShimmerSkeleton(ft.Container):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
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

class ShowCard(ft.Container):
    def __init__(self, state, title, item_type, universe, is_fav, score, is_watchlist, width, height, tmdb_id=None, initial_img_src=None, show_skeleton=True):
        super().__init__()
        self.state = state
        self.title_text = title
        self.item_type = item_type
        self.universe = universe
        self.tmdb_id = tmdb_id
        
        self.skeleton = ShimmerSkeleton(width, height) if show_skeleton else ft.Container()
        self.skeleton.visible = show_skeleton and not initial_img_src
        
        self.img = ft.Image(src=initial_img_src or "", fit=ft.BoxFit.COVER, width=width, height=height, border_radius=10)
        self.img.visible = bool(initial_img_src)
        
        self.icon = ft.Container(ft.Text("🎬", size=35, color="white54"), alignment=ft.Alignment(0,0), width=width, height=height)
        self.icon.visible = False

        fav_btn = ft.IconButton(
            icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
            icon_color=ft.Colors.RED if is_fav else ft.Colors.WHITE,
            icon_size=max(16, int(width * 0.16)),
            on_click=self._toggle_fav
        )
        fav_hover = HoverContainer(content=fav_btn, right=0, top=0)

        watch_btn = ft.IconButton(
            icon=ft.Icons.BOOKMARK if is_watchlist else ft.Icons.BOOKMARK_BORDER,
            icon_color=ft.Colors.BLUE if is_watchlist else ft.Colors.WHITE,
            icon_size=max(16, int(width * 0.16)),
            on_click=self._toggle_watchlist
        )
        watch_hover = HoverContainer(content=watch_btn, right=0, top=int(width * 0.25))

        rate_btn = ft.PopupMenuButton(
            icon=ft.Icons.STAR if score > 0 else ft.Icons.STAR_BORDER,
            icon_color=ft.Colors.AMBER if score > 0 else ft.Colors.WHITE,
            icon_size=max(16, int(width * 0.16)),
            items=[ft.PopupMenuItem(content=ft.Text("Clear"), data=0, on_click=self._on_rate)] +
                  [ft.PopupMenuItem(content=ft.Text(f"{i} ⭐"), data=i, on_click=self._on_rate) for i in range(1, 11)]
        )
        rate_hover = HoverContainer(content=rate_btn, left=0, top=0)

        rate_badge = ft.Container(
            content=ft.Text(f"{score}", size=10 if width < 120 else 11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor="#CC000000",
            padding=ft.Padding(left=4, top=2, right=4, bottom=2),
            border_radius=5,
            left=5, top=int(width * 0.25) + 5,
            visible=score > 0
        )

        ctx_menu = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                icon_color=ft.Colors.WHITE,
                icon_size=max(30, int(width * 0.25)),
                on_click=self._open_tmdb
            ),
            bgcolor="#AA000000",
            alignment=ft.Alignment(0, 0),
            width=width, height=height, border_radius=10,
            visible=False
        )

        detector = ft.GestureDetector(
            on_secondary_tap=lambda e: self._toggle_ctx(ctx_menu),
            on_tap=lambda e: self._handle_tap(ctx_menu),
            content=ft.Stack(
                controls=[
                    self.skeleton,
                    self.img,
                    self.icon,
                    fav_hover,
                    watch_hover,
                    rate_hover,
                    rate_badge,
                    ctx_menu
                ],
                width=width, height=height
            )
        )

        img_container = ft.Container(
            width=width, height=height, bgcolor="#333333", border_radius=10,
            content=detector
        )

        self.content = ft.Column([
            img_container,
            ft.Text(
                self.title_text,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                size=12 if width < 120 else 13,
                max_lines=2,
                width=width,
                overflow=ft.TextOverflow.ELLIPSIS
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        self.tooltip = self.title_text

    def _toggle_fav(self, e):
        self.state.db.toggle_favorite(self.title_text, self.item_type, self.universe)
        self.state.refresh_data()

    def _toggle_watchlist(self, e):
        self.state.db.toggle_watchlist(self.title_text, self.item_type, self.universe)
        self.state.refresh_data()

    def _on_rate(self, e):
        self.state.db.set_rating(self.title_text, e.control.data)
        self.state.refresh_data()

    def _toggle_ctx(self, ctx_menu):
        ctx_menu.visible = not ctx_menu.visible
        self.update()

    def _handle_tap(self, ctx_menu):
        if ctx_menu.visible:
            ctx_menu.visible = False
            self.update()
        else:
            self.state.navigate(0, self.title_text)

    def _open_tmdb(self, e):
        e.control.parent.visible = False
        self.update()
        tid = self.tmdb_id
        mtype = self.item_type
        if not tid:
            det = self.state.api.fetch_show_details(self.title_text)
            if det and det.get("tmdb_id"):
                tid = det.get("tmdb_id")
                mtype = det.get("media_type", mtype)
        if tid:
            url = f"https://www.themoviedb.org/{mtype}/{tid}"
            async def launch():
                await e.page.launch_url(url)
            e.page.run_task(launch)

    def set_image(self, det):
        self.skeleton.visible = False
        if det and det.get("local_image_path"):
            self.img.src = det.get("local_image_path")
            self.img.visible = True
        elif det and det.get("image_url"):
            self.img.src = det.get("image_url")
            self.img.visible = True
        else:
            self.icon.visible = True
        
        if det and det.get("tmdb_id"):
            self.tmdb_id = det.get("tmdb_id")
            self.item_type = det.get("media_type", self.item_type)

        try:
            self.update()
        except:
            pass