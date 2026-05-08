import flet as ft

def create_tracker_tab():
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Select Universe:", size=16),
                ft.Dropdown(
                    options=[ft.dropdown.Option("DCAU Evreni"), ft.dropdown.Option("Miyazaki Maratonu")],
                    width=300,
                    border_color=ft.Colors.AMBER
                ),
                ft.Text("Select Last Watched Show:", size=16),
                ft.Dropdown(
                    options=[],
                    width=300,
                    border_color=ft.Colors.AMBER
                ),
                ft.ElevatedButton(
                    "FIND NEXT SHOW", 
                    color=ft.Colors.BLACK, 
                    bgcolor=ft.Colors.AMBER,
                    width=300,
                    height=45
                ),
                ft.Text("Hesaplama motoru yarın bağlanacak... ⚙️", color=ft.Colors.GREY_500)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.Alignment(0, -0.5),
        padding=40
    )