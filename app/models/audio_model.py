import torch
from transformers import pipeline

class AudioModel:
    def __init__(self, model_name="C:/Users/songi/PycharmProjects/PythonProject/Models/whisper-medium"):
        print("Loading Whisper model...")
        self.pipe = pipeline("automatic-speech-recognition", model=model_name, device=0)
        print("Whisper model loaded.")

    def transcribe(self, audio_file_path):
        result = self.pipe(audio_file_path)
        return result["text"]
