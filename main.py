# DCAU Watch Guide - Version 5.1 (Saved Progress)
import tkinter as tk
from tkinter import ttk
import json
import os

# The timeline dictionary (Key: watched series, Value: next series to watch)
dcau_timeline = {
    "batman: the animated series": "The New Batman Adventures",
    "the new batman adventures": "Superman: the animated series",
    "superman: the animated series": "Batman Beyond",
    "batman beyond": "Justice League",
    "justice league": "Justice League Unlimited",
}

# Function to save the user's last watched show to a JSON file
def save_progress(last_show_name):
    data = {"last_watched": last_show_name}
    with open("progress.json", "w") as f:
        json.dump(data, f)

# Function to load the user's last watched show from a JSON file
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as f:
            data = json.load(f)
            return data.get("last_watched", "Select a series...")
    return "Select a series..."

# Function to find the next show based on the selected show
def find_next_show():
    selected_show = show_combobox.get()

    if selected_show in dcau_timeline:
        next_show = dcau_timeline[selected_show]
        save_progress(selected_show)
        result_label.config(text=f"Next up: {next_show}", fg="green")
    else:
        result_label.config(text="Please select a valid show from the list.", fg="red")

# Create the main application window
window = tk.Tk()
window.title("DCAU Watch Guide")
window.geometry("450x250")
window.eval('tk::PlaceWindow . center')

# Title label
title_label = tk.Label(window, text="Welcome to the DCAU Watch Guide!", font=("Arial", 14, "bold"))
title_label.pack(pady=15)

# Instruction label
instruction_label = tk.Label(window, text="Which series did you finish last?", font=("Arial", 10))
instruction_label.pack(pady=5)

# Combobox
show_list = list(dcau_timeline.keys())
show_combobox = ttk.Combobox(window, values=show_list, width=35, state="readonly")
saved_show = load_progress()
show_combobox.set(saved_show)
show_combobox.pack(pady=5)

# Calculate button
calculate_btn = tk.Button(window, text="Find Next Show", command=find_next_show, bg="black", fg="white", font=("Arial", 10, "bold"))
calculate_btn.pack(pady=15)

# Result label
result_label = tk.Label(window, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=5)

window.mainloop()