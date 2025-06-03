import os
import pygame
import sys
import time

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
        
play_azan()