import os,torch
import logging
from pathlib import Path
from typing import List, Optional
from langchain_huggingface import HuggingFacePipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("RAGRetriever")


class RAGRetriever:
    def __init__(
        self,
        data_dir: str = "data/rag_doc",
        persist_dir: str = "storage",
        embedding_model: str = "C:/Users/songi/PycharmProjects/PythonProject/Models/bge-small-zh-v1.5",
        llm_model_path: str = "C:/Users/songi/PycharmProjects/PythonProject/Models/DeepSeek-R1-Distill-Qwen-1.5B",
        top_k: int = 5,
    ):
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.top_k = top_k

        logger.info(f"加载本地嵌入模型：{embedding_model}")
        self.embed_model = HuggingFaceEmbedding(
            model_name=embedding_model,
            local_files_only=True
        )

        logger.info(f"加载本地LLM：{llm_model_path}")
        self.llm = self._load_local_llm(llm_model_path)

        if self._can_load_index():
            try:
                sc = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                self.index = load_index_from_storage(sc)
                logger.info("索引加载成功")
            except Exception as e:
                logger.error(f"索引加载失败，重建索引 {e}")
                self._build_index()
        else:
            self._build_index()

    def _load_local_llm(self, model_path: str):
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            temperature=0.3,
            top_p=0.95,
            repetition_penalty=1.1
        )
        return HuggingFacePipeline(pipeline=pipe)

    def _can_load_index(self) -> bool:
        return self.persist_dir.exists() and any(self.persist_dir.iterdir())

    def _build_index(self):
        logger.info("开始构建索引...")
        reader = SimpleDirectoryReader(input_dir=str(self.data_dir))
        docs = reader.load_data()
        logger.info(f"读取 {len(docs)} 个文档")
        self.index = VectorStoreIndex.from_documents(
            docs, embed_model=self.embed_model
        )
        self.index.storage_context.persist(persist_dir=str(self.persist_dir))
        logger.info("索引构建完成")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[str]:
        if not hasattr(self, "index"):
            return []
        k = top_k or self.top_k
        retriever = VectorIndexRetriever(index=self.index, similarity_top_k=k)
        return [node.text for node in retriever.retrieve(query)]

    def query(self, query: str) -> str:
        if not hasattr(self, "index") or self.llm is None:
            return "索引或LLM未初始化"
        qe = self.index.as_query_engine(llm=self.llm)
        resp = qe.query(query)
        return str(resp)
