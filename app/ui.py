import asyncio
import inspect
from datetime import date, timedelta

import streamlit as st


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="Singapore AI Travel Assistant",
    page_icon="🇸🇬",
    layout="wide",
)


# =========================================================
# Travel Agent
# =========================================================

@st.cache_resource
def load_travel_agent():
    """Load the existing Singapore travel agent."""

    from app.travel_agent import create_itinerary

    return create_itinerary


def execute_agent(
    start_date: str,
    traveler_preferences: str,
):
    """Execute the existing async travel agent."""

    create_itinerary = load_travel_agent()

    result = create_itinerary(
        start_date=start_date,
        traveler_preferences=traveler_preferences,
    )

    if inspect.isawaitable(result):
        result = asyncio.run(result)

    return result


# =========================================================
# Session state
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# Header
# =========================================================

st.title("🇸🇬 Singapore AI Travel Assistant")

st.markdown(
    """
Plan a Singapore trip using **RAG + custom MCP tools**.

- 📚 **RAG** — Singapore travel knowledge from the local knowledge base
- 🌦️ **MCP Weather** — current/future weather information
- 💱 **MCP Currency** — current exchange-rate conversion
- 🧠 **Conversation Context** — retain your travel preferences
"""
)


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.header("Trip Details")

    default_start_date = date.today() + timedelta(days=7)

    start_date = st.date_input(
        "Trip start date",
        value=default_start_date,
    )

    st.caption(
        f"Selected start date: {start_date.isoformat()}"
    )

    st.divider()

    st.header("Architecture")

    st.markdown(
        """
**Knowledge Base**

Travel sources  
↓  
Document chunks  
↓  
Local embeddings  
↓  
FAISS  
↓  
RAG retrieval

**Current Information**

Travel Agent  
↓  
MCP Client  
↓  
Custom MCP Server  
↓  
Weather / Currency APIs
"""
    )

    st.divider()

    st.header("Conversation")

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# =========================================================
# Previous conversation
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# User input
# =========================================================

question = st.chat_input(
    "Example: Create a 3-day itinerary for my family and adjust it according to the weather..."
)


if question:

    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


    # -----------------------------------------------------
    # Build conversation context
    # -----------------------------------------------------

    previous_messages = []

    for message in st.session_state.messages[:-1]:
        previous_messages.append(
            f"{message['role'].upper()}: {message['content']}"
        )

    conversation_context = "\n".join(previous_messages)

    traveler_preferences = question

    if conversation_context:

        traveler_preferences = f"""
Current user request:
{question}

Previous conversation context:
{conversation_context}

Use the previous conversation context to preserve relevant
traveler preferences and requirements.
"""


    # -----------------------------------------------------
    # Execute Travel Agent
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Planning your Singapore trip using RAG and MCP..."
        ):

            try:

                result = execute_agent(
                    start_date=start_date.isoformat(),
                    traveler_preferences=traveler_preferences,
                )

                # -----------------------------------------
                # Handle possible result formats
                # -----------------------------------------

                if isinstance(result, dict):

                    if "answer" in result:
                        answer = result["answer"]

                    elif "response" in result:
                        answer = result["response"]

                    else:
                        answer = str(result)

                else:
                    answer = str(result)


                # -----------------------------------------
                # Handle Gemini content lists
                # -----------------------------------------

                if isinstance(answer, list):

                    text_parts = []

                    for item in answer:

                        if isinstance(item, dict):

                            if item.get("text"):
                                text_parts.append(
                                    item["text"]
                                )

                        elif isinstance(item, str):

                            text_parts.append(item)

                    answer = "\n".join(text_parts)


                # -----------------------------------------
                # Display response
                # -----------------------------------------

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )


            except Exception as exc:

                error_message = (
                    "I couldn't complete the travel-planning request.\n\n"
                    f"**Error:** `{exc}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )