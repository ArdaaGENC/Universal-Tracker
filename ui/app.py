import flet as ft
from ui.tabs.tracker import TrackerTab
from ui.tabs.library import LibraryTab
from core.database import DatabaseManager
from core.api import APIClient

def run():
    db_manager = DatabaseManager()
    api_client = APIClient(db_manager)

    def main(page: ft.Page):
        page.title = "Universal Tracker"
        page.window.width = 550
        page.window.height = 800
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#1a1a1a"
        page.horizontal_alignment = "center"

        title = ft.Text("🎬 Universal Tracker", size=26, weight="bold", color="amber")

        def switch_to_tab(index, data=None):
            tabs.selected_index = index
            if data and index == 0:
                tracker_tab.set_show(data)
            if page:
                page.update()

        tracker_tab = TrackerTab(switch_func=switch_to_tab, db=db_manager, api=api_client)
        library_tab = LibraryTab(switch_func=switch_to_tab, db=db_manager, api=api_client)

        tab_view = ft.TabBarView(
            expand=True,
            controls=[tracker_tab, library_tab]
        )

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
                    tab_view
                ]
            )
        )

        page.add(title, tabs)

    ft.app(target=main)