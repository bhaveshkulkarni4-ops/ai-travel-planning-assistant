import asyncio

from app.mcp_client import call_mcp_tool


async def main():
    result = await call_mcp_tool(
        "get_weather",
        {
            "location": "Singapore",
            "forecast_days": 3,
            "start_date": "2026-09-27",
        },
    )

    print("FUTURE WEATHER RESULT:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())