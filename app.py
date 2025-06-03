import os
import pygame # used pygame because its more effecient than playsound library
import sys
import time
from datetime import datetime, timedelta
import schedule

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
        audio_file = "test_audio.mp3"
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
        print(test_time, prayer)
    

now = datetime.now()
print("Start Time: " , now.strftime("%I:%M:%S %p"))

setup_test_azan_schedule()

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
            last_azan_time = last_azan_time + timedelta(seconds=20) # 20 SECONDS PASSED AFTER LAST AZAN TIME OF THE DAY, THIS LINE IS FOR TEST SCHEDULES
            if now > last_azan_time:
                print("All Azans played. Exiting program.")
                print("Now: " , now.strftime("%I:%M:%S %p"))
                sys.exit(0)  # Exit with success code




run_schedule()