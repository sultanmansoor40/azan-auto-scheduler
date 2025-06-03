import os
import pygame # used pygame because its more effecient than playsound library
import sys
import time
from datetime import datetime, timedelta
import schedule
from threading import Thread
import tkinter as tk
from tkinter import ttk
import requests

# 🗂️ For PyInstaller: return the path to bundled resources or normal path if not frozen
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def str_to_datetime(time_str):
    """
    Convert a time string in 'HH:MM' or 'HH:MM:SS' format to a datetime object
    with today's date and the given time.
    """
    now = datetime.now()
    formats = ["%H:%M:%S", "%H:%M"]  # try seconds format first, then minutes only

    for fmt in formats:
        try:
            time_obj = datetime.strptime(time_str, fmt)
            # Replace year, month, day with today's date
            return time_obj.replace(year=now.year, month=now.month, day=now.day)
        except ValueError:
            continue
    raise ValueError(f"Time string '{time_str}' is not in a supported format")


def format_time_12h(time_str):
    """
    Converts a time string (HH:MM or HH:MM:SS) to 12-hour format with AM/PM.
    Includes seconds if they are present.
    """
    try:
        # Try parsing as HH:MM:SS
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        return time_obj.strftime("%I:%M:%S %p")
    except ValueError:
        try:
            # Try parsing as HH:MM
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        except ValueError:
            return time_str  # fallback if format is invalid

next_azans = [] # Global list to store all scheduled azans for today

def schedule_azan(time_str, prayer_name):
    def play_azan():
        print(f"\n🔊 Playing Azan for {prayer_name} at {time_str}")
        pygame.mixer.init()
        #audio_file = "test_audio.mp3"
        audio_file = "azan.mp3"
        if os.path.exists(audio_file):
            pygame.mixer.music.load(resource_path(audio_file))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        else:
            print(f"🚫 Audio file not found: {audio_file}")
        next_azans.remove((time_str, prayer_name))


    schedule.every().day.at(time_str).do(play_azan)
    next_azans.append((time_str, prayer_name))
        
def setup_test_azan_schedule():
    now = datetime.now()
    now = now + timedelta(seconds=20) # FIRST AZAAN SHOULD BE ALSO IN 20 Seconds LATER
    prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for i, prayer in enumerate(prayers):
        test_time = (now + timedelta(seconds=i * 20)).strftime("%H:%M:%S")  # 20-second intervals
        schedule_azan(test_time, prayer)
        #print(test_time, prayer)
        

