from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

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

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    user_name = request.form['user_name']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)",
              (user_input, date, user_name))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)