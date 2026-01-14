from pathlib import Path
from app.rag.loader import load_documents
from app.rag.vectorstore import build_vectorstore

# Resolve absolute path safely
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_PATH = BASE_DIR / "data" / "sop_docs"


def main():
    print("Loading SOP documents from:", DOCS_PATH)

    documents = load_documents(str(DOCS_PATH))
    print(f"Loaded {len(documents)} documents")

    if not documents:
        raise RuntimeError("No SOP documents found. Check sop_docs folder.")

    print("Building vector store...")
    build_vectorstore(documents)

    print("Vector store built successfully.")


if __name__ == "__main__":
    main()
