import os
import pygame
import sys
import time
from datetime import datetime, timedelta

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def play_azan():
    pygame.mixer.init()
    audio_file = "test_audio.mp3"
    if os.path.exists(resource_path(audio_file)):
        pygame.mixer.music.load(resource_path(audio_file))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    else:
        print(f"🚫 Audio file not found: {audio_file}")
        
def setup_test_azan_schedule():
    now = datetime.now()
    now = now + timedelta(seconds=20) # FIRST AZAAN SHOULD BE ALSO IN 20 Seconds LATER
    prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for i, prayer in enumerate(prayers):
        test_time = (now + timedelta(seconds=i * 20)).strftime("%H:%M:%S")  # 20-second intervals
        print(prayer, test_time)
    
setup_test_azan_schedule()