import flet as ft
from ui.tabs.tracker import create_tracker_tab
from ui.tabs.library import create_library_tab

def run():
    def main(page: ft.Page):
        page.title = "Universal Tracker"
        page.window.width = 550
        page.window.height = 700
        page.window.min_width = 450
        page.window.min_height = 650
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.bgcolor = "#1a1a1a"

        title = ft.Text("🎬 Universal Tracker", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)

        tabs = ft.Tabs(
            selected_index=0,
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Tracker"),
                            ft.Tab(label="Library"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            create_tracker_tab(),
                            create_library_tab(),
                        ]
                    )
                ]
            )
        )

        page.add(title, tabs)

    ft.app(target=main)