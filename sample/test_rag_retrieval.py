from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = BASE_DIR / "knowledge_base" / "vector_store"


def main():
    print("Loading FAISS vector store...\n")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    question = "What are some family-friendly attractions and activities in Singapore?"

    print(f"Question: {question}\n")
    print("Top retrieved knowledge-base chunks:\n")

    results = vector_store.similarity_search_with_score(
        question,
        k=5,
    )

    for index, (document, score) in enumerate(results, start=1):
        print("=" * 80)
        print(f"RESULT {index}")
        print(f"Score: {score:.4f}")
        print(f"Source file: {document.metadata.get('source_file')}")
        print(f"Source title: {document.metadata.get('source_title')}")
        print(f"Source URL: {document.metadata.get('source_url')}")
        print("\nContent:")
        print(document.page_content[:1000])
        print()


if __name__ == "__main__":
    main()  