# Function to fetch prayer times from AlAdhan API for given coordinates and date
def get_prayer_times_by_city_country(date_str=None):
    url = "https://api.aladhan.com/v1/timingsByCity/" + date_str
    params = {
        "city": "Kabul",
        "country": "Afghanistan",
        "method": 1,  # University of Islamic Sciences, Karachi
        "school": 1   # Hanafi
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["data"]["timings"]
    else:
        print("Error:", response.text)
        return None        

# Main execution: Fetch and schedule today's Azan times
def setup_daily_azan_schedule():
    # Format today’s date as DD-MM-YYYY
    today = datetime.now().strftime("%d-%m-%Y")

    # Get prayer times for today
    timings = get_prayer_times_by_city_country(date_str=today)
    

    if timings:
        # Choose which prayers to schedule (you can modify this list)
        for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            time_24h = timings[prayer]
            # Schedule in 24-hour format as required by schedule library
            schedule_azan(time_24h, prayer)

        print("Azan times scheduled for today.")

    

now = datetime.now()
print("Start Time: " , now.strftime("%I:%M:%S %p"))

#setup_test_azan_schedule()
setup_daily_azan_schedule()


def get_next_azan():
    now = datetime.now()
    future_azans = []
    for time_str, prayer_name in next_azans:
        azan_time = str_to_datetime(time_str)
        if azan_time > now:
            future_azans.append((azan_time, prayer_name))
    return min(future_azans, default=(None, None))


def refresh_table_highlight():
    # Remove all current highlights
    for item in tree.get_children():
        tree.item(item, tags=())
    # Highlight next azan row
    next_time, next_prayer = get_next_azan()
    if next_prayer:
        for item in tree.get_children():
            if tree.item(item, 'values')[0] == next_prayer:
                tree.item(item, tags=('next',))
                break

def update_gui():
    next_time, next_prayer = get_next_azan()
    if next_time:
        remaining = next_time - datetime.now()
        total_seconds = int(remaining.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_label.config(
            text=f"{next_prayer} in {hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        scheduled_label.config(text=f"Scheduled at: {next_time.strftime('%I:%M:%S %p')}")
    else:
        countdown_label.config(text="All Azans done")
        scheduled_label.config(text="")
    refresh_table_highlight()
    root.after(1000, update_gui)

# run scheduled events
def run_schedule():
    
    while True:
        
        schedule.run_pending() # Checks if any scheduled job is due to run right now, and runs it if so.
        time.sleep(1) # Pauses the loop for 1 second before checking again. This prevents it from constantly using CPU in a tight loop.
        # Without above line It can easily check millions of times per second, depending on your machine — causing 100% CPU usage on one core.
        # Other alternative can be 0.1 which means 10 times checking in each second
        # If we increase the sleep time more than 1 second for example 5 , it will work but it will be less accurate
        # Exit Condition
        if not next_azans:
            print("All Azans played. Exiting program.")
            sys.exit(0)  # Exit with success code
        else:
            now = datetime.now()
            last_azan_time = str_to_datetime(next_azans[-1][0])
            #last_azan_time = last_azan_time + timedelta(seconds=20) # 20 SECONDS PASSED AFTER LAST AZAN TIME OF THE DAY, THIS LINE IS FOR TEST SCHEDULES
            last_azan_time = last_azan_time + timedelta(minutes=5) # 5 MINUTES PASSED AFTER LAST AZAN TIME OF THE DAY, THIS LINE IS FOR REAL SCHEDULES
            if now > last_azan_time:
                print("All Azans played. Exiting program.")
                print("Now: " , now.strftime("%I:%M:%S %p"))
                schedule.clear()        # Cancel all scheduled jobs
                root.destroy()          # Close GUI
                sys.exit(0)  # Exit with success code



# Start scheduler thread
# if we dont use the threading for running schedule, the script gets stuck in the infinite loop, and anything after it (like the GUI window) will never run.
thread = Thread(target=run_schedule, daemon=True)
thread.start()


# 🖼️ Setup the GUI window using Tkinter
root = tk.Tk()
root.title("Azan Countdown & Prayer Times")
root.geometry("350x300")
root.resizable(False, False)


countdown_label = tk.Label(root, text="Loading...", font=("Helvetica", 18))
countdown_label.pack(pady=10)

# 📅 Label to show exact time of next Azan
scheduled_label = tk.Label(root, text="", font=("Helvetica", 12))
scheduled_label.pack()

# 📋 TreeView widget to display prayer schedule
tree = ttk.Treeview(root, columns=("Prayer", "Time"), show="headings", height=7)
tree.heading("Prayer", text="Prayer")
tree.heading("Time", text="Time")
tree.column("Prayer", width=120, anchor='center')
tree.column("Time", width=100, anchor='center')
tree.pack(pady=10)

# ⏳ Insert all scheduled Azans into the table
for time_str, prayer_name in next_azans:
    tree.insert('', 'end', values=(prayer_name, format_time_12h(time_str)))
    
def on_close():
    print("Window closed by user. Exiting...")
    schedule.clear()        # Cancel all scheduled jobs
    root.destroy()          # Close GUI
    sys.exit(0)  # Exit the program completely

# Attach the handler to the window close event
root.protocol("WM_DELETE_WINDOW", on_close)


# Tag styling for highlight
tree.tag_configure('next', background='lightgreen')

update_gui()

# 🖥️ Start the Tkinter event loop
root.mainloop()