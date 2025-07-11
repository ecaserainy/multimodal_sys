import asyncio
from celery.result import AsyncResult
from langchain.agents import initialize_agent, AgentType

from langchain_openai import ChatOpenAI
from services.rag_retriever import RAGRetriever
from services.di import container
import os

class MultimodalManager:
    def __init__(
            self,
            rag_data_dir: str = "data/rag_documents",
            rag_persist_dir: str = "storage",
            openai_api_key: str = None
    ):
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            raise ValueError("OpenAI API Key is required")

        self.text_model = container.text_model
        self.image_model = container.image_model
        self.audio_model = container.audio_model

        self.rag_retriever = RAGRetriever(
            data_dir=rag_data_dir,
            persist_dir=rag_persist_dir,
            openai_api_key=openai_api_key
        )

        self.agent = initialize_agent(
            tools=self.tools,
            llm=ChatOpenAI(temperature=0),
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False
        )

    def text_infer(self, text: str) -> str:
        return self.text_model.generate(text)

    def image_infer(self, image_path: str) -> str:
        return self.image_model.generate_caption(image_path)

    def audio_infer(self, audio_path: str) -> str:
        return self.audio_model.transcribe(audio_path)

    def knowledge_base_query(self, query_text: str) -> str:
        return self.rag_retriever.query(query_text)

    async def run_agent(self, task_data: dict):
        """
        核心异步多模态智能 Agent 推理入口。
        1. 提取文本、图片路径、音频路径。
        2. 调用单模态模型推理（放在线程池中避免阻塞）。
        3. 整合多模态输入。
        4. 交给 LangChain Agent 推理。
        """
        text = task_data.get("text", "")
        image_path = task_data.get("image_path")
        audio_path = task_data.get("audio_path")

        image_caption = None
        if image_path:
            image_caption = await asyncio.to_thread(self.image_infer, image_path)

        audio_transcript = None
        if audio_path:
            audio_transcript = await asyncio.to_thread(self.audio_infer, audio_path)

        combined_input = text
        if image_caption:
            combined_input += f"\n[图片描述]: {image_caption}"
        if audio_transcript:
            combined_input += f"\n[语音转录]: {audio_transcript}"

        reply = await asyncio.to_thread(self.agent.run, combined_input)
        return reply

    async def dispatch_tasks(self, text=None, image_path=None, audio_path=None):
        """
        异步任务调度：用Celery分发文本、图像、音频异步推理任务。
        """
        from tasks.text_task import text_inference_task
        from tasks.image_task import image_inference_task
        from tasks.audio_task import audio_inference_task

        tasks = {}
        if text:
            tasks["text"] = text_inference_task.delay(text)
        if image_path:
            tasks["image"] = image_inference_task.delay(image_path)
        if audio_path:
            tasks["audio"] = audio_inference_task.delay(audio_path)

        return {modal: task.id for modal, task in tasks.items()}

    async def aggregate_results(self, task_ids: dict, timeout=30):
        """
        异步轮询任务结果直到完成或超时，返回聚合结果。
        """
        results = {}
        start_time = asyncio.get_event_loop().time()

        while True:
            all_ready = True
            for modal, task_id in task_ids.items():
                res = AsyncResult(task_id)
                if res.ready():
                    results[modal] = res.result
                else:
                    all_ready = False

            if all_ready or (asyncio.get_event_loop().time() - start_time) > timeout:
                break
            await asyncio.sleep(1)

        return results
