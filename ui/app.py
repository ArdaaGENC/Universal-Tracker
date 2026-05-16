import flet as ft
from core.database import DatabaseManager
from core.api import APIClient
from core.state import AppState
from ui.tabs.tracker import TrackerTab
from ui.tabs.library import LibraryTab
from ui.tabs.favorites import FavoritesTab
from ui.tabs.watchlist import WatchlistTab
from ui.tabs.stats import StatsTab
from ui.components.manager_modal import ManagerModalOverlay
from ui.components.settings_modal import SettingsModalOverlay

def run():
    db_manager = DatabaseManager()
    api_client = APIClient(db_manager)

    def main(page: ft.Page):
        page.title = "Universal Tracker"
        page.window.width = 550
        page.window.height = 800
        page.padding = 0

        state = AppState(db_manager, api_client, page)

        title = ft.Text("Universal Tracker", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
        
        settings_modal = SettingsModalOverlay(state)
        settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS, 
            icon_color=ft.Colors.PRIMARY, 
            on_click=lambda e: settings_modal.open_modal()
        )
        
        top_row = ft.Row([title, settings_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        tracker_tab = TrackerTab(state)
        library_tab = LibraryTab(state)
        favorites_tab = FavoritesTab(state)
        watchlist_tab = WatchlistTab(state)
        stats_tab = StatsTab(state)

        main_content_area = ft.Column([tracker_tab, library_tab, favorites_tab, watchlist_tab, stats_tab], expand=True)

        main_tab_buttons = [
            ft.Container(content=ft.Text("Tracker", weight=ft.FontWeight.BOLD), data=0, padding=10, ink=True),
            ft.Container(content=ft.Text("Library", weight=ft.FontWeight.BOLD), data=1, padding=10, ink=True),
            ft.Container(content=ft.Text("Favorites", weight=ft.FontWeight.BOLD), data=2, padding=10, ink=True),
            ft.Container(content=ft.Text("Watchlist", weight=ft.FontWeight.BOLD), data=3, padding=10, ink=True),
            ft.Container(content=ft.Text("Stats", weight=ft.FontWeight.BOLD), data=4, padding=10, ink=True),
        ]

        def switch_main_tab(idx):
            tracker_tab.visible = (idx == 0)
            library_tab.visible = (idx == 1)
            favorites_tab.visible = (idx == 2)
            watchlist_tab.visible = (idx == 3)
            stats_tab.visible = (idx == 4)

            for i, btn in enumerate(main_tab_buttons):
                btn.border = ft.Border(bottom=ft.BorderSide(2, ft.Colors.PRIMARY)) if i == idx else None
                btn.content.color = ft.Colors.PRIMARY if i == idx else ft.Colors.ON_SURFACE_VARIANT

            page.update()

        for i, btn in enumerate(main_tab_buttons):
            btn.on_click = lambda e, idx=i: state.navigate(idx)

        main_tabs_row = ft.Row(main_tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=15)

        manager_modal = ManagerModalOverlay(state)

        def open_manage_dialog(e):
            page.floating_action_button.visible = False
            page.update()
            manager_modal.open_modal()

        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.EDIT,
            bgcolor=ft.Colors.PRIMARY,
            on_click=open_manage_dialog,
            tooltip="Manage Database"
        )

        def on_pubsub_message(msg):
            if msg.get("action") == "NAVIGATE":
                switch_main_tab(msg["index"])

        state.subscribe(on_pubsub_message)

        main_layout = ft.Container(
            expand=True, padding=20,
            content=ft.Column(
                expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[top_row, ft.Divider(height=1, color=ft.Colors.TRANSPARENT), main_tabs_row, ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT), main_content_area]
            )
        )

        root_stack = ft.Stack(expand=True, controls=[main_layout, manager_modal, settings_modal])
        
        switch_main_tab(0) 
        
        page.add(root_stack)

    ft.app(target=main)