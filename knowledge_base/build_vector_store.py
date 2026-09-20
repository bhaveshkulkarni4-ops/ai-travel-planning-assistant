from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

load_dotenv()


def load_documents():
    documents = []

    for file_path in sorted(DOCUMENTS_DIR.glob("*.md")):
        print(f"Loading: {file_path.name}")

        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
        )

        file_documents = loader.load()


        source_metadata = {
    "visit_singapore_itineraries.md": {
        "title": "Visit Singapore — Singapore Travel Guide",
        "url": "https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/q4-singapore-insider-2019-en.pdf",
    },
    "visit_singapore_travel_guide.md": {
        "title": "Visit Singapore — Travel Guide",
        "url": "https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/q3_singapore-insider-2019_en.pdf",
    },
    "wikivoyage_singapore.md": {
        "title": "Wikivoyage — Singapore Travel Guide",
        "url": "https://en.wikivoyage.org/wiki/Singapore",
    },
}
        
        for document in file_documents:
            document.metadata["source_file"] = file_path.name

            metadata = source_metadata.get(file_path.name)

        if metadata:
            document.metadata["source_title"] = metadata["title"]
            document.metadata["source_url"] = metadata["url"]

        documents.extend(file_documents)

    return documents


def clean_documents(documents):
    for document in documents:
        text = document.page_content

        # Fix common encoding artifacts from extracted web/PDF text.
        text = text.replace("â€”", "—")
        text = text.replace("â€“", "–")
        text = text.replace("â€™", "'")
        text = text.replace("â€œ", '"')
        text = text.replace("â€", '"')

        document.page_content = text.strip()

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index

    return chunks


def build_vector_store(chunks):
    print("\nCreating Gemini embeddings...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings,
    )

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(VECTOR_STORE_DIR))

    print(f"Vector store saved to: {VECTOR_STORE_DIR}")


def main():
    print("Starting RAG knowledge-base ingestion...\n")

    documents = load_documents()

    print(f"\nDocuments loaded: {len(documents)}")

    documents = clean_documents(documents)

    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    build_vector_store(chunks)

    print("\nRAG knowledge-base ingestion completed successfully.")


if __name__ == "__main__":
    main()