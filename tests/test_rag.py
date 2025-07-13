import sys
import os
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_retriever import RAGRetriever
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRAG")


def test_rag_retriever():
    """测试RAG检索器的基本功能"""
    logger.info("初始化RAGRetriever...")
    retriever = RAGRetriever()

    logger.info("测试检索功能...")
    results = retriever.retrieve("技术支持")
    assert isinstance(results, list), "检索结果应该是列表"
    for i, res in enumerate(results, 1):
        logger.info(f"结果 {i}: {res[:50]}...")

    logger.info("测试问答功能...")
    answer = retriever.query("如何联系技术支持?")
    assert isinstance(answer, str), "回答应该是字符串"
    logger.info(f"问答结果: {answer}")

    logger.info("所有测试通过")


if __name__ == "__main__":
    os.makedirs("data/rag_doc", exist_ok=True)
    if not any(Path("data/rag_doc").iterdir()):
        with open("data/rag_doc/support.txt", "w") as f:
            f.write("技术支持联系方式：\n邮箱：support@example.com\n电话：400-123-4567")

    test_rag_retriever()