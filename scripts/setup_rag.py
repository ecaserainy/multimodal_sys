from pathlib import Path


def init_rag_documents():
    rag_dir = Path("data/rag_doc")
    rag_dir.mkdir(parents=True, exist_ok=True)

    docs = {
        "welcome.txt": "欢迎使用智能客服系统！本系统支持文本、图像和语音多模态交互。",
        "contact.txt": "技术支持联系方式：\n邮箱：support@example.com\n电话：400-123-4567",
        "faq.txt": "常见问题解答：\nQ: 如何重置密码？\nA: 访问设置页面选择'忘记密码'选项"
    }

    for filename, content in docs.items():
        file_path = rag_dir / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"创建示例文档: {file_path}")


if __name__ == "__main__":
    init_rag_documents()