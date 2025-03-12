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
        {"role": "user", "content": "Is Vladmir Putin on the news today?"}
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
                    "category": {
                        "type": "string",
                        "enum": [
                            "business",
                            "entertainment",
                            "general",
                            "health",
                            "science",
                            "sports",
                            "technology"
                        ]
                    },
                },
                "required": ["category"],
                "additionalProperties": False
            },
        "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather given a longitude and latitude",
            "parameters": {
                "type": "object",
                "properties": {
                    "longitude": {
                        "type": "float"
                    },
                    "latitude": {
                        "type": "float"
                    }
                ,
                }
                "required": ["longitude", "langitude"],
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


tool_call_str = completion.choices[0].message.tool_calls
if tool_call_str is None:
    print(completion.choices[0].message.content)
else:
    tool_call = json.loads(tool_call_str)
    # print(json.dumps(tool_call, indent=2))
    args = tool_call[0]['function']['arguments']
    arg_json = json.loads(args)
    result = news_generator.get_news_headlines(arg_json["category"])
    messages.append(completion.choices[0].message)

    messages.append({                               # append result message
        "role": "tool",
        "tool_call_id": tool_call[0]['id'],
        "content": str(result)
        })
    completion_2 = client.chat.completions.create(
        model="llama3.1-70b",
        messages=messages,
        tools=tools,
    )

    print(completion_2.choices[0])