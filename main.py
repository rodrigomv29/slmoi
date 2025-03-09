from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import markdown
from openai import OpenAI
app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")
base_url = "https://api.llama-api.com"

"""
OPENAI.openai error
"""
def generate_lorem_ipsum_text():
    # Generate lorem ipsum text
    lorem_ipsum_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    return lorem_ipsum_text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        lorem_ipsum_text = generate_lorem_ipsum_text()
        return render_template("index.html", user_input=user_input, lorem_ipsum_text=lorem_ipsum_text)
    else:
        return redirect(url_for('index'))

        
