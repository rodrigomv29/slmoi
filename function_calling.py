from openai import OpenAI
from dotenv import load_dotenv
import os
import news_generator
import json
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key = openai_api_key,
    base_url = "https://api.llama-api.com"
)
messages=[
        {"role": "user", "content": "What are the sports news today?"}
]
model="llama3.1-70b"
tools = [{
        "type": "function",
        "function": {
            "name": "get_news_headlines",
            "description": "Get current news headlines given a news category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                },
                "required": ["category"],
                "additionalProperties": False
        },
        "strict": True
        }
    }
]
completion = client.chat.completions.create(
    model="llama3.1-70b",
    messages=messages,
    tools=tools,
)


tool_call = completion.choices[0].message.tool_calls
json_list = json.loads(tool_call)
args = json_list[0]['function']['arguments']
arg_json = json.loads(args)
result = news_generator.get_news_headlines(arg_json["category"])
print(result)