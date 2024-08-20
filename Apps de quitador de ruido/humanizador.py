import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment, effects
import numpy as np
import os
import librosa
import librosa.display
import soundfile as sf
import scipy.signal

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    if file_path:
        process_audio(file_path)

def process_audio(file_path):
    # Convertir MP3 a WAV
    audio = AudioSegment.from_mp3(file_path)
    audio.export("temp.wav", format="wav")

    # Cargar archivo WAV
    y, sr = librosa.load("temp.wav", sr=None)

    # Normalización
    y = librosa.util.normalize(y)

    # Ecualización para resaltar la voz (frecuencias entre 300 y 3000 Hz)
    y = librosa.effects.equalizer(y, sr, low=300, high=3000)

    # Aplicar reverberación
    y_reverb = librosa.effects.preemphasis(y, coef=0.97)

    # Ajuste de tono (pitch) y formantes para hacer la voz más natural
    y_shifted = librosa.effects.pitch_shift(y_reverb, sr, n_steps=2)

    # Suavizar para reducir artefactos
    y_smoothed = librosa.effects.time_stretch(y_shifted, rate=0.9)

    # Guardar el archivo de audio procesado
    output_file = os.path.splitext(file_path)[0] + "_improved_voice.wav"
    sf.write(output_file, y_smoothed, sr)

    # Limpiar archivo temporal
    os.remove("temp.wav")
    
    result_label.config(text=f"Audio procesado y mejorado guardado en: {output_file}")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Mejora de Voz")

upload_button = tk.Button(root, text="Subir Archivo MP3", command=upload_file)
upload_button.pack(pady=20)

result_label = tk.Label(root, text="")
result_label.pack(pady=20)

root.mainloop()
