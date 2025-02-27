from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key = openai_api_key,
    base_url = "https://api.llama-api.com"
)

response = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "What are the news today?"}
    ],
    

)

print(response.model_dump_json(indent=2))
print(response.choices[0].message.content)