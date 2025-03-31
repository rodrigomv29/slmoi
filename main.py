from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import function_calling

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = "https://api.llama-api.com"
client = OpenAI(
api_key = api_key,
base_url = "https://api.llama-api.com"
)

def init_db():
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_inputs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  input_text TEXT NOT NULL,
                  date TEXT NOT NULL,
                  user_name TEXT DEFAULT 'guest')''')
    conn.commit()
    conn.close()

def get_llama_output(inp, fun_call):
    if fun_call == 1:
        response = client.chat.completions.create(
        model="llama3.1-70b",
        messages=[
            {"role": "system", "content": "You are a programming assistant that doesn't fully answer questions but recommends computer science textbooks to read for a deeper understanding"},
            {"role": "user", "content": inp}
        ],
    )
        return response.choices[0].message.content
    elif fun_call==2:
        # refer to function_calling.py
        pass
    elif fun_call==3:
        # refer to function_calling.py
        pass


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        user_name = request.form.get('user_name')
        if request.form.get("Weather"):
            print("WEATHER!!")
        if request.form.get("News"):
            print("NEWS!!")
        llama_output = get_llama_output(user_input, fun_call=1 )
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('prompts.db')
        c = conn.cursor()
        c.execute("""INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)""",
                  (user_input, date, user_name))
        conn.commit()
        conn.close()

        return render_template('index.html', user_input=user_input, llama_output=llama_output)
    else:
        conn = sqlite3.connect('prompts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user_inputs")
        rows = c.fetchall()
        conn.close()
        return render_template('index.html', rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


