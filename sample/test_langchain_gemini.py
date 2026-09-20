import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found in .env")


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    temperature=0.2,
)

response = llm.invoke(
    "Give me three important things a family should consider when planning a "
    "three-day trip to Singapore."
)

print("\nLangChain + Gemini response:\n")
print(response.content)