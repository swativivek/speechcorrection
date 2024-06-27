from gtts import gTTS
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import os
import language_tool_python
import time
from vosk import Model, KaldiRecognizer
import pyaudio
import json

kivy.require('1.11.1')

class SpeechPracticeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.label = Label(text='Press the button and start speaking...', font_size='20sp', size_hint=(1, 0.5))
        self.layout.add_widget(self.label)
        
        self.button = Button(text='Start Speaking', size_hint=(1, 0.3), background_color=(0.1, 0.5, 0.7, 1), font_size='20sp')
        self.button.bind(on_press=self.recognize_speech)
        self.layout.add_widget(self.button)
        
        return self.layout
    
    def recognize_speech(self, instance):
        self.label.text = "Listening..."
        try:
            text = self.get_recognized_text()
            self.label.text = f'You said: {text}'
            self.correct_speech(text)
        except Exception as e:
            self.label.text = f"An error occurred: {e}"
    
    def get_recognized_text(self, retries=3):
        model_path = "D:\\Vosk\\vosk-model-small-en-us"  # Make sure this path is correct
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path {model_path} does not exist.")
        
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        stream.start_stream()

        for attempt in range(retries):
            try:
                print(f"Attempt {attempt+1} to recognize speech")
                while True:
                    data = stream.read(4000, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        result = recognizer.Result()
                        text = json.loads(result).get('text', '')
                        print(f"Recognized text: {text}")
                        if text:
                            stream.stop_stream()
                            stream.close()
                            p.terminate()
                            return text
            except Exception as e:
                print(f"An error occurred: {e}")
                if attempt < retries - 1:
                    self.label.text = f"Retrying... ({attempt+1}/{retries})"
                    time.sleep(2)  # Wait before retrying
                else:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    raise Exception(f"Failed to use Vosk API after several retries: {e}")
    
    def correct_speech(self, text):
        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        self.label.text = f'Corrected: {corrected_text}'
        self.speak_text(corrected_text)
    
    def speak_text(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        os.system("start output.mp3")

if __name__ == '__main__':
    SpeechPracticeApp().run()
