import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NEWS_API")
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

def get_news_headlines():
    response = requests.get(url)
    for i in range(len(response.json()['articles'])):
        print(response.json()["articles"][i]['title'])