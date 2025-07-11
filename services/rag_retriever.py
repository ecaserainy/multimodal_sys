import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.indices import load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from langchain_openai import ChatOpenAI

class RAGRetriever:
    def __init__(
        self,
        data_dir: str,
        persist_dir: str = "storage",
        openai_api_key: str = None,
        model_name: str = "gpt-3.5-turbo",
        top_k: int = 5,
    ):
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key

        self.llm = ChatOpenAI(model_name=model_name, api_key=openai_api_key)
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.top_k = top_k

        if os.path.isdir(self.persist_dir) and os.listdir(self.persist_dir):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                self.index = load_index_from_storage(storage_context)
                print(f"[RAGRetriever] 加载索引成功：{self.persist_dir}")
            except Exception as e:
                print(f"[RAGRetriever] 加载索引失败，重新构建索引: {e}")
                self._build_index()
        else:
            self._build_index()

    def _build_index(self):
        print("[RAGRetriever] 正在构建索引...")
        reader = SimpleDirectoryReader(input_dir=self.data_dir)
        documents = reader.load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist(persist_dir=self.persist_dir)
        print(f"[RAGRetriever] 索引构建并持久化到：{self.persist_dir}")

    def retrieve(self, query: str, top_k: int = None):
        k = top_k or self.top_k
        retriever = VectorIndexRetriever(index=self.index, similarity_top_k=k)
        results = retriever.retrieve(query)
        return [res.text for res in results]

    def query(self, query: str) -> str:
        query_engine = self.index.as_query_engine(llm=self.llm)
        response = query_engine.query(query)
        return str(response)
