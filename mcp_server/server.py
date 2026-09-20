from datetime import date, timedelta
from datetime import date, timedelta

import httpx

from mcp.server.mcpserver import MCPServer


server = MCPServer(
    name="Singapore Travel Tools"
)


SINGAPORE_COORDINATES = {
    "latitude": 1.3521,
    "longitude": 103.8198,
}


@server.tool()
def get_weather(
    location: str = "Singapore",
    forecast_days: int = 3,
    start_date: str | None = None,
) -> dict:
    """
    Get the current weather forecast for Singapore.

    Returns daily temperature, precipitation probability,
    rainfall and weather-code information from Open-Meteo.
    """

    if location.strip().lower() != "singapore":
        return {
            "status": "error",
            "message": "This travel assistant currently supports weather for Singapore only.",
        }

    if forecast_days < 1 or forecast_days > 16:
        return {
            "status": "error",
            "message": "forecast_days must be between 1 and 16.",
        }

    latitude = SINGAPORE_COORDINATES["latitude"]
    longitude = SINGAPORE_COORDINATES["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
    "latitude": latitude,
    "longitude": longitude,
    "daily": (
        "weather_code,"
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_probability_max,"
        "rain_sum"
    ),
    "timezone": "Asia/Singapore",
}

    if start_date:
        try:
            start = date.fromisoformat(start_date)
        except ValueError:
            return {
                "status": "error",
                "message": "start_date must use YYYY-MM-DD format.",
            }

        end = start + timedelta(days=forecast_days - 1)

        params["start_date"] = start.isoformat()
        params["end_date"] = end.isoformat()
    else:
        params["forecast_days"] = forecast_days

    try:
        response = httpx.get(
            url,
            params=params,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "status": "success",
            "source": "Open-Meteo",
            "source_url": "https://open-meteo.com/",
            "location": "Singapore",
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "daily": data.get("daily", {}),
        }

    except httpx.HTTPError as exc:
        return {
            "status": "error",
            "message": f"Weather service is currently unavailable: {exc}",
        }
@server.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:
    """
    Convert an amount from one currency to another using
    the latest available Frankfurter exchange rate.
    """

    if amount < 0:
        return {
            "status": "error",
            "message": "Amount must be zero or greater.",
        }

    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    if len(from_currency) != 3 or len(to_currency) != 3:
        return {
            "status": "error",
            "message": "Currency codes must be 3-letter ISO codes, such as INR or SGD.",
        }

    if from_currency == to_currency:
        return {
            "status": "success",
            "source": "Frankfurter",
            "source_url": "https://frankfurter.dev/",
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0,
            "converted_amount": amount,
        }

    url = (
        f"https://api.frankfurter.dev/v2/rate/"
        f"{from_currency.lower()}/{to_currency.lower()}"
    )

    try:
        response = httpx.get(
            url,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        rate = float(data["rate"])
        converted_amount = round(amount * rate, 2)

        return {
            "status": "success",
            "source": "Frankfurter",
            "source_url": "https://frankfurter.dev/",
            "date": data.get("date"),
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "converted_amount": converted_amount,
        }

    except httpx.HTTPError as exc:
        return {
            "status": "error",
            "message": (
                f"Currency conversion service is currently unavailable: {exc}"
            ),
        }

    except (KeyError, TypeError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Invalid currency response received: {exc}",
        }

if __name__ == "__main__":
    server.run()