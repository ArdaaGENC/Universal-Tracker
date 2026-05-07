# DCAU Watch Guide - Version 5.3 (Visual Update)
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
        return {"hata": "Veritabanı Bulunamadı"}
    
# Function to load the user's last watched show from a JSON file
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as f:
            data = json.load(f)
            return data.get("last_watched", "Select a series...")
    return "Select a series..."

# Function to save the user's last watched show to a JSON file
def save_progress(last_show_name):
    data = {"last_watched": last_show_name}
    with open("progress.json", "w") as f:
        json.dump(data, f)

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
# 4. GUI SETUP
# ==========================================
# Function to find the next show based on the selected show
def find_next_show():
    selected_show = show_combobox.get()

    if selected_show in dcau_timeline:
        next_show = dcau_timeline[selected_show]
        save_progress(selected_show)
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
        
        save_progress(selected_show)
    else:
        result_label.configure(text="Please select a valid show from the list.", text_color=ERROR_COLOR)
        details_label.configure(text="")
        poster_label.configure(image='', text="")

# ==========================================
# 5. GUI INITIALIZATION
# ==========================================
dcau_timeline = load_timeline()

# Create the main application window
window = ctk.CTk()
window.title("DCAU Watch Guide")
window.geometry("500x600")

# Title label
title_label = ctk.CTkLabel(window, text="🦇 DCAU Watch Guide", font=TITLE_FONT, text_color=ACCENT_COLOR)
title_label.pack(pady=(20, 15))

# Instruction label
instruction_label = ctk.CTkLabel(window, text="Which series did you finish last?", font=NORMAL_FONT)
instruction_label.pack(pady=5)

# Combobox
show_list = list(dcau_timeline.keys())
show_combobox = ctk.CTkComboBox(window, values=show_list, width=350, font=NORMAL_FONT, dropdown_font=NORMAL_FONT, border_color=ACCENT_COLOR)
show_combobox.set(load_progress())
show_combobox.pack(pady=10)

# Calculate button
calculate_btn = ctk.CTkButton(window, text="FIND NEXT SHOW", command=find_next_show, fg_color=ACCENT_COLOR, text_color="black", hover_color="#d4aa00", font=("Segoe UI", 14, "bold"), corner_radius=8, width=200, height=40)
calculate_btn.pack(pady=20)

# Result label
result_label = ctk.CTkLabel(window, text="", font=("Segoe UI", 16, "bold"))
result_label.pack(pady=5)

# Details label
details_label = ctk.CTkLabel(window, text="", font=SMALL_FONT)
details_label.pack(pady=5)

# Poster label
poster_label = ctk.CTkLabel(window, text="")
poster_label.pack(pady=10)


window.mainloop()