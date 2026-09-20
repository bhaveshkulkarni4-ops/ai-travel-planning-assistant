 AI Travel Planning Assistant

A context-aware Singapore Travel Planning Assistant built using Retrieval-Augmented Generation (RAG), custom Model Context Protocol (MCP) tools, Gemini LLM, FAISS vector search, and Streamlit.

The application combines:

- Singapore travel knowledge from public travel resources
- Semantic retrieval using local embeddings and FAISS
- Current weather information through a custom MCP server
- Current currency conversion through a custom MCP server
- Conversation context for multi-turn travel planning
- A simple Streamlit user interface

---

## 1. Solution Overview

The assistant is designed to answer Singapore travel questions using two different information paths.

### Knowledge Base / RAG

RAG is used for relatively stable destination information such as:

- Attractions
- Neighbourhoods
- Transportation
- Cultural information
- Food and local experiences
- Indoor and outdoor activities
- Itinerary ideas
- Practical travel information

### MCP

MCP tools are used for current or dynamic information such as:

- Weather forecasts
- Currency conversion

The application deliberately separates destination knowledge from current external information.

---

## 2. Architecture

```text
                         ┌──────────────────────┐
                         │       Chat UI        │
                         │      Streamlit       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │     Travel AI Agent      │
                     │        LangChain         │
                     │                          │
                     │   Prompt + User Context  │
                     └───────────┬──────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌────────────┐     ┌──────────────┐
        │    RAG    │      │ MCP Client │     │ Conversation │
        │ Retriever │      │            │     │    Context   │
        └─────┬─────┘      └─────┬──────┘     └──────────────┘
              │                  │
              ▼                  ▼
        ┌───────────┐       ┌──────────────┐
        │   FAISS   │       │  Custom MCP  │
        │ Vector DB │       │    Server    │
        └───────────┘       │              │
                            │ Weather Tool │
                            │ Currency Tool│
                            └──────┬───────┘
                                   │
                                   ▼
                          External Current APIs
## 3. RAG Workflow
Public Travel Sources
        │
        ▼
Document Acquisition
        │
        ▼
Text Extraction / Cleaning
        │
        ▼
Document Chunking
        │
        ▼
Local Embeddings
(all-MiniLM-L6-v2)
        │
        ▼
FAISS Vector Store
        │
        ▼
Semantic Retrieval
        │
        ▼
Relevant Knowledge Chunks
        │
        ▼
Gemini LLM
        │
        ▼
Grounded Answer + Sources

The current knowledge base contains three Singapore travel resources.

4. Knowledge Base Sources

The application currently uses the following public travel resources:

Visit Singapore — Singapore Travel Guide
Visit Singapore — Travel Guide
Wikivoyage — Singapore Travel Guide

Source titles and URLs are maintained in:

knowledge_base/sources.md

The processed knowledge documents are stored under:

knowledge_base/documents/

The source acquisition logic is available in:

knowledge_base/fetch_sources.py
5. Embeddings and Vector Store

The application uses a local Hugging Face sentence-transformer model:

sentence-transformers/all-MiniLM-L6-v2

Local embeddings are used so that the retrieval pipeline does not require an external embedding API for every query.

FAISS is used as the vector store.

Generated vector store files:

knowledge_base/vector_store/
├── index.faiss
└── index.pkl

The current knowledge base contains approximately 429 document chunks.

6. MCP Architecture

The project implements its own MCP server instead of using a ready-to-use MCP server.

MCP server:

mcp_server/server.py

The application acts as an MCP client and invokes the tools exposed by this server.

MCP Tool 1 — Weather

Tool name:

get_weather

Purpose:

Retrieve current or future weather forecast information for Singapore.

Example inputs:

location = Singapore
forecast_days = 3

The weather information is obtained from Open-Meteo.

The application clearly identifies this information as:

MCP / Open-Meteo Weather Tool
MCP Tool 2 — Currency

Tool name:

convert_currency

Purpose:

Convert an amount between currencies using the current available exchange rate.

Example:

amount = 60000
from_currency = INR
to_currency = SGD

The currency information is obtained through Frankfurter.

The application identifies this as current information obtained through the MCP currency tool.

7. MCP Request Flow
User
 │
 ▼
Streamlit UI
 │
 ▼
Travel Agent
 │
 ▼
MCP Client
 │
 ▼
Custom MCP Server
 │
 ├── get_weather
 │
 └── convert_currency
 │
 ▼
External Current Information APIs
 │
 ▼
MCP Response
 │
 ▼
Gemini
 │
 ▼
Final Response
8. Tool Selection Strategy

The assistant uses different information sources depending on the user's request.

Knowledge Base Only

Example:

What are some family-friendly attractions in Singapore?

The application retrieves relevant destination information from the FAISS knowledge base.

Weather MCP

Example:

What is the weather forecast for Singapore for the next 3 days?

The application invokes the get_weather MCP tool.

Currency MCP

Example:

Convert INR 60,000 to SGD.

The application invokes the convert_currency MCP tool.

RAG + MCP

Example:

Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.

The application:

Retrieves destination information from the knowledge base.
Calls the weather MCP tool.
Combines the retrieved destination knowledge with the current weather information.
Produces a weather-aware itinerary.
Suggests indoor alternatives when weather conditions require changes.
9. Prompt and Context Strategy

The application follows these principles:

Use retrieved knowledge-base content for destination facts.
Use MCP tools for current or dynamic information.
Do not invent unsupported destination facts.
Clearly communicate when the knowledge base does not contain sufficient information.
Clearly identify information obtained from MCP tools.
Preserve relevant user preferences across multiple conversation turns.
Distinguish knowledge-base facts from AI-generated itinerary suggestions.
Include source references where applicable.
10. Conversation Context

The application supports multi-turn travel planning.

Example:

User
I am travelling with my wife and 5-year-old child.
Remember this preference.
User
Create a 3-day itinerary for us.

The assistant uses the previously provided family preference when generating the itinerary.

The user can then refine the plan without repeating the previous context.

Example:

Make Day 2 more indoor-focused.

This demonstrates conversation context and preference retention.

11. Handling Missing Information and Tool Failures

The assistant is designed not to fabricate destination information.

If a question asks for information that is not sufficiently represented in the knowledge base, the response indicates that the knowledge base does not contain enough information.

Similarly, if an MCP service becomes unavailable, the application reports the tool or service error rather than inventing current weather or exchange-rate information.

For unsupported weather locations, the weather MCP tool returns an explicit error because the current implementation is focused on Singapore travel planning.

12. Project Structure
ai_travel_planning_assistant/
│
├── app/
│   ├── agent.py
│   ├── mcp_client.py
│   ├── mcp_tools.py
│   ├── rag.py
│   ├── travel_agent.py
│   └── ui.py
│
├── knowledge_base/
│   ├── documents/
│   │   ├── visit_singapore_itineraries.md
│   │   ├── visit_singapore_travel_guide.md
│   │   └── wikivoyage_singapore.md
│   │
│   ├── vector_store/
│   │   ├── index.faiss
│   │   └── index.pkl
│   │
│   ├── build_vector_store.py
│   ├── fetch_sources.py
│   └── sources.md
│
├── mcp_server/
│   └── server.py
│
├── sample/
│   ├── test_future_weather.py
│   ├── test_gemini.py
│   ├── test_gemini_embeddings.py
│   ├── test_langchain_gemini.py
│   ├── test_mcp_client.py
│   └── test_rag_retrieval.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
13. Technology Stack
Component	Technology
UI	Streamlit
LLM	Google Gemini
LLM Framework	LangChain
RAG	LangChain + FAISS
Embeddings	Hugging Face Sentence Transformers
Vector Database	FAISS
MCP Server	Python MCP SDK
MCP Client	Python MCP SDK
Weather API	Open-Meteo
Currency API	Frankfurter
Programming Language	Python 3.11
14. Setup
Prerequisites

Install:

Python 3.11
Git
Internet connectivity
Google Gemini API key
Step 1 — Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ai_travel_planning_assistant
Step 2 — Create Virtual Environment
python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1
Step 3 — Install Dependencies
pip install -r requirements.txt
Step 4 — Configure Gemini API Key

Copy:

.env.example

to:

.env

Add:

GEMINI_API_KEY=your_gemini_api_key

Do not commit .env to Git.

15. Running the Application

From the project root:

python -m streamlit run app/ui.py

The Streamlit application will normally be available at:

http://localhost:8501
16. Rebuilding the Knowledge Base

The repository contains the source acquisition script:

knowledge_base/fetch_sources.py

To refresh the knowledge documents:

python knowledge_base/fetch_sources.py

Then rebuild the FAISS vector store:

python knowledge_base/build_vector_store.py

The generated vector store is saved under:

knowledge_base/vector_store/
17. Testing
Test Gemini
python sample/test_gemini.py
Test LangChain + Gemini
python sample/test_langchain_gemini.py
Test MCP Client
python sample/test_mcp_client.py
Test Future Weather
python sample/test_future_weather.py
Test RAG Retrieval
python sample/test_rag_retrieval.py
Test RAG Answer Generation
python -m app.rag
18. Sample Questions
RAG
What are some family-friendly attractions in Singapore?
What are some outdoor activities in Singapore?
What transportation options are available in Singapore?
Weather MCP
What is the weather forecast for Singapore for the next 3 days?
Currency MCP
My travel budget is INR 60,000. Convert it to SGD using the current exchange rate.
Combined RAG + MCP
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
Conversation Context
I am travelling with my wife and 5-year-old child. Remember this preference.

Followed by:

Create a 3-day itinerary for us.
19. Example End-to-End Scenario

User:

Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.

The application performs:

                         User Request
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
              RAG                      Weather MCP
                │                           │
                ▼                           ▼
       Singapore travel             Current forecast
          knowledge                  for travel dates
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                       Gemini Travel Planner
                              │
                              ▼
                   Weather-aware itinerary

The final response contains:

Day-by-day itinerary
Weather information
Weather-based adjustments
Indoor alternatives where appropriate
Knowledge-base source references
Explicit indication that current weather came from MCP
20. Demonstrated Assignment Scenarios

The application has been tested with the following scenarios:

Scenario 1 — RAG
What are some family-friendly attractions in Singapore?

The application retrieves relevant Singapore travel information from the FAISS knowledge base and provides source references.

Scenario 2 — Weather MCP
What is the weather forecast for Singapore for the next 3 days?

The application invokes the custom weather MCP tool and displays forecast information from the MCP response.

Scenario 3 — Currency MCP
My travel budget is INR 60,000. Convert it to SGD using the current exchange rate.

The application invokes the custom currency MCP tool and returns the current available exchange-rate result.

Scenario 4 — RAG + MCP
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.

The application combines destination knowledge retrieved through RAG with current weather obtained through MCP.

Scenario 5 — Multi-turn Context
I am travelling with my wife and 5-year-old child.

Followed by:

Create a 3-day itinerary for us.

The assistant retains the family preference while generating the itinerary.

21. Assignment Acceptance Criteria Coverage
Requirement	Implementation
At least 3 travel resources	3 Singapore travel resources
Semantic retrieval	FAISS + sentence-transformer embeddings
Grounded answers	RAG prompt restricts destination facts to retrieved context
Source references	Source title and URL metadata
Weather MCP	Custom get_weather tool
Currency MCP	Custom convert_currency tool
At least 2 MCP tools	Yes
RAG + MCP response	Weather-aware 3-day itinerary
Multi-turn context	User preferences retained
Appropriate tool selection	RAG / weather / currency / combined paths
Missing knowledge handling	Explicit insufficient-information response
MCP failure handling	Tool errors are returned instead of fabricated data
Simple UI	Streamlit
22. Design Principle

The core design principle is:

Stable / Destination Knowledge
            │
            ▼
       RAG Knowledge Base


Current / Dynamic Information
            │
            ▼
          MCP Tools

This separation allows the assistant to ground destination recommendations in curated travel knowledge while obtaining dynamic information such as weather and exchange rates at runtime.