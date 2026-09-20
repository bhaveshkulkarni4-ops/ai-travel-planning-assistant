import asyncio

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

from app.rag import retrieve_context
from app.mcp_tools import get_weather


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    temperature=0.2,
    max_retries=0,
)


async def create_itinerary(
    start_date: str,
    traveler_preferences: str = "",
):
    # -----------------------------------------
    # 1. Retrieve Singapore travel knowledge
    # -----------------------------------------

    rag_question = """
    Create a three-day Singapore itinerary.

    Include:
    - major attractions
    - indoor and outdoor activities
    - neighborhoods
    - transport considerations
    - family-friendly activities where appropriate
    - alternatives for rainy weather
    """

    rag_result = retrieve_context(rag_question)

    # -----------------------------------------
    # 2. Get live weather through MCP
    # -----------------------------------------

    weather_result = await get_weather.ainvoke(
        {
            "location": "Singapore",
            "forecast_days": 3,
            "start_date": start_date,
        }
    )

    # -----------------------------------------
    # 3. Ask Gemini to combine RAG + MCP
    # -----------------------------------------

    prompt = f"""
You are a Singapore travel planning assistant.

Create a practical three-day itinerary for Singapore.

TRAVEL DATES:
{start_date} for three days

TRAVELER PREFERENCES:
{traveler_preferences or "No specific preferences provided."}

KNOWLEDGE BASE:
Use the following retrieved Singapore travel information as the
source for destination facts, attractions, activities, neighborhoods,
transport and itinerary ideas.

{rag_result}

CURRENT WEATHER FROM MCP:
The following information was obtained from our weather MCP tool.
Use it to adjust outdoor and indoor activities.

{weather_result}

IMPORTANT RULES:

1. Use the knowledge-base information for Singapore destination facts.
2. Use the MCP weather information for current/future weather.
3. Do not invent attractions or destination facts that are not
   supported by the knowledge base.
4. If weather is unfavorable for an outdoor activity, prefer a
   suitable indoor alternative supported by the knowledge base.
5. Clearly indicate that the weather information came from MCP.
6. Clearly distinguish destination facts from your itinerary suggestions.
7. Produce a day-by-day itinerary.
8. Include a short explanation of how weather affected the plan.
"""

    try:
        response = await llm.ainvoke(prompt)

        answer = response.content

        if isinstance(answer, list):
            text_parts = []

            for item in answer:
                if isinstance(item, dict) and item.get("text"):
                    text_parts.append(item["text"])

            answer = "\n".join(text_parts)

        return answer

    except Exception as exc:
        error_text = str(exc)

        if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text or "quota" in error_text.lower():
            return (
                "The Gemini AI service is temporarily unavailable because the API quota "
                "has been reached. Please try again after the quota resets."
            )

        return (
            "The travel-planning AI service is temporarily unavailable. "
            "Please try again later."
        )


if __name__ == "__main__":

    result = asyncio.run(
        create_itinerary(
            start_date="2026-09-27",
            traveler_preferences="First-time visitors to Singapore",
        )
    )

    print("\n" + "=" * 70)
    print("WEATHER-AWARE SINGAPORE ITINERARY")
    print("=" * 70)
    print(result)