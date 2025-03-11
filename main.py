from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")
base_url = "https://api.llama-api.com"
client = OpenAI(
api_key = api_key,
base_url = "https://api.llama-api.com"
)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_inputs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  input_text TEXT NOT NULL,
                  date TEXT NOT NULL,
                  user_name TEXT DEFAULT 'guest')''')
    conn.commit()
    conn.close()

def get_llama_output(inp):
    response = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[
        {"role": "system", "content": "You are an assist that will politely reject any questions related to hip hop music trivia with the text \"PASS!\" "},
        {"role": "user", "content": inp}
    ],
)
    return response.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        llama_output = get_llama_output(user_input)
        user_name = request.form['user_name']

        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('prompts.db')
        c = conn.cursor()
        c.execute("INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)",
                  (user _input, date, user_name))
        conn.commit()
        conn.close()"
        """

        return render_template('index.html', user_input=user_input, llama_output=llama_output)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


