import asyncio
from celery.result import AsyncResult
from langchain.agents import initialize_agent, Tool, AgentType
from services.rag_retriever import RAGRetriever
from services.di import get_container


class MultimodalManager:
    def __init__(
        self,
        rag_data_dir: str = "data/rag_doc",
        rag_persist_dir: str = "storage",
    ):

        self.text_model = get_container().text_model
        self.image_model = get_container().image_model
        self.audio_model = get_container().audio_model


        self.rag_retriever = RAGRetriever(
            data_dir=rag_data_dir,
            persist_dir=rag_persist_dir,
        )


        self.text_infer = self.text_model.run_inference
        self.image_infer = self.image_model.run_inference
        self.audio_infer = self.audio_model.run_inference
        self.knowledge_base_query = self.rag_retriever.query


        self.tools = [
            Tool(name="TextModel", func=self.text_infer, description="文本问答与指令"),
            Tool(name="ImageModel", func=self.image_infer, description="图像识别与描述"),
            Tool(name="AudioModel", func=self.audio_infer, description="语音转文本"),
            Tool(name="KnowledgeBase", func=self.knowledge_base_query, description="检索企业知识库并回答"),
        ]


        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.rag_retriever.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False
        )

    async def run_agent(self, task_data: dict):
        text = task_data.get("text", "")
        image_path = task_data.get("image_path")
        audio_path = task_data.get("audio_path")


        image_caption = await asyncio.to_thread(self.image_infer, image_path) if image_path else None
        audio_transcript = await asyncio.to_thread(self.audio_infer, audio_path) if audio_path else None

        combined_input = text
        if image_caption:
            combined_input += f"\n[图像内容]: {image_caption}"
        if audio_transcript:
            combined_input += f"\n[语音内容]: {audio_transcript}"


        reply = await asyncio.to_thread(self.agent.run, combined_input)
        return reply

    async def process_task(self, task_data: dict):
        return await self.run_agent(task_data)

    async def dispatch_tasks(self, text=None, image_path=None, audio_path=None):
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
        results = {}
        start = asyncio.get_event_loop().time()
        while True:
            all_ready = True
            for modal, tid in task_ids.items():
                res = AsyncResult(tid)
                if res.ready():
                    results[modal] = res.result
                else:
                    all_ready = False
            if all_ready or (asyncio.get_event_loop().time() - start) > timeout:
                break
            await asyncio.sleep(1)
        return results
