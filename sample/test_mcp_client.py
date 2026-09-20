import asyncio

from mcp import Client, StdioServerParameters


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"],
    )

    async with Client(server_params) as client:

        result = await client.call_tool(
            "convert_currency",
            {
                "amount": 60000,
                "from_currency": "INR",
                "to_currency": "SGD",
            },
        )

        print("\nCURRENCY TOOL RESULT")
        print("====================")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())