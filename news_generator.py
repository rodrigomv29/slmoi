import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import datetime


# NEWSAPI CLASS

# NEWSAPI FACTORY


# 


load_dotenv()
api_key = os.getenv("NEWS_API")
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

def get_news_headlines(category):
    categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
    if category not in categories:
        return "NOT A CATEGORY!"
    modified_url = url
    modified_url += f"&category={category}"
    response = requests.get(modified_url)
    result = []
    for i in range(len(response.json()['articles'])):
        result.append(response.json()["articles"][i]['title'])
    
    return str(result) + "\n\n**END OF LIST**\n\n"

class News:
    def get_news(self):
        raise NotImplementedError("Subclasses must implement get_news method.")

class APINews(News):
    def get_news(self):
        # Placeholder for API-based news fetching logic
        return "News from API source."

class RSSNews(News):
    def get_news(self):
        # Placeholder for RSS-based news fetching logic
        return "News from RSS feed."

class LocalNews(News):
    def get_news(self):
        # Placeholder for local news fetching logic
        return "Local news."

class NewsFactory:
    @staticmethod
    def create_news(source_type):
        if source_type == "api":
            return APINews()
        elif source_type == "rss":
            return RSSNews()
        elif source_type == "local":
            return LocalNews()
        else:
            raise ValueError(f"Unknown news source type: {source_type}")

if __name__ == "__main__":
    current_time = datetime.datetime.now()
    print(current_time)
    print(get_news_headlines("general"))
