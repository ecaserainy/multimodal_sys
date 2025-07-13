from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
from PIL import Image
import torch

class ImageModel:
    def __init__(self):
        self.model = None
        self.processor = None

    def load_model(self):
        model_path = "C:/Users/songi/PycharmProjects/PythonProject/Models/SmolVLM-Instruct"
        if self.model is None:
            print("[ImageModel] Loading model...")
            self.processor = LlavaNextProcessor.from_pretrained(model_path, trust_remote_code=True)
            self.model = LlavaNextForConditionalGeneration.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16
            )
            print("[ImageModel] Model loaded.")

    def generate(self, image_path, question="请描述这张图片的内容"):
        self.load_model()
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(text=question, images=image, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=50)
        answer = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return answer.strip()

    def run_inference(self, image_path: str):
        print(f"[ImageModel] Inference on: {image_path}")
        answer = self.generate(image_path)
        return {"response": answer}


def load_image_model():
    return ImageModel()

def run_image_inference(model, image_path):
    return model.run_inference(image_path)





