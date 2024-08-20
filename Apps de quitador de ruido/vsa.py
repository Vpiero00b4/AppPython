import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment, effects
import noisereduce as nr
import numpy as np
import os
import soundfile as sf
import librosa

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    if file_path:
        process_audio(file_path)

def apply_reverb(audio_segment, reverb_amount=0.3):
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
    samples /= np.iinfo(audio_segment.sample_width * 8 - 1).max  # Normalize to [-1, 1]
    
    # Using librosa for reverberation
    reverb_samples = librosa.effects.preemphasis(samples, coef=reverb_amount)
    
    reverb_samples = (reverb_samples * np.iinfo(audio_segment.sample_width * 8 - 1).max).astype(np.int16)  # Denormalize
    
    reverb_audio = AudioSegment(
        reverb_samples.tobytes(), 
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width, 
        channels=audio_segment.channels
    )
    return reverb_audio

def process_audio(file_path):
    # Convertir MP3 a WAV
    audio = AudioSegment.from_mp3(file_path)
    audio.export("temp.wav", format="wav")

    # Cargar archivo WAV
    raw_audio = AudioSegment.from_wav("temp.wav")
    samples = np.array(raw_audio.get_array_of_samples())
    
    # Determinar el formato de los samples
    if raw_audio.sample_width == 2:
        dtype = np.int16
    elif raw_audio.sample_width == 4:
        dtype = np.int32
    else:
        raise ValueError("Formato de sample desconocido")

    samples = np.array(raw_audio.get_array_of_samples(), dtype=dtype)

    # Suponer que el primer segundo es solo ruido
    noise_sample = samples[:raw_audio.frame_rate]

    # Reducir ruido
    reduced_noise = nr.reduce_noise(y=samples, y_noise=noise_sample, sr=raw_audio.frame_rate)

    # Crear nuevo archivo de audio sin ruido
    reduced_audio = AudioSegment(
        reduced_noise.tobytes(), 
        frame_rate=raw_audio.frame_rate,
        sample_width=raw_audio.sample_width, 
        channels=raw_audio.channels
    )

    # Normalizar el audio para que la voz sea más fuerte
    normalized_audio = effects.normalize(reduced_audio)

    # Ecualizar el audio para resaltar la voz (frecuencias entre 300 y 3000 Hz)
    equalized_audio = normalized_audio.low_pass_filter(3000).high_pass_filter(300)

    # Aplicar reverberación
    reverberated_audio = apply_reverb(equalized_audio)

    # Aplicar compresión
    compressed_audio = effects.compress_dynamic_range(reverberated_audio, threshold=-20.0, ratio=4.0)

    output_file = os.path.splitext(file_path)[0] + "_humanized_audio.wav"
    compressed_audio.export(output_file, format="wav")

    # Limpiar archivo temporal
    os.remove("temp.wav")
    
    result_label.config(text=f"Audio procesado y mejorado guardado en: {output_file}")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Humanización de Voz y Reducción de Ruido")

upload_button = tk.Button(root, text="Subir Archivo MP3", command=upload_file)
upload_button.pack(pady=20)

result_label = tk.Label(root, text="")
result_label.pack(pady=20)

root.mainloop()
