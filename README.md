# AI Travel Planning Assistant

## GitHub Repository

Source code and complete project history:

https://github.com/bhaveshkulkarni4-ops/ai-travel-planning-assistant

# AI Travel Planning Assistant

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
                          
```
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
```

The current knowledge base contains three Singapore travel resources.

---

## 4. Knowledge Base Sources

The application currently uses the following public travel resources:

1. **Visit Singapore — Singapore Travel Guide**
2. **Visit Singapore — Travel Guide**
3. **Wikivoyage — Singapore Travel Guide**

Source titles and URLs are maintained in:

```text
knowledge_base/sources.md
```

The processed knowledge documents are stored under:

```text
knowledge_base/documents/
```

The source acquisition logic is available in:

```text
knowledge_base/fetch_sources.py
```

### Source Resources

The current sources include:

- Visit Singapore travel guide resources
- Wikivoyage Singapore Travel Guide

The complete source titles and original URLs are maintained in:

```text
knowledge_base/sources.md
```

---

## 5. Embeddings and Vector Store

The application uses a local Hugging Face sentence-transformer model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Local embeddings are used so that the retrieval pipeline does not require an external embedding API for every query.

FAISS is used as the vector store.

Generated vector store files:

```text
knowledge_base/vector_store/
├── index.faiss
└── index.pkl
```

The current knowledge base contains approximately 429 document chunks.

---

## 6. MCP Architecture

The project implements its **own custom MCP server and MCP client** instead of using a ready-to-use MCP server.

MCP server:

```text
mcp_server/server.py
```

The application acts as an MCP client and invokes the tools exposed by this custom server.

The MCP server exposes two custom tools:

- `get_weather`
- `convert_currency`

The application connects to this server through its own MCP client implementation.

### MCP Tool 1 — Weather

Tool name:

```text
get_weather
```

Purpose:

Retrieve current or future weather forecast information for Singapore.

Example inputs:

```text
location = Singapore
forecast_days = 3
```

The weather information is obtained from Open-Meteo.

The application clearly identifies this information as:

```text
MCP / Open-Meteo Weather Tool
```

### MCP Tool 2 — Currency

Tool name:

```text
convert_currency
```

Purpose:

Convert an amount between currencies using the current available exchange rate.

Example:

```text
amount = 60000
from_currency = INR
to_currency = SGD
```

The currency information is obtained through Frankfurter.

The application identifies this as current information obtained through the MCP currency tool.

---

## 7. MCP Request Flow

```text
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
```

---

## 8. Tool Selection Strategy

The assistant uses different information sources depending on the user's request.

### Knowledge Base Only

Example:

```text
What are some family-friendly attractions in Singapore?
```

The application retrieves relevant destination information from the FAISS knowledge base.

### Weather MCP

Example:

```text
What is the weather forecast for Singapore for the next 3 days?
```

The application invokes the `get_weather` MCP tool.

### Currency MCP

Example:

```text
Convert INR 60,000 to SGD.
```

The application invokes the `convert_currency` MCP tool.

### RAG + MCP

Example:

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

The application:

1. Retrieves destination information from the knowledge base.
2. Calls the weather MCP tool.
3. Combines the retrieved destination knowledge with the current weather information.
4. Produces a weather-aware itinerary.
5. Suggests indoor alternatives when weather conditions require changes.

---

## 9. Prompt and Context Strategy

The application follows these principles:

- Use retrieved knowledge-base content for destination facts.
- Use MCP tools for current or dynamic information.
- Do not invent unsupported destination facts.
- Clearly communicate when the knowledge base does not contain sufficient information.
- Clearly identify information obtained from MCP tools.
- Preserve relevant user preferences across multiple conversation turns.
- Distinguish knowledge-base facts from AI-generated itinerary suggestions.
- Include source references where applicable.

### Facts vs Suggestions

The application distinguishes between different types of information:

- **Knowledge-base facts:** Destination information is grounded in retrieved travel-source content and accompanied by source references where applicable.
- **Current information:** Weather and exchange-rate information are obtained at runtime through MCP tools and are identified as MCP-derived information.
- **AI suggestions:** Itinerary sequencing, activity combinations, and weather-based alternatives are generated suggestions based on retrieved information and user preferences.

