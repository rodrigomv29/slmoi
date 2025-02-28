from flask import Flask, request, render_template, Response
from dotenv import load_dotenv
import os
import markdown
from openai import OpenAI
app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")
llama = OpenAI(
    api_key = api_key,
    base_url = "https://api.llama-api.com"
)
def generate_lorem_ipsum_text():
    # Generate lorem ipsum text
    lorem_ipsum_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    return lorem_ipsum_text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        # lorem = generate_lorem_ipsum_text()
        raw_output = get_llama_output(user_input)
        llama_output = markdown.markdown(raw_output)
        return render_template("index.html", user_input=user_input, llama_output=llama_output)
    return render_template("index.html")

def get_llama_output(user_input):
    completion = llama.chat.completions.create(
        model="llama3.1-70b",
         messages=[
        {"role": "developer", "content": "You are a helpful assistant that responds in less than 100 characters."},
        {
            "role": "user",
            "content": user_input
        }
    ]
    )
    return completion.choices[0].message.content


    
        
