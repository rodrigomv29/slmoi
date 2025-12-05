import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import socket


load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API")
def initialize_boto_client():
    load_dotenv()
    aws_access_key_id = os.getenv("BUCKETEER_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("BUCKETEER_AWS_REGION")
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    return s3


class News:
    def __init__(self, source, title, url):
        self.source=source
        self.title=title
        self.url=url
    def __str__(self):
        return f"{self.title}\n{self.source}\n{self.url}\n"
    def get_source(self):
        return self.source
    def get_title(self):
        return self.title
    def get_url(self):
        return self.url
    def set_source(self, s):
        self.source=s
    def set_title(self, t):
        self.title = t
    def set_url(self, u):
        self.url = u
    def get_news(self):
        raise NotImplementedError("Subclasses must implement get_news method.")

class APINews(News):
    def __init__(self, api_key):
        self.api_key =api_key
    def get_news(self):
        # Placeholder for API-based news fetching logic
        categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        category="general"
        modified_url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={self.api_key}"
        response = requests.get(modified_url)
        # data = response.json()
        return response.json()
    def get_news_headlines(self, category):
        categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        if category not in categories:
            return "NOT A CATEGORY!"
        modified_url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={self.api_key}"
        response = requests.get(modified_url)
        result = []
        data = response.json()
        if not isinstance(data, dict):
            return "News Object not available"
        try:
            for i in range(len(data['articles'])):
                result.append(data['articles'][i]['title'])
        except KeyError:
            aws_client = initialize_boto_client()
            f = get_most_recent_news(aws_client)
            backup = show_contents_of_file(aws_client, f)
            return backup
        return "\n\n**START OF LIST**\n\n" + str(result) + "\n\n**END OF LIST**\n\n"
    def get_news_readable(self, news, i):
        try:
            news_source = news['articles'][i]['source']
            news_title = news['articles'][i]['title']
            news_url = news['articles'][i]['url']
            news_obj = News(news_source, news_title, news_url) 
        except IndexError:
            return ""
        return f"{news_obj.title}\n{news_obj.source}\n{news_obj.url}\n"

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
    bucket_name = os.getenv("BUCKETEER_BUCKET_NAME")
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
def get_most_recent_news(client):
    bucket_name = os.getenv("BUCKETEER_BUCKET_NAME")
    response = client.list_objects_v2(Bucket=bucket_name)
    if "Contents" in response:
        sorted_objects = sorted(response["Contents"], key=lambda obj: obj["LastModified"], reverse=True)
        most_recent_file_key = sorted_objects[0]["Key"]
        return most_recent_file_key
    return None
def show_contents_of_file(client, filename):
    bucket_name = os.getenv("BUCKETEER_BUCKET_NAME")
    try:
        response = client.get_object(Bucket=bucket_name, Key=filename)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        return f"Error retrieving file: {e}"

if __name__ == "__main__":


    current_time = datetime.datetime.now()
    print(current_time)
    api_news = APINews(NEWS_API_KEY)
    news = api_news.get_news()
    news_output = ""
    for i in range(news['totalResults']):
        temp = api_news.get_news_readable(news, i)
        if temp == "":
            continue
        news_output += api_news.get_news_readable(news, i)
    print("START OF FILE:")
    print(news_output)
    print("END OF FILE")
    save_news_to_s3(news_output, f"news_headlines_{current_time.strftime('%Y%m%d_%H%M%S')}.txt")