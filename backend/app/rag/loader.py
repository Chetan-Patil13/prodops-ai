from langchain_community.document_loaders import TextLoader
from pathlib import Path


def load_documents(folder_path: str):
    docs = []
    for file in Path(folder_path).glob("*.md"):
        loader = TextLoader(str(file))
        docs.extend(loader.load())
    return docs
