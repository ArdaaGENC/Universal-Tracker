import flet as ft
import threading
from core.database import load_timeline
from core.api import fetch_show_details

def create_library_tab(page, switch_func):
    db = load_timeline()
    grid = ft.GridView(expand=True, max_extent=160, child_aspect_ratio=0.6, spacing=15)

    def load_posters(title_str, img_container):
        det = fetch_show_details(title_str)
        if det and det.get("image_url"):
            img_container.content = ft.Image(src=det.get("image_url"), fit="contain")
            try:
                if img_container.page:
                    img_container.update()
            except Exception:
                pass

    def build_grid(uni, is_initial=False):
        new_cards = []
        pending_downloads = []
        
        for item in db.get(uni, []):
            title = item if isinstance(item, str) else item.get("title", "")
            
            img_container = ft.Container(width=120, height=180, bgcolor="#333333", border_radius=10)
            
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
                on_click=lambda e, s=title: switch_func(0, s)
            )
            new_cards.append(card)
            pending_downloads.append((title, img_container))
            
        grid.controls = new_cards
        
        if not is_initial:
            if grid.page:
                grid.update()
                
        for title_str, img_cont in pending_downloads:
            threading.Thread(target=load_posters, args=(title_str, img_cont), daemon=True).start()

    universes = list(db.keys())
    initial_uni = universes[0] if universes else None

    def handle_dropdown_select(e):
        e.control.value = e.data
        if e.control.page:
            e.control.update()
            
        build_grid(e.data, is_initial=False)

    uni_drop = ft.Dropdown(
        options=[ft.DropdownOption(key=u, text=u) for u in universes],
        value=initial_uni, 
        width=300,
        on_select=handle_dropdown_select
    )
    
    if initial_uni:
        build_grid(initial_uni, is_initial=True)

    return ft.Container(
        content=ft.Column([uni_drop, grid], horizontal_alignment="center"),
        expand=True,
        padding=20
    )