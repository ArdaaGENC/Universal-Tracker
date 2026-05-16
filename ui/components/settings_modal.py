import flet as ft
from core.themes import THEMES

class SettingsModalOverlay(ft.Stack):
    def __init__(self, state):
        super().__init__(expand=True, visible=False)
        self.state = state
        self._build_ui()

    def open_modal(self):
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.color_drop.value = self.state.theme_name
        self.visible = True
        self.update()

    def _close_modal(self, e=None):
        self.visible = False
        self.update()

    def _toggle_theme(self, e):
        new_mode = "dark" if e.control.value else "light"
        self.state.set_theme_mode(new_mode)
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.update()

    def _change_color(self, e):
        self.state.set_theme_name(e.control.value)
        self.color_drop.value = self.state.theme_name
        self.update()

    def _build_ui(self):
        self.theme_switch = ft.Switch(
            label="Dark Mode",
            value=(self.state.theme_mode == "dark"),
            on_change=self._toggle_theme
        )

        dropdown_options = []
        for key, value in THEMES.items():
            dropdown_options.append(ft.DropdownOption(key=key, text=value["name"]))

        self.color_drop = ft.Dropdown(
            label="Custom Theme",
            options=dropdown_options,
            width=250,
            on_select=self._change_color
        )

        modal_header = ft.Row(
            controls=[
                ft.Text("Settings", weight=ft.FontWeight.BOLD, size=18, color="primary"),
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=self._close_modal)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        settings_content = ft.Column(
            controls=[
                ft.Text("Appearance", weight=ft.FontWeight.BOLD, color="primary"),
                self.theme_switch,
                self.color_drop
            ],
            spacing=15
        )

        self.modal_box = ft.Container(
            width=400,
            height=350,
            bgcolor="surface",
            border_radius=15,
            padding=20,
            content=ft.Column(
                controls=[
                    modal_header,
                    ft.Divider(height=1),
                    settings_content
                ],
                expand=True
            )
        )

        self.modal_overlay = ft.Container(
            content=self.modal_box,
            bgcolor="#8A000000",
            alignment=ft.Alignment(0, 0),
            expand=True
        )

        self.controls = [self.modal_overlay]