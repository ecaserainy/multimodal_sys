import torch
from transformers import pipeline

class AudioModel:
    def __init__(self, model_path="C:/Users/songi/PycharmProjects/PythonProject/Models/whisper-medium"):
        print("[AudioModel] Loading Whisper model...")
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_path,
            device=0
        )
        print("[AudioModel] Model loaded.")

    def generate(self, audio_path):
        result = self.pipe(audio_path)
        return result["text"].strip()

    def run_inference(self, audio_path: str):
        print(f"[AudioModel] Inference on: {audio_path}")
        answer = self.generate(audio_path)
        return {"response": answer}

def load_audio_model():
    return AudioModel()

def run_audio_inference(model, audio_path):
    return model.run_inference(audio_path)
