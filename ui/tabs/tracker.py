import flet as ft
from core.database import load_timeline, load_progress, save_progress
from core.api import fetch_show_details

def create_tracker_tab(page, switch_func, auto_select_show=None):
    db = load_timeline()
    universes = list(db.keys())
    initial_uni = universes[0] if universes else None
    
    if auto_select_show:
        for u, shows in db.items():
            for item in shows:
                title = item if isinstance(item, str) else item.get("title")
                if auto_select_show == title:
                    initial_uni = u
                    break

    uni_drop = ft.Dropdown(options=[ft.DropdownOption(key=u, text=u) for u in universes], value=initial_uni, width=300, label="Universe")
    
    filter_drop = ft.Dropdown(
        options=[
            ft.DropdownOption(key="all", text="All Types"),
            ft.DropdownOption(key="movie", text="Movies Only"),
            ft.DropdownOption(key="show", text="Shows Only")
        ],
        value="all", width=145, label="Filter"
    )
    
    sort_drop = ft.Dropdown(
        options=[
            ft.DropdownOption(key="chrono", text="Chronological"),
            ft.DropdownOption(key="release", text="Release Order")
        ],
        value="chrono", width=145, label="Sort"
    )

    show_drop = ft.Dropdown(width=300, label="Show")
    res_label = ft.Text("", size=18, weight="bold", color="green")
    poster = ft.Image(src="", width=160, height=230, fit="contain", visible=False)

    def update_list(e=None, force_select=None):
        if e:
            e.control.value = e.data

        current_uni = uni_drop.value
        if not current_uni: 
            return
            
        raw_shows = db.get(current_uni, [])
        processed = []
        
        for item in raw_shows:
            if isinstance(item, str):
                processed.append({"title": item, "type": "all", "chrono": 0, "release": 0})
            else:
                processed.append(item)
        
        current_filter = filter_drop.value
        if current_filter and current_filter != "all":
            processed = [s for s in processed if s.get("type", "all").lower() == current_filter]
            
        current_sort = sort_drop.value
        if current_sort == "chrono":
            processed = sorted(processed, key=lambda x: x.get("chrono", 0))
        elif current_sort == "release":
            processed = sorted(processed, key=lambda x: x.get("release", 0))
            
        filtered_titles = [s["title"] for s in processed]
        
        show_drop.options.clear()
        for t in filtered_titles:
            show_drop.options.append(ft.DropdownOption(key=t, text=t))
            
        prog = load_progress()
        saved_val = prog.get(current_uni, "")
        
        if force_select and force_select in filtered_titles:
            show_drop.value = force_select
        elif saved_val in filtered_titles:
            show_drop.value = saved_val
        else:
            show_drop.value = filtered_titles[0] if filtered_titles else None
            
        res_label.value = ""
        poster.visible = False
        
        if page: 
            page.update()

    uni_drop.on_select = update_list
    filter_drop.on_select = update_list
    sort_drop.on_select = update_list
    
    update_list(force_select=auto_select_show)

    def find_next(e):
        current_titles = [opt.key for opt in show_drop.options]
        
        if show_drop.value in current_titles:
            idx = current_titles.index(show_drop.value)
            if idx + 1 < len(current_titles):
                nxt = current_titles[idx + 1]
                res_label.value = f"Next: {nxt}"
                det = fetch_show_details(nxt)
                if det and det.get("image_url"):
                    poster.src = det.get("image_url")
                    poster.visible = True
            else:
                res_label.value = "🎉 List Finished!"
                poster.visible = False
            
            save_progress(uni_drop.value, show_drop.value)
            if e.page: 
                e.page.update()

    filter_sort_row = ft.Row([filter_drop, sort_drop], alignment=ft.MainAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Column([
            uni_drop, 
            filter_sort_row, 
            show_drop,
            ft.ElevatedButton("FIND NEXT", bgcolor="amber", color="black", on_click=find_next, width=300),
            res_label, poster
        ], horizontal_alignment="center", spacing=20),
        alignment=ft.Alignment(0, 0),
        padding=40
    )