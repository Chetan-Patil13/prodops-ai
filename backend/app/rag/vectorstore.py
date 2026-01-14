from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
import os
from dotenv import load_dotenv
 
# Load env file (same logic as seed_data.py)
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env.example"
load_dotenv(env_path)

VECTOR_DB_PATH = "data/vectorstore"


def build_vectorstore(documents):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    return vectorstore


def load_vectorstore():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(VECTOR_DB_PATH, embeddings,allow_dangerous_deserialization=True)
