import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import datetime
import boto3
from botocore.exceptions import NoCredentialsError


# NEWSAPI CLASS

# NEWSAPI FACTORY


# 


load_dotenv()
api_key = os.getenv("NEWS_API")
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

class News:
    def get_news(self):
        raise NotImplementedError("Subclasses must implement get_news method.")

class APINews(News):
    def get_news(self):
        # Placeholder for API-based news fetching logic
        return "News from API source."

    def get_news_headlines(self, category):
        categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        if category not in categories:
            return "NOT A CATEGORY!"
        modified_url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={api_key}"
        response = requests.get(modified_url)
        result = []
        data = response.json()
        for i in range(len(data['articles'])):
            result.append(data["articles"][i]['title'])
        
        return str(result) + "\n\n**END OF LIST**\n\n"
        return str(result) + "\n\n**END OF LIST**\n\n"
    def get_news(self):
        # Placeholder for RSS-based news fetching logic
        return "News from RSS feed."

class LocalNews(News):
    def get_news(self):
        # Placeholder for local news fetching logic
        return "Local news."

class RSSNews(News):
    def get_news(self):
        # Placeholder for RSS-based news fetching logic
        return "News from RSS feed."

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
def save_news_to_s3(news_data, filename):
    """Save news articles to AWS S3 bucket using credentials from .env."""
    load_dotenv()
    aws_access_key_id = os.getenv("BUCKETEER_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("BUCKETEER_AWS_REGION")
    bucket_name = os.getenv("BUCKETEER_AWS_BUCKET_NAME")
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    try:
        s3.put_object(Bucket=bucket_name, Key=filename, Body=news_data)
        print(f"News data saved to S3 bucket {bucket_name} as {filename}")
    except NoCredentialsError:
        print("AWS credentials not found. News data not saved to S3.")
    except Exception as e:
        print(f"Error saving news data to S3: {e}")

# Example usage:
if __name__ == "__main__":
    current_time = datetime.datetime.now()
    print(current_time)
    api_news = APINews()
    headlines = api_news.get_news_headlines("general")
    # Save headlines to S3 bucket
    save_news_to_s3(headlines, f"news_headlines_{current_time.strftime('%Y%m%d_%H%M%S')}.txt")
