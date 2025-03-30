from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import function_calling

app = Flask(__name__)
# load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
print(api_key)
base_url = "https://api.llama-api.com"
client = OpenAI(
api_key = api_key,
base_url = "https://api.llama-api.com"
)

@app.route("/", methods=["GET", "POST"])
def index():
    print("Works?")
    return "<h1>Hello World!</h1>"
