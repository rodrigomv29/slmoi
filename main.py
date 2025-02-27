from flask import Flask, request, render_template, Response
from dotenv import load_dotenv
import os
import markdown
from llamaapi import LlamaAPI

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")
llama = LlamaAPI(api_key)

def generate_lorem_ipsum_text():
    # Generate lorem ipsum text
    lorem_ipsum_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    return lorem_ipsum_text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        raw_output = get_llama_output(user_input)
        llama_output = markdown.markdown(raw_output)
        return render_template("index.html", user_input=user_input, llama_output=llama_output)
    return render_template("index.html")

def get_llama_output(user_input):
    api_request_json = {
        "model": "llama3.1-70b",
        "messages": [
            {"role": "user", "content": user_input},
        ]
    }
    # Execute the Request
    response = llama.run(api_request_json)
    # print(json.dumps(response.json(), indent=2))
    # return "None"
    return response.json()["choices"][0]["message"]["content"]
def stream_llama_output(user_input):
    raw_output = get_llama_output(user_input)
    markdown_output = markdown.markdown(raw_output)
    yield markdown_output

    
        
