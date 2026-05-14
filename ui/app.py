import flet as ft
from ui.tabs.tracker import TrackerTab
from ui.tabs.library import LibraryTab
from ui.tabs.favorites import FavoritesTab
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
        page.padding = 0

        title = ft.Text("🎬 Universal Tracker", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)

        tracker_tab = TrackerTab(switch_func=None, db=db_manager, api=api_client)
        library_tab = LibraryTab(switch_func=None, db=db_manager, api=api_client)
        favorites_tab = FavoritesTab(switch_func=None, db=db_manager, api=api_client)

        def switch_main_tab_by_index(idx):
            tracker_tab.visible = (idx == 0)
            library_tab.visible = (idx == 1)
            favorites_tab.visible = (idx == 2)

            for i, btn in enumerate(main_tab_buttons):
                btn.border = ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)) if i == idx else None
                btn.content.color = ft.Colors.AMBER if i == idx else ft.Colors.WHITE70

            if idx == 0:
                tracker_tab._update_dashboard()
            elif idx == 1:
                library_tab._build_grid(library_tab.uni_drop.value)
            elif idx == 2:
                favorites_tab._build_view()

            page.update()

        def switch_to_tab(index, data=None):
            switch_main_tab_by_index(index)
            if data and index == 0:
                tracker_tab.set_show(data)
            page.update()

        tracker_tab.switch_func = switch_to_tab
        library_tab.switch_func = switch_to_tab
        favorites_tab.switch_func = switch_to_tab

        def switch_main_tab(e):
            switch_main_tab_by_index(e.control.data)

        main_tab_buttons = [
            ft.Container(content=ft.Text("Tracker", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER), data=0, on_click=switch_main_tab, padding=10, border=ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)), ink=True),
            ft.Container(content=ft.Text("Library", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70), data=1, on_click=switch_main_tab, padding=10, ink=True),
            ft.Container(content=ft.Text("Favorites", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70), data=2, on_click=switch_main_tab, padding=10, ink=True),
        ]
        
        main_tabs_row = ft.Row(main_tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        tracker_tab.visible = True
        library_tab.visible = False
        favorites_tab.visible = False
        main_content_area = ft.Column([tracker_tab, library_tab, favorites_tab], expand=True)

        def refresh_all_tabs():
            tracker_tab._init_data(tracker_tab.show_drop.value)
            
            timeline = db_manager.load_timeline()
            universes = list(timeline.keys())
            library_tab.universes = universes
            library_tab.uni_drop.options = [ft.DropdownOption(key=u, text=u) for u in universes]
            
            if library_tab.uni_drop.value not in universes and universes:
                library_tab.uni_drop.value = universes[0]
            elif not universes:
                library_tab.uni_drop.value = None
                
            if library_tab.uni_drop.value:
                library_tab._build_grid(library_tab.uni_drop.value)
            else:
                library_tab.grid.controls.clear()
                library_tab.update()
                
            favorites_tab._build_view()
            page.update()

        search_results_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=15, expand=True)
        search_input = ft.TextField(label="Search Movies/Shows", expand=True)

        def perform_search(e=None):
            search_results_col.controls.clear()
            search_results_col.controls.append(ft.ProgressRing())
            page.update()
            
            query = search_input.value
            if not query:
                search_results_col.controls.clear()
                page.update()
                return
                
            results = api_client.search_tmdb_query(query)
            search_results_col.controls.clear()
            
            if not results:
                search_results_col.controls.append(ft.Text("No results found on TMDB.", color=ft.Colors.WHITE70))
                page.update()
                return
            
            universes = list(db_manager.load_timeline().keys())
            
            for res in results:
                uni_dropdown = ft.Dropdown(
                    options=[ft.DropdownOption(key=u, text=u) for u in universes],
                    width=110,
                    hint_text="Universe",
                    text_size=12
                )
                
                chrono_input = ft.TextField(
                    label="Order",
                    width=60,
                    text_size=12,
                    keyboard_type=ft.KeyboardType.NUMBER
                )
                
                def add_clicked(e, r=res, d=uni_dropdown, c_inp=chrono_input):
                    if not d.value:
                        return
                    
                    release_year = int(r['year']) if r['year'] else 0
                    c_val = None
                    if c_inp.value and c_inp.value.isdigit():
                        c_val = int(c_inp.value)
                        
                    db_manager.add_show(d.value, r['title'], r['type'], c_val, release_year, 0)
                    refresh_all_tabs()
                    
                    d.disabled = True
                    c_inp.disabled = True
                    e.control.disabled = True
                    e.control.icon = ft.Icons.CHECK
                    e.control.icon_color = ft.Colors.GREEN
                    page.update()

                add_btn = ft.IconButton(
                    icon=ft.Icons.ADD, 
                    icon_color=ft.Colors.AMBER, 
                    on_click=add_clicked
                )
                
                image_control = ft.Image(src=res['image'], width=40, height=60, fit=ft.BoxFit.COVER, border_radius=5) if res['image'] else ft.Container(width=40, height=60, bgcolor="#333333", border_radius=5)
                
                row = ft.Row([
                    image_control,
                    ft.Column([
                        ft.Text(res['title'], weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{res['type'].capitalize()} • {res['year']}", size=11, color=ft.Colors.WHITE70)
                    ], spacing=2, expand=True),
                    uni_dropdown,
                    chrono_input,
                    add_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                
                search_results_col.controls.append(row)
            
            page.update()

        search_input.on_submit = perform_search
        search_btn = ft.IconButton(icon=ft.Icons.SEARCH, on_click=perform_search)
        search_row = ft.Row([search_input, search_btn])

        search_tab = ft.Container(
            content=ft.Column([
                search_row,
                search_results_col
            ], expand=True),
            padding=15,
            expand=True,
            visible=True
        )

        del_uni_drop = ft.Dropdown(label="Select Universe", width=250)
        del_show_drop = ft.Dropdown(label="Select Show", width=250)
        
        def load_del_drops():
            timeline = db_manager.load_timeline()
            unis = list(timeline.keys())
            del_uni_drop.options = [ft.DropdownOption(key=u, text=u) for u in unis]
            
            if not del_uni_drop.value or del_uni_drop.value not in unis:
                del_uni_drop.value = unis[0] if unis else None
            
            if del_uni_drop.value:
                shows = timeline.get(del_uni_drop.value, [])
                show_titles = [s["title"] for s in shows] if shows else []
                del_show_drop.options = [ft.DropdownOption(key=t, text=t) for t in show_titles]
                
                if not del_show_drop.value or del_show_drop.value not in show_titles:
                    del_show_drop.value = show_titles[0] if show_titles else None
            else:
                del_show_drop.options = []
                del_show_drop.value = None

        def on_del_uni_change(e):
            if e:
                e.control.value = e.data
            load_del_drops()
            page.update()
            
        del_uni_drop.on_select = on_del_uni_change

        confirm_dialog_content = ft.Text("")
        confirm_callback_holder = []

        def execute_confirm(e):
            confirm_overlay.visible = False
            page.update()
            if confirm_callback_holder:
                confirm_callback_holder[0]()

        def close_confirm_dlg(e):
            confirm_overlay.visible = False
            page.update()

        confirm_dialog_box = ft.Container(
            content=ft.Column([
                ft.Text("Confirm Deletion", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.RED),
                confirm_dialog_content,
                ft.Row([
                    ft.TextButton("Cancel", on_click=close_confirm_dlg),
                    ft.ElevatedButton("Delete", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=execute_confirm)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, spacing=20),
            bgcolor="#222222",
            padding=20,
            border_radius=10,
            width=400
        )

        confirm_overlay = ft.Container(
            content=confirm_dialog_box,
            bgcolor="#AA000000",
            alignment=ft.Alignment(0, 0),
            expand=True,
            visible=False
        )

        def show_confirm_dialog(content_text, confirm_callback):
            confirm_dialog_content.value = content_text
            confirm_callback_holder.clear()
            confirm_callback_holder.append(confirm_callback)
            confirm_overlay.visible = True
            page.update()

        def delete_show_action(e):
            if del_uni_drop.value and del_show_drop.value:
                def do_delete():
                    db_manager.delete_show(del_uni_drop.value, del_show_drop.value)
                    refresh_all_tabs()
                    load_del_drops()
                    page.update()
                
                show_confirm_dialog(
                    f"Are you sure you want to delete '{del_show_drop.value}'?",
                    do_delete
                )

        def delete_uni_action(e):
            if del_uni_drop.value:
                def do_delete():
                    db_manager.delete_universe(del_uni_drop.value)
                    refresh_all_tabs()
                    load_del_drops()
                    page.update()
                
                show_confirm_dialog(
                    f"Are you sure you want to delete the entire universe '{del_uni_drop.value}'?",
                    do_delete
                )
                
        new_uni_input = ft.TextField(label="New Universe Name", width=200)
        
        def add_uni_action(e):
            if new_uni_input.value:
                db_manager.add_universe(new_uni_input.value)
                new_uni_input.value = ""
                refresh_all_tabs()
                load_del_drops()
                page.update()

        manage_tab = ft.Container(
            content=ft.Column([
                ft.Text("Create New Universe", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                ft.Row([new_uni_input, ft.ElevatedButton("Add Universe", on_click=add_uni_action)]),
                ft.Divider(height=25, color=ft.Colors.OUTLINE_VARIANT),
                ft.Text("Remove Data", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                del_uni_drop,
                ft.ElevatedButton("Delete Selected Universe", color=ft.Colors.RED, on_click=delete_uni_action),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                del_show_drop,
                ft.ElevatedButton("Delete Selected Show", color=ft.Colors.RED, on_click=delete_show_action)
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
            padding=15,
            expand=True,
            visible=False
        )

        def switch_dialog_tab(e):
            idx = e.control.data
            search_tab.visible = (idx == 0)
            manage_tab.visible = (idx == 1)
            
            for i, btn in enumerate(dialog_tab_buttons):
                btn.border = ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)) if i == idx else None
                btn.content.color = ft.Colors.AMBER if i == idx else ft.Colors.WHITE70
            
            page.update()

        dialog_tab_buttons = [
            ft.Container(content=ft.Text("Search & Add", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER), data=0, on_click=switch_dialog_tab, padding=10, border=ft.Border(bottom=ft.BorderSide(2, ft.Colors.AMBER)), ink=True),
            ft.Container(content=ft.Text("Manage DB", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70), data=1, on_click=switch_dialog_tab, padding=10, ink=True),
        ]
        
        dialog_tabs_row = ft.Row(dialog_tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        dialog_content_area = ft.Column([search_tab, manage_tab], expand=True)

        def close_manage_dialog(e=None):
            modal_overlay.visible = False
            page.floating_action_button.visible = True
            page.update()

        modal_header = ft.Row(
            [
                ft.Text("Database Manager", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.AMBER),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=ft.Colors.WHITE70, on_click=close_manage_dialog)
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        modal_overlay = ft.Container(
            content=ft.Container(
                width=500,
                height=550,
                bgcolor="#2a2a2a",
                border_radius=15,
                padding=15,
                content=ft.Column([
                    modal_header,
                    dialog_tabs_row,
                    ft.Divider(height=1, color=ft.Colors.WHITE24),
                    dialog_content_area
                ], expand=True)
            ),
            bgcolor="#CC000000",
            alignment=ft.Alignment(0, 0),
            expand=True,
            visible=False
        )

        main_layout = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title, 
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    main_tabs_row, 
                    ft.Divider(height=1, color=ft.Colors.WHITE24),
                    main_content_area
                ]
            )
        )

        root_stack = ft.Stack(
            expand=True,
            controls=[
                main_layout,
                modal_overlay,
                confirm_overlay
            ]
        )

        def open_manage_dialog(e):
            load_del_drops()
            modal_overlay.visible = True
            page.floating_action_button.visible = False
            page.update()

        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.EDIT,
            bgcolor=ft.Colors.AMBER,
            on_click=open_manage_dialog,
            tooltip="Manage Database"
        )

        page.add(root_stack)

    ft.app(target=main)