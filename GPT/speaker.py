import os
import pygame
import speech_recognition as sr
from gtts import gTTS

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening... Please speak into the microphone.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='ko')
        print("[User] " + text)
        return text
    except sr.UnknownValueError:
        #print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        #print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def speak(text, always_speak=False):
    if not text and not always_speak:
        return

    print(f"assistant: {text}")
    tts = gTTS(text=text, lang='ko')
    file_path = 'temp_assistant.mp3'

    # Save the new audio file
    tts.save(file_path)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Wait until the audio file is done playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Ensure the file is no longer being used
    pygame.mixer.quit()

    # Remove the file after playing
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")