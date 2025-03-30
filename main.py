from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI, OpenAIError
import function_calling

app = Flask(__name__)
# load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
base_url = "https://api.llama-api.com"
try:
    client = OpenAI(
    api_key = api_key,
    base_url = "https://api.llama-api.com"
    )
except OpenAIError:
    @app.route("/", methods=["GET", "POST"])
    def index():
        return "<h1>Hello World!</h1>"
    ## run hello world webpage
    