---

## 10. Conversation Context

The application supports multi-turn travel planning.

Example:

```text
User:
I am travelling with my wife and 5-year-old child.
Remember this preference.

User:
Create a 3-day itinerary for us.
```

The assistant uses the previously provided family preference when generating the itinerary.

The user can then refine the plan without repeating the previous context.

Example:

```text
Make Day 2 more indoor-focused.
```

This demonstrates conversation context and preference retention.

---

## 11. Handling Missing Information and Tool Failures

The assistant is designed not to fabricate destination information.

If a question asks for information that is not sufficiently represented in the knowledge base, the response indicates that the knowledge base does not contain enough information.

Similarly, if an MCP service becomes unavailable, the application reports the tool or service error rather than inventing current weather or exchange-rate information.

For unsupported weather locations, the weather MCP tool returns an explicit error because the current implementation is focused on Singapore travel planning.

---

## 12. Project Structure

```text
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
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 13. Technology Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini |
| LLM Framework | LangChain |
| RAG | LangChain + FAISS |
| Embeddings | Hugging Face Sentence Transformers |
| Vector Database | FAISS |
| MCP Server | Python MCP SDK |
| MCP Client | Python MCP SDK |
| Weather API | Open-Meteo |
| Currency API | Frankfurter |
| Programming Language | Python 3.11 |

---

## 14. Setup

### Prerequisites

Install:

- Python 3.11
- Git
- Internet connectivity
- Google Gemini API key

### Step 1 — Clone the Repository

```powershell
git clone https://github.com/bhaveshkulkarnI4-ops/ai-travel-planning-assistant.git
cd ai-travel-planning-assistant
```

### Step 2 — Create Virtual Environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Configure Gemini API Key

Copy:

```text
.env.example
```

to:

```text
.env
```

Add:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` to Git.

The `.gitignore` file excludes `.env` and the local `.venv` directory from source control.

---

## 15. Development Mode and Running the Application

The application can be run locally in development mode using Streamlit.

From the project root:

```powershell
.venv\Scripts\Activate.ps1
python -m streamlit run app/ui.py
```

The Streamlit application will normally be available at:

```text
http://localhost:8501
```

The MCP server is started by the application through the MCP client when MCP tools are required.

No ready-to-use external MCP server is required.

The custom MCP server implementation is available in:

```text
mcp_server/server.py
```

---

## 16. Rebuilding the Knowledge Base

The repository contains the source acquisition script:

```text
knowledge_base/fetch_sources.py
```

To refresh the knowledge documents:

```powershell
python knowledge_base/fetch_sources.py
```

Then rebuild the FAISS vector store:

```powershell
python knowledge_base/build_vector_store.py
```

The generated vector store is saved under:

```text
knowledge_base/vector_store/
```

---

## 17. Testing

### Test Gemini

```powershell
python sample/test_gemini.py
```

### Test LangChain + Gemini

```powershell
python sample/test_langchain_gemini.py
```

### Test MCP Client

```powershell
python sample/test_mcp_client.py
```

### Test Future Weather

```powershell
python sample/test_future_weather.py
```

### Test RAG Retrieval

```powershell
python sample/test_rag_retrieval.py
```

### Test RAG Answer Generation

```powershell
python -m app.rag
```

The RAG answer-generation test requires a valid Gemini API key and available Gemini API quota.

---

## 18. Sample Questions

### RAG

```text
What are some family-friendly attractions in Singapore?
```

```text
What are some outdoor activities in Singapore?
```

```text
What transportation options are available in Singapore?
```

### Weather MCP

```text
What is the weather forecast for Singapore for the next 3 days?
```

### Currency MCP

```text
My travel budget is INR 60,000. Convert it to SGD using the current exchange rate.
```

### Combined RAG + MCP

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

### Conversation Context

```text
I am travelling with my wife and 5-year-old child. Remember this preference.
```

Followed by:

