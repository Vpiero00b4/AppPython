from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os

Window.size = (400, 600)  # Tamaño de la ventana

class SimpleDownloaderApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        self.label = Label(text='Ingresa el URL del vídeo de YouTube', size_hint_y=None, height=dp(40))
        self.add_widget(self.label)
        
        self.input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        self.add_widget(self.input)
        
        self.download_button = Button(text='Descargar MP3', size_hint_y=None, height=dp(40))
        self.download_button.bind(on_press=self.descargar)
        self.add_widget(self.download_button)
        
        self.status = Label(text='', size_hint_y=None, height=dp(40))
        self.add_widget(self.status)

    def descargar(self, instance):
        url = self.input.text
        if not url:
            self.status.text = 'Por favor, ingresa un URL'
            self.status.color = (1, 0, 0, 1)
            return

        self.status.text = 'Descargando...'
        self.status.color = (1, 1, 1, 1)

        try:
            yt = YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path='.')
            nombre_base, ext = os.path.splitext(out_file)
            nuevo_nombre = nombre_base + '.mp3'
            
            # Procesar el archivo de audio
            clip = AudioFileClip(out_file)
            clip.write_audiofile(nuevo_nombre)
            clip.close()
            
            # Eliminar el archivo temporal
            os.remove(out_file)
            
            self.status.text = 'Descarga completada con éxito'
            self.status.color = (0, 1, 0, 1)
            self.input.text = ''  # Limpiar el cuadro de texto después de la descarga exitosa
        except Exception as e:
            self.status.text = f'Error: {str(e)}'
            self.status.color = (1, 0, 0, 1)

class SimpleDownloaderAppApp(App):
    def build(self):
        return SimpleDownloaderApp()

if __name__ == '__main__':
    SimpleDownloaderAppApp().run()
