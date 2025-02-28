import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv

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





if __name__ == "__main__":
    print(get_news_headlines("business"))
    print(get_news_headlines("entertainment"))
    print(get_news_headlines("general"))
    print(get_news_headlines("health"))
    print(get_news_headlines("science"))
    print(get_news_headlines("sports"))
    print(get_news_headlines("technology"))

    

