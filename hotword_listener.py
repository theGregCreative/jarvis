import pvporcupine
import pyaudio
import struct
import os

KEYWORD_PATH = "wakewords/hey_jarvis_linux.ppn"
MODEL_PATH = "wakewords/porcupine_params.pv"

def listen_for_wake_word(callback):
    porcupine = pvporcupine.create(
        access_key="YOUR_PICOVOICE_ACCESS_KEY",  # can be omitted if using local .ppn + .pv
        keyword_paths=[KEYWORD_PATH],
        model_path=MODEL_PATH,
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("🔊 Waiting for 'Hey Jarvis'...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("🎤 Wake word detected!")
                callback()
    except KeyboardInterrupt:
        print("🛑 Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
