import flet as ft

class StatsTab(ft.Container):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.padding = 20
        self.expand = True
        self.visible = False
        self.content_col = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.content = self.content_col
        self.state.subscribe(self._on_message)

    def did_mount(self):
        self._build_view()

    def _on_message(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._build_view()

    def _build_view(self):
        data = self.state.db.get_analytics()
        self.content_col.controls.clear()

        movies_count = data.get("watched_movies", 0)
        shows_count = data.get("watched_shows", 0)

        movie_card = ft.Container(
            content=ft.Column([
                ft.Text("🎬 Movies", size=16, color=ft.Colors.WHITE70, weight=ft.FontWeight.BOLD),
                ft.Text(str(movies_count), size=28, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#222222", padding=20, border_radius=10, expand=True
        )

        show_card = ft.Container(
            content=ft.Column([
                ft.Text("📺 Shows", size=16, color=ft.Colors.WHITE70, weight=ft.FontWeight.BOLD),
                ft.Text(str(shows_count), size=28, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#222222", padding=20, border_radius=10, expand=True
        )

        distribution_row = ft.Row([movie_card, show_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        uni_time = data.get("universe_watch_time", {})
        chart_column = ft.Column(spacing=15)

        if uni_time:
            max_hours = max(uni_time.values()) if max(uni_time.values()) > 0 else 1

            for uni, hours in uni_time.items():
                fill_ratio = hours / max_hours
                bar_width = int(fill_ratio * 250)

                bar_container = ft.Container(
                    width=bar_width if bar_width > 5 else 5,
                    height=20,
                    bgcolor=ft.Colors.AMBER,
                    border_radius=5
                )

                row = ft.Row([
                    ft.Text(uni[:15], width=110, text_align=ft.TextAlign.RIGHT, size=13),
                    bar_container,
                    ft.Text(f"{hours:.1f} hrs", size=13, color=ft.Colors.WHITE70)
                ], alignment=ft.MainAxisAlignment.START)

                chart_column.controls.append(row)
        else:
            chart_column.controls.append(ft.Text("No watch data available yet.", color=ft.Colors.WHITE54))

        chart_panel = ft.Container(
            content=ft.Column([
                ft.Text("Time Spent per Universe", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                ft.Divider(color=ft.Colors.WHITE24),
                chart_column
            ]),
            bgcolor="#222222", padding=20, border_radius=10, width=500
        )

        self.content_col.controls.extend([
            ft.Text("Watch Distribution", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
            distribution_row,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=10),
            chart_panel
        ])

        if getattr(self, "page", None):
            try:
                self.update()
            except Exception:
                pass