```text
Create a 3-day itinerary for us.
```

---

## 19. Example End-to-End Scenario

User:

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

The application performs:

```text
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
```

The final response contains:

- Day-by-day itinerary
- Weather information
- Weather-based adjustments
- Indoor alternatives where appropriate
- Knowledge-base source references
- Explicit indication that current weather came from MCP

---

## 20. Demonstrated Assignment Scenarios

### Scenario 1 — RAG

Question:

```text
What are some family-friendly attractions in Singapore?
```

The application retrieves relevant Singapore travel information from the FAISS knowledge base and provides source references.

### Scenario 2 — Weather MCP

Question:

```text
What is the weather forecast for Singapore for the next 3 days?
```

The application invokes the custom weather MCP tool and displays forecast information from the MCP response.

### Scenario 3 — Currency MCP

Question:

```text
My travel budget is INR 60,000. Convert it to SGD using the current exchange rate.
```

The application invokes the custom currency MCP tool and returns the current available exchange-rate result.

### Scenario 4 — RAG + MCP

Question:

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

The application combines destination knowledge retrieved through RAG with current weather obtained through MCP.

### Scenario 5 — Multi-turn Context

First message:

```text
I am travelling with my wife and 5-year-old child.
```

Followed by:

```text
Create a 3-day itinerary for us.
```

The assistant retains the family preference while generating the itinerary.

---

## 21. Assignment Acceptance Criteria Coverage

| Requirement | Implementation |
|---|---|
| At least 3 travel resources | 3 Singapore travel resources |
| Semantic retrieval | FAISS + sentence-transformer embeddings |
| Grounded answers | RAG prompt restricts destination facts to retrieved context |
| Source references | Source title and URL metadata |
| Weather MCP | Custom `get_weather` tool |
| Currency MCP | Custom `convert_currency` tool |
| At least 2 MCP tools | Yes |
| RAG + MCP response | Weather-aware 3-day itinerary |
| Multi-turn context | User preferences retained |
| Appropriate tool selection | RAG / weather / currency / combined paths |
| Missing knowledge handling | Explicit insufficient-information response |
| MCP failure handling | Tool errors are returned instead of fabricated data |
| Simple UI | Streamlit |
| Custom MCP server and client | Implemented in the project |

---

## 22. Design Principle

The core design principle is:

```text
Stable / Destination Knowledge
            │
            ▼
       RAG Knowledge Base


Current / Dynamic Information
            │
            ▼
          MCP Tools
```

This separation allows the assistant to ground destination recommendations in curated travel knowledge while obtaining dynamic information such as weather and exchange rates at runtime.

---

## 23. Demo

A short demonstration of the application covers:

1. RAG-based Singapore travel question with source references
2. Current weather retrieval through the custom Weather MCP tool
3. Currency conversion through the custom Currency MCP tool
4. Combined RAG + MCP weather-aware itinerary generation
5. Multi-turn conversation context using family travel preferences
6. Handling of unsupported knowledge or unavailable MCP information without fabrication

### Demo Video

Demo link:

```text
<DEMO_VIDEO_LINK>
```

The demo is intentionally kept short and focuses on the key assignment scenarios.

---

## 24. Key Takeaways

The application demonstrates how RAG and MCP can be combined in a practical AI application:

- **RAG** provides grounded destination knowledge.
- **FAISS** enables semantic retrieval over the travel knowledge base.
- **Local embeddings** provide an efficient retrieval pipeline without requiring an embedding API for every query.
- **Custom MCP tools** provide access to current external information.
- **Weather MCP** provides current/future weather information.
- **Currency MCP** provides current available exchange-rate information.
- **Conversation context** allows the assistant to retain user preferences across turns.
- **Tool selection** ensures that stable knowledge and dynamic information are handled through the appropriate information path.
- **Failure handling** prevents the application from fabricating unsupported information.
- **Streamlit** provides a simple user interface for the complete solution.

The overall design separates:

```text
Knowledge → RAG
Current Information → MCP
User Preferences → Conversation Context
```

and combines these components through a LangChain-based travel planning assistant.