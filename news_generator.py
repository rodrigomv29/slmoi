import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import socket


# NEWSAPI CLASS

# NEWSAPI FACTORY


# 


load_dotenv()
api_key = os.getenv("NEWS_API")
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
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
            f = get_most_recent_news()
            backup = show_contents_of_file(f)
            return data
        return "\n\n**START OF LIST**\n\n" + str(result) + "\n\n**END OF LIST**\n\n"
    def get_news_readable(self, news, i):
        try:
            news_source = news['articles'][i]['source']
            news_title = news['articles'][i]['title']
            news_url = news['articles'][i]['url']
        except IndexError:
            return ""
        return f"{news_title}\n{news_source}\n{news_url}\n"

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
def get_most_recent_news():
    s3=initialize_boto_client()
    bucket_name = os.getenv("BUCKETEER_BUCKET_NAME")
    response = s3.list_objects_v2(Bucket=bucket_name)
    if "Contents" in response:
        sorted_objects = sorted(response["Contents"], key=lambda obj: obj["LastModified"], reverse=True)
        most_recent_file_key = sorted_objects[0]["Key"]
        return most_recent_file_key
    return None
def show_contents_of_file(filename):
    s3 = boto3.client('s3')
    bucket_name = os.getenv("BUCKETEER_BUCKET_NAME")
    try:
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        return f"Error retrieving file: {e}"

# Example usage:
if __name__ == "__main__":


    current_time = datetime.datetime.now()
    print(current_time)
    
    file_key = get_most_recent_news()
    print("CONTENTS OF FILE:\n\n\n")
    print(show_contents_of_file(file_key))
    

    """
    api_news = APINews(api_key)
    news = api_news.get_news()
    news_output = ""
    for i in range(news['totalResults']):
        temp = api_news.get_news_readable(news, i)
        if temp == "":
            continue
        news_output += api_news.get_news_readable(news, i)
    print(news_output)
    save_news_to_s3(news_output, f"news_headlines_{current_time.strftime('%Y%m%d_%H%M%S')}.txt")
    
"""