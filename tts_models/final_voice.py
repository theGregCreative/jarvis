import os
import torch
from pathlib import Path
from TTS.utils.synthesizer import Synthesizer
from pydub import AudioSegment
from pydub.playback import play

def main():
    """
    Uses the lower-level Synthesizer object for direct, stable control over
    the TTS model and its built-in speakers.
    """
    # --- 1. DEFINE PATHS ---
    model_dir = Path.home() / ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
    output_path = Path("jarvis_final_output.wav")

    if not model_dir.exists():
        print(f"FATAL: Model directory not found at {model_dir}")
        return

    # --- 2. INITIALIZE THE SYNTHESIZER ---
    print("Loading Synthesizer...")
    synthesizer = Synthesizer(
        model_dir=str(model_dir),
        use_cuda=torch.cuda.is_available(),
    )
    print("Synthesizer loaded successfully.")

    # --- 3. LIST AVAILABLE SPEAKERS (Corrected Path) ---
    available_speakers = list(synthesizer.tts_model.speaker_manager.name_to_id)
    
    print("\nAvailable built-in voices:")
    for speaker in available_speakers:
        print(f"- {speaker}")

    # --- 4. CONFIGURE AND SPEAK ---
    speaker_to_use = 'Abrahan Mack'
    text_to_speak = "Finally. I believe this attempt will be successful. My apologies for the considerable delay."

    print(f"\nUsing voice: '{speaker_to_use}'")
    print(f"🤖 Jarvis: {text_to_speak}")

    try:
        # Generate the audio waveform
        outputs = synthesizer.tts(
            text=text_to_speak,
            speaker_name=speaker_to_use,
            language_name="en"
        )
        
        # Save the waveform to a .wav file
        print("Saving audio to file...")
        synthesizer.save_wav(outputs, output_path)
        
        # Play the generated audio file
        print("Playing audio...")
        audio = AudioSegment.from_wav(output_path)
        play(audio)
        print("\nProcess complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()