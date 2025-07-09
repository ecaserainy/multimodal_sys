from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration, BitsAndBytesConfig
from PIL import Image
import torch

class ImageModel:
    def __init__(self):
        self.model = None
        self.processor = None

    def load_model(self):
        model_path = "C:/Users/songi/PycharmProjects/PythonProject/Models/llava-v1.6-vicuna-7b"
        if self.model is None:
            print("[ImageModel] Loading model...")
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )
            self.processor = LlavaNextProcessor.from_pretrained(model_path)
            self.model = LlavaNextForConditionalGeneration.from_pretrained(
                model_path,
                device_map="auto",
                quantization_config=quant_config
            )
            print("[ImageModel] Model loaded.")

    def generate_caption(self, image_path):
        self.load_model()
        image = Image.open(image_path).convert("RGB")
        conversation = [
            {"role": "user", "content": [
                {"type": "text", "text": "Describe this image in detail."},
                {"type": "image", "image": image}
            ]}
        ]
        prompt = self.processor.apply_chat_template(conversation, add_generation_prompt=True)
        inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs, max_new_tokens=50)
        generated_text = self.processor.batch_decode(output, skip_special_tokens=True)[0]

        if "<|assistant|>" in generated_text:
            generated_text = generated_text.split("<|assistant|>")[-1].strip()

        return generated_text

# class ImageModel:
#     def __init__(self):
#         model_path = "C:/Users/songi/PycharmProjects/PythonProject/Models/llava-v1.6-vicuna-7b"
#         print("Loading LLaVA model...")
#         self.model = LlavaNextForConditionalGeneration.from_pretrained(
#             model_path,
#             torch_dtype=torch.float16,
#             device_map="auto",
#         )
#         self.processor = LlavaNextProcessor.from_pretrained(model_path,use_fast_tokenizer=True)
#         print("LLaVA model loaded.")
#
#     def generate_caption(self, image_path):
#         image = Image.open(image_path).convert("RGB")
#         conversation = [
#             {"role": "user", "content": [
#                 {"type": "text", "text": "Describe this image in detail."},
#                 {"type": "image"}
#             ]}
#         ]
#         prompt = self.processor.apply_chat_template(conversation, add_generation_prompt=True)
#         inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.model.device)
#         outputs = self.model.generate(**inputs, max_new_tokens=80)
#         result = self.processor.decode(outputs[0], skip_special_tokens=True)
#         return result
