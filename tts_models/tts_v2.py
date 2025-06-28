import torch
import os
from pathlib import Path
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play

class JarvisTTS:
    """
    A class to manage the JARVIS Text-to-Speech system, 
    featuring performance caching and quality tuning.
    """
    def __init__(self, voice_sample_path: Path, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.voice_sample_path = voice_sample_path
        self.output_path = Path("jarvis_output.wav")
        self.cache_path = self.voice_sample_path.with_suffix('.pt')

        # Load the TTS model
        print("Loading XTTS V2 model...")
        self.tts = TTS(self.model_name).to(self.device)
        print("Model loaded successfully.")

        # Get or create speaker latents for caching
        self.gpt_cond_latent, self.speaker_embedding = self._get_or_create_latents()

    def _get_or_create_latents(self):
        """
        Checks for cached speaker latents, creates them if not found.
        This provides a massive speed-up on subsequent runs.
        """
        if self.cache_path.exists():
            print(f"Loading cached voice latents from {self.cache_path}...")
            return torch.load(self.cache_path)
        else:
            print("No cache found. Computing new voice latents...")
            # --- THIS IS THE FINAL CORRECTED LINE ---
            gpt_cond_latent, speaker_embedding = self.tts.synthesizer.tts_model.get_conditioning_latents(audio_path=[self.voice_sample_path])
            print(f"Saving new voice latents to {self.cache_path}...")
            torch.save((gpt_cond_latent, speaker_embedding), self.cache_path)
            return gpt_cond_latent, speaker_embedding

    def speak(self, text: str, temperature=0.65, repetition_penalty=5.0):
        """
        Generate and play TTS audio using the cached voice latents.
        
        Args:
            text (str): The text to be spoken.
            temperature (float): Controls creativity. Lower is more deterministic. Default is 0.65.
            repetition_penalty (float): Higher values reduce repetition. Default is 5.0.
        """
        if not self.voice_sample_path.exists():
            print(f"Error: Voice sample file not found at '{self.voice_sample_path}'")
            return
            
        print(f"🤖 Jarvis: {text}")
        try:
            # Generate audio using the cached latents for speed
            self.tts.tts_to_file(
                text=text,
                file_path=self.output_path,
                speaker_embedding=self.speaker_embedding,
                gpt_cond_latent=self.gpt_cond_latent,
                language="en",
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )
            
            # Play the generated audio file using pydub
            print("Playing audio...")
            audio = AudioSegment.from_wav(self.output_path)
            play(audio)
            
        except Exception as e:
            print(f"An error occurred during TTS processing or playback: {e}")

def main():
    """Main execution function."""
    # --- CONFIGURATION ---
    voice_sample = Path("jarvis_voice_sample.wav")
    text_to_speak = "Sir, the updated speech synthesis protocols are now online. The result is significantly more performant and, if I may say so, sounds rather like myself."

    # --- INITIALIZE AND RUN ---
    try:
        jarvis = JarvisTTS(voice_sample_path=voice_sample)
        jarvis.speak(text_to_speak)

        # Example of speaking again with different text (will be much faster)
        jarvis.speak("This second sentence was generated almost instantly, thanks to latency caching.")

    except Exception as e:
        print(f"Failed to initialize or run Jarvis TTS. Error: {e}")

if __name__ == "__main__":
    main()