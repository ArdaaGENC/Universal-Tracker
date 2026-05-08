import flet as ft

def create_library_tab():
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Dropdown(
                    options=[ft.dropdown.Option("DCAU Evreni"), ft.dropdown.Option("Miyazaki Maratonu")],
                    width=300,
                    border_color=ft.Colors.AMBER
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text("Sayfalı (Pagination) Katalog Sistemi yarın buraya inşa edilecek 🚀", color=ft.Colors.GREY_500)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, -0.8),
        padding=20
    )