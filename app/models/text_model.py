from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

class TextModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def load_model(self):
        model_path = "C:/Users/songi/PycharmProjects/PythonProject/Models/DeepSeek-R1-Distill-Qwen-1.5B"
        if self.model is None:
            print("[TextModel] Loading model...")
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                quantization_config=quant_config
            )
            print("[TextModel] Model loaded.")

    def build_prompt(self, question, context=None):
        prompt = "你是专业数据分析助手，回答精准且有逻辑。"
        if context:
            prompt += f"\n相关背景信息：{context}"
        prompt += f"\n请回答以下问题：{question}\n回答："
        return prompt

    def generate(self, question, context=None, max_new_tokens=50):
        self.load_model()
        prompt = self.build_prompt(question, context)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return answer[len(prompt):].strip()





# class TextModel:
#     def __init__(self, model_path="C:/Users/songi/PycharmProjects/PythonProject/Models/DeepSeek-R1-Distill-Qwen-1.5B", device="cuda"):
#         self.device = device
#         print("Loading DeepSeek model...")
#         self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
#         self.model = AutoModelForCausalLM.from_pretrained(
#             model_path,
#             device_map="auto",
#             torch_dtype=torch.float16
#         )
#         self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
#         print("DeepSeek model loaded.")
#
#     def generate(self, prompt):
#         result = self.pipe(prompt, max_new_tokens=100)
#         return result[0]['generated_text']
