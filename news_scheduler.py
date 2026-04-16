"""
Scheduled news fetcher - Run this periodically to update S3 with fresh news.
Can be triggered by Heroku Scheduler or similar cron job service.
"""
import os
from dotenv import load_dotenv
import datetime
from news_generator import APINews, save_news_to_s3

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API")

def fetch_and_cache_news():
    """Fetch news from API and save to S3 for later retrieval."""
    try:
        api_news = APINews(NEWS_API_KEY)
        news = api_news.get_news()

        news_output = ""
        for i in range(news.get('totalResults', 0)):
            temp = api_news.get_news_readable(news, i)
            if temp == "":
                continue
            news_output += temp

        current_time = datetime.datetime.now()
        filename = f"news_headlines_{current_time.strftime('%Y%m%d_%H%M%S')}.txt"

        save_news_to_s3(news_output, filename)
        print(f"✓ Successfully cached news to S3: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error caching news: {e}")
        return False

if __name__ == "__main__":
    fetch_and_cache_news()
