import requests
from langchain_core.tools import tool
from config import NEWS_API_KEY

URL = "https://api.worldnewsapi.com/search-news"


@tool
def get_news(limit: int = 5) -> str:
    """Fetch the latest English-language news articles from India.
    Use this tool when the user asks for Indian news headlines or updates.
    Args:
        limit: Number of headlines to return, between 1 and 10 (default 5).
    """
    limit = max(1, min(limit, 10))

    try:
        response = requests.get(
            URL,
            params={
                "api-key": NEWS_API_KEY,
                "source-countries": "in",
                "language": "en",
                "number": limit,
                "sort": "publish-time",
                "sort-direction": "DESC",
            },
            timeout=10,
        )
        response.raise_for_status()

        articles = response.json().get("news", [])

        headlines = [
            article["title"]
            for article in articles
            if article.get("title")
        ]

        if not headlines:
            return "Sorry, I couldn't find any news at the moment."

        return headlines

    except requests.exceptions.Timeout:
        return "The news service timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Unable to connect to the news service."

    except requests.exceptions.RequestException as e:
        return f"Failed to fetch news: {e}"
