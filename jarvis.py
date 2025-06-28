import os
import subprocess
import threading
import speech_recognition as sr
from TTS.api import TTS
from modules.generate import query_llm

# Initialize recognizer and TTS
recognizer = sr.Recognizer()

# Try using a different FastSpeech2 model for a more natural-sounding voice
tts = TTS(model_name="tts_models/en/vctk/fastspeech2", progress_bar=False, gpu=True)

playback_process = None
HOTWORD = "jarvis"

def listen():
    """Capture voice input from the default microphone."""
    with sr.Microphone() as source:
        print("🎤 Calibrating mic... please wait.")
        
        # Adjust for ambient noise levels with a shorter duration for quicker calibration
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        
        # Set the energy threshold dynamically to adapt to background noise
        recognizer.energy_threshold = 300
        
        # Set pause threshold to be more responsive to short pauses
        recognizer.pause_threshold = 0.6  # Allow short pauses (0.6 seconds)
        recognizer.non_speaking_duration = 0.5  # Adjust non-speaking duration to allow for natural speech
        
        print(f"🎚️ Energy threshold set to: {recognizer.energy_threshold}")
        
        print("🎤 Listening...")
        try:
            # Listen continuously until the user finishes speaking
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)  # Adjusted timeout/phrase time
        except sr.WaitTimeoutError:
            print("⏰ Listening timed out waiting for phrase.")
            return ""
        
    try:
        # Use Google Web API to transcribe speech to text
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError as e:
        print(f"🚨 Speech recognition error: {e}")
        return ""


def speak(text):
    """Generate and play TTS audio."""
    global playback_process
    print("🤖 Jarvis:", text)

    tts.tts_to_file(text=text, file_path="jarvis_output.wav")

    # Start the new audio playback without checking for interruptions
    playback_process = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "jarvis_output.wav"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def listen_for_hotword():
    """Background listener to detect hotword without interrupting playback."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=2)
            phrase = recognizer.recognize_google(audio).lower()
            print(f"👂 Detected during playback: {phrase}")
            if HOTWORD in phrase:
                print("Hotword detected!")
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            pass
        except sr.RequestError as e:
            print(f"⚠️ Hotword listener error: {e}")


def main():
    """Main loop: listen, respond, repeat."""
    while True:
        user_input = listen()
        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "goodbye"}:
            speak("Goodbye!")
            break

        response = query_llm(user_input)

        # Start speaking in a separate thread
        speak_thread = threading.Thread(target=speak, args=(response,))
        
        # Start hotword listener in background (non-blocking)
        hotword_thread = threading.Thread(target=listen_for_hotword)

        speak_thread.start()
        hotword_thread.start()

        speak_thread.join()  # Wait for the speech to finish before listening for new input
        # No need to join hotword_thread – it's non-blocking


if __name__ == "__main__":
    main()
