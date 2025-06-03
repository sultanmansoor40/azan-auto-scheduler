import os
import pygame
import sys
import time
from datetime import datetime, timedelta
import schedule

# 🗂️ For PyInstaller: return the path to bundled resources or normal path if not frozen
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


next_azans = [] # Global list to store all scheduled azans for today

def schedule_azan(time_str, prayer_name):
    def play_azan():
        print(f"\n🔊 Playing Azan for {prayer_name} at {time_str}")
        pygame.mixer.init()
        audio_file = "azan.mp3"
        #audio_file = "test_audio.mp3"
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
    
setup_test_azan_schedule()