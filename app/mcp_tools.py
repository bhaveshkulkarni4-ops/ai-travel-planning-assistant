from langchain_core.tools import tool

from app.mcp_client import call_mcp_tool


def _extract_text(result) -> str:
    """Extract text returned by the MCP server."""

    if hasattr(result, "content"):
        for item in result.content:
            if getattr(item, "type", None) == "text":
                return item.text

    return str(result)


@tool
async def get_weather(
    location: str = "Singapore",
    forecast_days: int = 3,
    start_date: str | None = None,
) -> str:
    """
    Get the weather forecast for Singapore.

    Use this tool when the user asks about current or upcoming
    weather conditions or when an itinerary needs to be adjusted
    according to the weather forecast.

    If the user specifies a future travel date, provide that date
    using start_date in YYYY-MM-DD format.
    """

    arguments = {
    "location": location,
    "forecast_days": forecast_days,
}

    if start_date:
        arguments["start_date"] = start_date

    result = await call_mcp_tool(
        "get_weather",
        arguments,
    )

    return _extract_text(result)


@tool
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """
    Convert an amount between currencies using the current
    available exchange rate.

    Use this tool when the user asks for a currency conversion
    or provides a travel budget in another currency.
    """

    result = await call_mcp_tool(
        "convert_currency",
        {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
        },
    )

    return _extract_text(result)


MCP_TOOLS = [
    get_weather,
    convert_currency,
]


if __name__ == "__main__":
    print("LangChain MCP tools:")
    for tool_item in MCP_TOOLS:
        print(f"- {tool_item.name}")
        print(f"  {tool_item.description}")
