from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import markdown
import sqlite3
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("LLAMA_API")
base_url = "https://api.llama-api.com"

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        user_name = request.form['user_name']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)",
                  (user_input, date, user_name))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    else:
        return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


