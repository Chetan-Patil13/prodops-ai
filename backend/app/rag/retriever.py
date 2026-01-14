from app.rag.vectorstore import load_vectorstore


def retrieve_docs(query: str, k: int = 3):
    vectorstore = load_vectorstore()
    return vectorstore.similarity_search(query, k=k)
