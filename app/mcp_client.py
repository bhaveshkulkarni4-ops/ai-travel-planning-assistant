import asyncio

from mcp import Client, StdioServerParameters


SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["mcp_server/server.py"],
)


async def list_mcp_tools():
    async with Client(SERVER_PARAMS) as client:
        result = await client.list_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in result.tools
        ]


async def call_mcp_tool(tool_name: str, arguments: dict):
    async with Client(SERVER_PARAMS) as client:
        result = await client.call_tool(
            tool_name,
            arguments,
        )

        return result


if __name__ == "__main__":
    result = asyncio.run(
        call_mcp_tool(
            "convert_currency",
            {
                "amount": 60000,
                "from_currency": "INR",
                "to_currency": "SGD",
            },
        )
    )

    print("MCP TOOL CALL RESULT:")
    print(result)