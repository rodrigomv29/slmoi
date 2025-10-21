
from openai import OpenAI
from dotenv import load_dotenv
import os
from news_generator import APINews
import json

tools = [
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
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def news_function_call(key):
    input_list = [
    {"role": "user", "content": "What are the general news today?"}
    ]
    # 2. Prompt the model with tools defined
    client = OpenAI(
        api_key = api_key,
    )
    response = client.responses.create(
        model="gpt-4.1",
        tools=tools,
        input=input_list,
    )

    news = APINews(key)
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
        instructions="Answer prompt to summarize the output received by tool. Separate every headline into its own paragaph.If error is seen please display error message shown by the API",
        tools=tools,
        input=input_list,
    )
    return response.output_text
if __name__ == "__main__":

    print(news_function_call(api_key))