import os
import asyncio

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.mcp_tools import MCP_TOOLS


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    max_retries=0,
)

llm_with_tools = llm.bind_tools(MCP_TOOLS)


async def run_agent(question: str):

    response = await llm_with_tools.ainvoke(question)

    print("MODEL TOOL CALL:")
    print(response.tool_calls)

    if not response.tool_calls:
        print("\nFINAL ANSWER:")
        print(response.content)
        return

    tool_messages = []

    for tool_call in response.tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"\nEXECUTING TOOL: {tool_name}")
        print(f"ARGUMENTS: {tool_args}")

        for tool_item in MCP_TOOLS:

            if tool_item.name == tool_name:

                tool_result = await tool_item.ainvoke(tool_args)

                print("\nMCP TOOL RESULT:")
                print(tool_result)

                tool_messages.append(
                    {
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call["id"],
                    }
                )

    final_response = await llm_with_tools.ainvoke(
        [
            {
                "role": "user",
                "content": question,
            },
            response,
            *tool_messages,
        ]
    )

    print("\nFINAL ANSWER:")

    answer = final_response.content

    if isinstance(answer, list):
        text_parts = []

        for item in answer:
            if isinstance(item, dict) and item.get("text"):
                text_parts.append(item["text"])

        answer = "\n".join(text_parts)

    print(answer)


if __name__ == "__main__":

    asyncio.run(
        run_agent(
            "What will the weather be like in Singapore over the next 3 days?"
        )
    )