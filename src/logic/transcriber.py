import asyncio
import os
import time
import re
import sounddevice as sd
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile
import torch

model = None

def load_model():
    torch.cuda.empty_cache()

    device, model_name = ("cuda", "turbo") if torch.cuda.is_available() else ("cpu", "small")
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
    global model
    model = whisper.load_model(model_name).to(device)

def extract_number(text):
    pattern = r'-?\d+(?:\.\d+)?'

    number = re.findall(pattern, text)

    #print(f"Numeri trovati nel testo: {number}, {len(number)}")

    if len(number) > 0:
        last_number = number[-1]

        return int(last_number)
    return None


def capture_audio_sync():
    duration = 8  # secondi
    fs = 16000  # frequenza di campionamento richiesta da Whisper

    print("Inizio registrazione...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # aspetta fine registrazione
    print("Registrazione terminata!")

    # Salva temporaneamente in un WAV
    # Salva temporaneamente il file WAV
    tmp_path = os.path.join(tempfile.gettempdir(), "tmp_audio.wav")
    scipy.io.wavfile.write(tmp_path, fs, (audio * 32767).astype(np.int16))

    # Trascrivi audio
    start_time = time.time()
    result = model.transcribe(tmp_path, language="it")
    elapsed = time.time() - start_time

    print(result["text"], f"(Tempo: {elapsed:.2f}s)")
    return result["text"]


def capture_audio():
    #loop = asyncio.get_event_loop()
    #return await loop.run_in_executor(executor, capture_audio_sync)
    text = capture_audio_sync()

    if "passo" in text.lower():
        return "PASSO"
    else:
        return extract_number(text)
