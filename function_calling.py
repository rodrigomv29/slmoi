from openai import OpenAI
from dotenv import load_dotenv
import os
from news_generator import APINews
import requests
import news_generator
import json
import wikipediaapi

NEWS_TOOLS = [
        {
            "type": "function",
            "name": "get_news_headlines",
            "description": "Get current news headlines given a news category",
            "parameters":{
                "type": "object",
                "properties": {
                    "category": {
                        "type":"string",
                        "enum": [
                            "business",
                            "entertainment",
                            "general",
                            "health",
                            "science",
                            "sports",
                            "technology"
                        ],
                        "description": "News category for the articles that are to be returned"

                    }
                },
                
                "required": ["category"],
                "additionalProperties": False
            },
            "strict": True
            

        }
]

WIKI_TOOLS = [
        {
            "type": "function",
            "name": "get_wikipedia_page",
            "description": "Get current new data given a news topic",
            "parameters":{
                "type": "object",
                "properties": {
                    "topic": {
                        "type":"string",
                        "description": "Subject for wikipedia page to be returned."

                    }
                },
                
                "required": ["topic"],
                "additionalProperties": False
            },
            "strict": True
            

        }
]
WEATHER_TOOLS = [
        {
            "type": "function",
            "name": "get_weather_data",
            "description": "Get current weather data given longitude and latitude coordinates",
            "parameters":{
                "type": "object",
                "properties": {
                    "latitude": {
                        "type":"string",
                        "description": "Latitude coordinates of location"

                    },
                    "longitude":{
                        "type": "string",
                        "description":"Longitude coordinates of location"
                    }

                },
                
                "required": ["latitude", "latitude"],
                "additionalProperties": False
            },
            "strict": True
            

        }
]
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
def news_function_call(user_prompt):
    input_list = [
    {"role": "user", "content":user_prompt}
    ]
    # 2. Prompt the model with tools defined
    client = OpenAI(
        api_key = OPENAI_API_KEY,
    )
    response = client.responses.create(
        model="gpt-4.1",
        tools=NEWS_TOOLS,
        input=input_list,
    )
    news = APINews(NEWS_API_KEY)
    input_list+=response.output
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_news_headlines":
                argument_dict = json.loads(item.arguments)
                headlines = news.get_news_headlines(argument_dict['category'])
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "headlines": headlines
                    })
                })
    response = client.responses.create(
        model="gpt-5",
        instructions="Answer prompt to summarize the output received by tool. Separate every headline into its own paragaph.If error is seen please display error message shown by the API. If prompt does not ask for news related task then print an error message for that.",
        tools=NEWS_TOOLS,
        input=input_list,
    )
    return response.output_text
def get_wikipedia_page(topic):
    USER_AGENT = os.getenv("USER_AGENT")
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language='en')
    page_py = wiki_wiki.page(topic)
    return page_py.text
def wikipedia_function_call(prompt):
    input_list = [
    {"role": "user", "content": prompt}
    ]
    # 2. Prompt the model with tools defined
    client = OpenAI(
        api_key = OPENAI_API_KEY,
    )
    response = client.responses.create(
        model="gpt-4.1",
        tools=WIKI_TOOLS,
        input=input_list,
    )
    input_list+=response.output
    #print(response.output)
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_wikipedia_page":
                argument_dict = json.loads(item.arguments)
                wiki_page = get_wikipedia_page(argument_dict['topic'])
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "page": wiki_page
                    })
                })
        else:
            return "LLM is responding without wikipedia"
    response = client.responses.create(
        model="gpt-4.1",
        instructions="Answer prompt using wikipedia tool. If error is seen please display error message shown by the wikipedia api. If successfully retrieved wikipedia information then cite the page you used to retrieve the information.",
        tools=WIKI_TOOLS,
        input=input_list,
    )
    return response.output_text
def get_weather_data(lat, lon):
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=imperial")
    return res.json()

def weather_function_call():
    return "weather function call"
if __name__ == "__main__":
    print(wikipedia_function_call("Can you pass me the ketchup?"))
    #print(wikipedia_function_call("Linear Algebra"))
    #print(news_function_call("Can you pass the salt?"))
    #print(get_weather_data(40.758896, -73.985130))