import os
import requests

from dotenv import load_dotenv
from config import NEWS_API_KEY

URL = (
    f"https://api.worldnewsapi.com/search-news"
    f"?api-key={NEWS_API_KEY}"
    f"&source-countries=in"
    f"&language=en"
)

def get_news(limit=5):
    """Fetch the latest Indian news headlines."""

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("news", [])

        if not articles:
            return ["Sorry, I couldn't find any news at the moment."]

        headlines = [
            article["title"]
            for article in articles[:limit]
            if article.get("title")
        ]
        return headlines

    except requests.exceptions.Timeout:
        return ["The news service is taking too long to respond."]

    except requests.exceptions.ConnectionError:
        return ["Unable to connect to the internet."]

    except requests.exceptions.RequestException:
        return ["Something went wrong while fetching the news."]