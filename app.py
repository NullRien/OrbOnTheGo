import tkinter as tk
from tkinter import PhotoImage
import os
import random
import pygame
import requests
import threading
from PIL import Image, ImageTk

# Initialize pygame mixer
pygame.mixer.init()

# Function to play a random sound from a folder
def play_random_sound(folder):
    sound_files = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    if sound_files:
        sound_path = os.path.join(folder, random.choice(sound_files))
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()

# Function to update the counter
def update_counter(new_count):
    counter_label["text"] = str(new_count)

# Function to send a request and update counter asynchronously
def send_request():
    def request_thread():
        url = "https://orborb.org/api/orbcounter"
        payload = {"version": 2}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                root.after(0, update_counter, data.get("count", 0))
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
    threading.Thread(target=request_thread, daemon=True).start()

# Function to get the initial counter value asynchronously
def get_initial_count():
    def request_thread():
        url = "https://orborb.org/api/orbcounter"
        payload = {"version": 2}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                root.after(0, update_counter, data.get("count", 0))
        except requests.exceptions.RequestException as e:
            print("Initial request failed:", e)
    threading.Thread(target=request_thread, daemon=True).start()

# Function to periodically update counter asynchronously
def periodic_update():
    get_initial_count()
    root.after(500, periodic_update)  # Schedule next update in 60 seconds

# Function to resize and update an image
def resize_image(image, scale_factor):
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    return ImageTk.PhotoImage(image.resize(new_size, Image.ANTIALIAS))

# Create main application window
root = tk.Tk()
root.title("Orb on the go")
root.geometry("400x400")

# Load images
original_red_orb = Image.open("orb-red.png").convert("RGBA").resize((100, 100))
original_blue_orb = Image.open("orb-blue.png").convert("RGBA").resize((100, 100))

red_photo = ImageTk.PhotoImage(original_red_orb)
blue_photo = ImageTk.PhotoImage(original_blue_orb)

# Create counter label
counter_label = tk.Label(root, text="0", font=("Arial", 16))
counter_label.pack()

# Fetch the initial count
get_initial_count()
periodic_update()  # Start periodic updates

# Create canvas
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

# Draw images
blue_orb_id = canvas.create_image(135, 135, anchor=tk.NW, image=blue_photo)
red_orb_id = canvas.create_image(185, 185, anchor=tk.NW, image=red_photo)

# Resize effect functions
def on_press(event, orb_id, original_image, sound_folder):
    new_photo = resize_image(original_image, 0.9)
    canvas.itemconfig(orb_id, image=new_photo)
    canvas.image_dict[orb_id] = new_photo  # Store reference to prevent garbage collection
    play_random_sound(sound_folder)  # Play sound when pressed
    send_request()  # Send request asynchronously

def on_release(event, orb_id, original_image):
    new_photo = ImageTk.PhotoImage(original_image)
    canvas.itemconfig(orb_id, image=new_photo)
    canvas.image_dict[orb_id] = new_photo  # Store reference

# Bind click events
canvas.image_dict = {}  # Store image references
canvas.image_dict[red_orb_id] = red_photo
canvas.image_dict[blue_orb_id] = blue_photo

canvas.tag_bind(red_orb_id, "<ButtonPress-1>", lambda event: on_press(event, red_orb_id, original_red_orb, "gavinsounds"))
canvas.tag_bind(red_orb_id, "<ButtonRelease-1>", lambda event: on_release(event, red_orb_id, original_red_orb))

canvas.tag_bind(blue_orb_id, "<ButtonPress-1>", lambda event: on_press(event, blue_orb_id, original_blue_orb, "cmcsounds"))
canvas.tag_bind(blue_orb_id, "<ButtonRelease-1>", lambda event: on_release(event, blue_orb_id, original_blue_orb))

# Run the application
root.mainloop()
