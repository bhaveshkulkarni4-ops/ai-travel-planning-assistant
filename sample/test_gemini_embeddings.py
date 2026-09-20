import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found in .env")


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=api_key,
    task_type="RETRIEVAL_DOCUMENT",
)


texts = [
    "Singapore has an efficient public transportation system.",
    "Gardens by the Bay is a major attraction in Singapore.",
    "Singapore offers many family-friendly attractions.",
]


vectors = embeddings.embed_documents(texts)

print("\nGemini embedding test successful.")
print(f"Number of texts: {len(texts)}")
print(f"Number of vectors: {len(vectors)}")
print(f"Vector dimensions: {len(vectors[0])}")