from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_STORE_DIR = (
    BASE_DIR
    / "knowledge_base"
    / "vector_store"
)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Load FAISS vector store
# ---------------------------------------------------------

def load_vector_store():
    """
    Load the locally created FAISS knowledge base.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store


# ---------------------------------------------------------
# Retrieve relevant knowledge
# ---------------------------------------------------------

def retrieve_context(
    question: str,
    k: int = 5,
) -> list[Any]:
    """
    Retrieve the most relevant knowledge-base chunks
    for the user's question.
    """

    vector_store = load_vector_store()

    results = vector_store.similarity_search_with_score(
        question,
        k=k,
    )

    return results


# ---------------------------------------------------------
# Build clean context for Gemini
# ---------------------------------------------------------

def build_context(
    results: list[Any],
) -> str:
    """
    Convert retrieved documents into clean grounded
    context for the LLM.

    Each source includes:
    - source title
    - source URL
    - relevance score
    - retrieved content
    """

    context_parts = []

    for index, (document, score) in enumerate(
        results,
        start=1,
    ):

        source_title = document.metadata.get(
            "source_title",
            document.metadata.get(
                "source_file",
                "Unknown source",
            ),
        )

        source_url = document.metadata.get(
            "source_url",
            "",
        )

        context_parts.append(
            f"""
SOURCE {index}
Title: {source_title}
URL: {source_url}
Relevance score: {score:.4f}

Content:
{document.page_content}
"""
        )

    return "\n".join(context_parts)


# ---------------------------------------------------------
# Extract unique source references
# ---------------------------------------------------------

def get_sources(
    results: list[Any],
) -> list[dict]:
    """
    Extract unique source references from retrieved
    knowledge-base documents.
    """

    sources = []

    for document, score in results:

        source = {
            "title": document.metadata.get(
                "source_title",
                document.metadata.get(
                    "source_file",
                    "Unknown source",
                ),
            ),
            "url": document.metadata.get(
                "source_url",
                "",
            ),
            "score": score,
        }

        if source not in sources:
            sources.append(source)

    return sources


# ---------------------------------------------------------
# Clean Gemini response
# ---------------------------------------------------------

def clean_response_content(
    content: Any,
) -> str:
    """
    Convert Gemini response content into clean text.

    Gemini may return either:
    - a normal string
    - a list containing text dictionaries
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(text)

        return "\n".join(text_parts)

    return str(content)


# ---------------------------------------------------------
# Generate grounded RAG answer
# ---------------------------------------------------------

def generate_answer(
    question: str,
) -> dict:
    """
    Generate a grounded Singapore travel answer
    using the retrieved knowledge base.

    Returns:
        {
            "answer": "...",
            "sources": [...]
        }
    """

    # ---------------------------------------------
    # 1. Retrieve relevant documents
    # ---------------------------------------------

    results = retrieve_context(
        question,
        k=5,
    )

    # ---------------------------------------------
    # 2. Build clean context
    # ---------------------------------------------

    context = build_context(
        results
    )

    # ---------------------------------------------
    # 3. Extract source references
    # ---------------------------------------------

    sources = get_sources(
        results
    )

    # ---------------------------------------------
    # 4. Create Gemini model
    # ---------------------------------------------

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=None,
        max_retries=0,
    )

    # ---------------------------------------------
    # 5. Grounded RAG prompt
    # ---------------------------------------------

    prompt = f"""
You are a Singapore travel planning assistant.

Answer the user's question using ONLY the knowledge-base
context provided below.

IMPORTANT RULES:

1. Use the retrieved knowledge base as the source of
   destination facts.

2. Do not invent attractions, locations, transportation
   details, cultural information, activities, or other
   destination facts that are not supported by the
   retrieved context.

3. If the retrieved context does not contain enough
   information to answer the question, clearly state:

   "The knowledge base does not contain enough information
   to answer this part of the question."

4. You may organize and summarize retrieved information
   to make the answer useful.

5. Do not present unsupported assumptions as facts.

6. Keep the answer concise and practical.

7. Clearly distinguish factual information from
   itinerary or recommendation suggestions.

8. At the end of the answer, provide the source title
   and URL used for the destination information.

KNOWLEDGE-BASE CONTEXT
======================

{context}


USER QUESTION
=============

{question}
"""

    # ---------------------------------------------
    # 6. Generate answer
    # ---------------------------------------------

    response = llm.invoke(
        prompt
    )

    # ---------------------------------------------
    # 7. Clean Gemini response
    # ---------------------------------------------

    answer = clean_response_content(
        response.content
    )

    # ---------------------------------------------
    # 8. Return answer + sources
    # ---------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
    }


# ---------------------------------------------------------
# Standalone RAG test
# ---------------------------------------------------------

if __name__ == "__main__":

    question = (
        "What are some family-friendly attractions "
        "and activities in Singapore?"
    )

    result = generate_answer(
        question
    )

    print("\n" + "=" * 80)
    print("RAG ANSWER")
    print("=" * 80)

    print(
        result["answer"]
    )

    print("\n" + "=" * 80)
    print("RETRIEVED SOURCES")
    print("=" * 80)

    for source in result["sources"]:

        print(
            f"\nTitle: {source['title']}"
        )

        print(
            f"URL: {source['url']}"
        )

        print(
            f"Score: {source['score']:.4f}"
        )