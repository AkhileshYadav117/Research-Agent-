import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import tempfile
import time

recognizer = sr.Recognizer()
pygame.mixer.init()

def listen(language: str = "en") -> str:
    """
    Listens via microphone and converts speech to text.
    language: 'en' for English, 'hi' for Hindi
    """
    lang_code = "en-IN" if language == "en" else "hi-IN"

    with sr.Microphone() as source:
        print("🎙️  Listening... speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return ""

def speak(text: str, language: str = "en"):
    """
    Converts text to speech and plays it aloud.
    language: 'en' for English, 'hi' for Hindi
    """
    if not text.strip():
        return

    lang_code = "en" if language == "en" else "hi"

    try:
        tts = gTTS(text=text, lang=lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            temp_path = tmp.name
        tts.save(temp_path)

        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()
        os.remove(temp_path)
    except Exception as e:
        print(f"Text-to-speech error: {e}")