# Universal Marathon Tracker - Version 6.0 (Multiverse Engine)
import customtkinter as ctk
import json
import os
import requests
from PIL import Image
from io import BytesIO

# ==========================================
# 1.THEME SETTINGS
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
ACCENT_COLOR = "#f5c518"
SUCCESS_COLOR = "#2ecc71"
ERROR_COLOR = "#e74c3c"

TITLE_FONT = ("Segoe UI", 20, "bold")
NORMAL_FONT = ("Segoe UI", 13)
SMALL_FONT = ("Segoe UI", 12, "italic")

# ==========================================
# 2. DATA AND MEMORY MANAGEMENT
# ==========================================
# Function to load the timeline data from a JSON file
def load_timeline():
    try:
        with open("timeline.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("HATA: timeline.json dosyası bulunamadı!")
        return {}
    
# Function to load the user's last watched show from a JSON file
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Function to save the user's last watched show to a JSON file
def save_progress(universe_name, show_name):
    progress_data = load_progress()
    progress_data[universe_name] = show_name
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=4)

# ==========================================
# 3. INTERNET AND API INTEGRATION
# ==========================================
# Fetches live data and poster URL from TVmaze API
def fetch_show_details(show_name):
    search_query = show_name.replace(" (Film)", "")
    api_url = f"https://api.tvmaze.com/singlesearch/shows?q={search_query}"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            rating = data.get("rating", {}).get("average", "N/A")
            premiered = data.get("premiered", "N/A")
            text_info = f"Rating: {rating}/10 | Premiered: {premiered}"
            image_url = data["image"].get("medium") if data.get("image") else None
            return {"text": text_info, "image_url": image_url}
        else:
            return {"text": "Details not available", "image_url": None}
    except:
        return {"text": "No internet connection", "image_url": None}
    
# ==========================================
# 4. GUI BRAINS AND LOGIC
# ==========================================
# Updates the show combobox based on the selected universe and loads the last watched show
def update_show_menu(selected_universe):
    show_in_universe = timeline_db.get(selected_universe, [])
    show_combobox.configure(values=show_in_universe)

    saved_progress = load_progress()
    last_watched = saved_progress.get(selected_universe, show_in_universe[0] if show_in_universe else "")
    show_combobox.set(last_watched)

    result_label.configure(text="")
    details_label.configure(text="")
    poster_label.configure(image='', text="")

# Function to find the next show based on the selected show
def find_next_show():
    selected_universe = universe_combobox.get()
    selected_show = show_combobox.get()

    universe_list = timeline_db.get(selected_universe, [])

    if selected_show in universe_list:
        current_index = universe_list.index(selected_show)

        if current_index + 1 < len(universe_list):
            next_show = universe_list[current_index + 1]
            result_label.configure(text=f"Next up: {next_show}", text_color=SUCCESS_COLOR)

            details = fetch_show_details(next_show)
            details_label.configure(text=details["text"], text_color="#aaaaaa")

            if details["image_url"]:
                img_response = requests.get(details["image_url"])
                img_data = Image.open(BytesIO(img_response.content))
                ctk_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(160, 230))
                poster_label.configure(image=ctk_image, text="")
            else:
                poster_label.configure(image='', text="No Poster Found")
        else:
            result_label.configure(text="🎉 Congratulations! You have finished this list.", text_color=SUCCESS_COLOR)
            details_label.configure(text="")
            poster_label.configure(image='', text="")

        save_progress(selected_universe, selected_show)   
    else:
        result_label.configure(text="Please select a valid show.", text_color=ERROR_COLOR)

# ==========================================
# 5. GUI INITIALIZATION
# ==========================================
timeline_db = load_timeline()
universes = list(timeline_db.keys())

# Create the main application window
window = ctk.CTk()
window.title("Universal Marathon Tracker")
window.geometry("550x700")
window.minsize(450, 650)

main_frame = ctk.CTkFrame(window, fg_color="transparent")
main_frame.pack(expand=True, fill="both", padx=40, pady=20)

# Title label
title_label = ctk.CTkLabel(main_frame, text="🎬 Universal Tracker", font=TITLE_FONT, text_color=ACCENT_COLOR)
title_label.pack(pady=(0, 20))

# Universe label and combobox
universe_label = ctk.CTkLabel(main_frame, text="Select Universe:", font=NORMAL_FONT)
universe_label.pack(pady=(0, 5))

universe_combobox = ctk.CTkComboBox(main_frame, values=universes, font=NORMAL_FONT, dropdown_font=NORMAL_FONT, border_color=ACCENT_COLOR, command=update_show_menu)
universe_combobox.pack(pady=(0, 15), fill="x")

# Show label and combobox
show_label = ctk.CTkLabel(main_frame, text="Select Last Watched Show:", font=NORMAL_FONT)
show_label.pack(pady=(0, 5))

show_combobox = ctk.CTkComboBox(main_frame, values=[], font=NORMAL_FONT, dropdown_font=NORMAL_FONT, border_color=ACCENT_COLOR)
show_combobox.pack(pady=(0, 15), fill="x")

# Calculate button
calculate_btn = ctk.CTkButton(main_frame, text="FIND NEXT SHOW", command=find_next_show, fg_color=ACCENT_COLOR, text_color="black", hover_color="#d4aa00", font=("Segoe UI", 14, "bold"), corner_radius=8, height=40)
calculate_btn.pack(pady=10, fill="x")

# Result label
result_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 16, "bold"), wraplength=400)
result_label.pack(pady=10)

# Details label
details_label = ctk.CTkLabel(main_frame, text="", font=SMALL_FONT)
details_label.pack(pady=5)

# Poster label
poster_label = ctk.CTkLabel(main_frame, text="")
poster_label.pack(pady=10)


if universes:
    universe_combobox.set(universes[0])
    update_show_menu(universes[0])


window.mainloop()