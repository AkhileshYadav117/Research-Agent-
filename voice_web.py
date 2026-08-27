import speech_recognition as sr
from gtts import gTTS
import io
import re

recognizer = sr.Recognizer()

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Takes recorded audio bytes (from Streamlit's audio_input) and
    converts to text using Google's speech recognition.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-IN")
        return text
    except sr.UnknownValueError:
        return ""
    except Exception:
        return ""

def clean_for_speech(text: str) -> str:
    """Removes markdown/citation symbols so speech doesn't read them out."""
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"[#*_`]", "", text)
    return text.strip()

def text_to_audio_bytes(text: str) -> bytes:
    """
    Converts text to speech and returns MP3 audio bytes
    (for use with st.audio in Streamlit, no file needed on disk).
    """
    if not text.strip():
        return b""

    clean_text = clean_for_speech(text)
    tts = gTTS(text=clean_text, lang="en")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()