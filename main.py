from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import function_calling

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")

@app.route("/")
def index():
    return "<h1>Hello World!</h1>"
if __name__ == '__main__':
    app.run(debug=True)


