from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import openai
import function_calling

# Initializing Flask App
app = Flask(__name__)
# Configuring OpenAI app using environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = "https://api.apillm.com"
client = OpenAI(
api_key = api_key,
base_url = base_url
)
app.secret_key = os.getenv("SECRET_KEY")
def init_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "prompts.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_inputs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_name TEXT DEFAULT 'guest')''')
        conn.commit()

#TODO DEFINE A FUNCTION WHERE USER CAN CUSTOMIZE 
def get_openai_version():
    return openai.__version__

#TODO GET CHAT COMPLETIONS INFO

def get_chat_completions_info(client):
    if isinstance(client, openai.types.chat.chat_completion.ChatCompletion):
        return client.usage.total_tokens
    return 0
def get_llama_output(inp, user_name, fun_call=1, conversation_history=None):
    # TODO: ADD MECHANISM TO LOAD CONVERSATION HISTORY FROM SPECIFIC USER 
    if conversation_history is None:
        conversation_history = []
    conversation_history.append({"role": "user", "content": inp})

    if fun_call == 1:
        # role_system = [ {"role": "system", "content": "You are a helpful assistant that answer questions in a grandiloquent  way"},]
        try:
            response = client.responses.create(
            input=inp,
            model="llama3.1-70b"
            )
            outp = response.output.content.text
        except Exception as e:
            print("An error occurred:", e)
            outp = None  # or some fallback value
            # or
            # outp = response.output.content
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        insert_conversation_history(BASE_DIR, inp, date, user_name, outp)
        outp = "lorem ipsum"  # Update this line after inspecting the response
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        insert_conversation_history(BASE_DIR, inp, date, user_name, outp)
        #print("TOTAL TOKENS: ", end="")
        #print(get_chat_completions_info(response))
        return outp
    elif fun_call==2:
        # refer to function_calling.py
        pass
    elif fun_call==3:
        # refer to function_calling.py
        pass

@app.route("/", methods=["GET", "POST"])
def index():
    openai_version = get_openai_version()
    if request.method == "POST":
        user_input = request.form.get("user_input")
        user_name = request.form.get('user_name')
        if request.form.get("Weather"):
            print("WEATHER!!")
        if request.form.get("News"):
            print("NEWS!!")
        llama_output = get_llama_output(user_input, user_name )
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        try:
            insert_prompt_input(BASE_DIR, user_input, date, user_name)
        except:
            init_db()
            insert_prompt_input(BASE_DIR, user_input, date, user_name)
        return render_template('index.html', user_input=user_input, llama_output=llama_output, openai_version=openai_version)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        try:
            rows = select_prompts(BASE_DIR, "signin")
        except sqlite3.OperationalError:
            init_db()
            rows = select_prompts(BASE_DIR)
        return render_template('index.html', rows=rows, openai_version=openai_version)
def insert_conversation_history(base, inp, d, uname, output):
        db_path = os.path.join(base, "conversations.db")
        try:
            with sqlite3.connect(db_path) as conn:        
                c = conn.cursor()
                # TO BE COMPLETED: WRITE A TABLE THAT STORES CONVERSARTIONS, TEXT, and AI OUTPUT
                c.execute("INSERT INTO conversation (input_text, output, date, user_name) VALUES (?, ?, ?, ?)",
                    (inp, d, uname, output))
                conn.commit()
        except sqlite3.OperationalError:
            c = conn.cursor()
            # TODO: WRITE A TABLE THAT STORES CONVERSARTIONS, TEXT, and AI OUTPUT
            c.execute('''CREATE TABLE IF NOT EXISTS conversation
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    output TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_name TEXT DEFAULT 'guest')''',
                    )
            c.execute('''
                      INSERT INTO conversation (input_text, output, date, user_name) VALUES (?, ?, ?, ?)
                      
            ''', (inp, output, d, uname))
            conn.commit()


def insert_prompt_input(base, inp, d, uname):
        db_path = os.path.join(base, "prompts.db")
        with sqlite3.connect(db_path) as conn:        
            c = conn.cursor()
            c.execute("INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)",
                    (inp, d, uname))
            conn.commit()
def insert_signin_data(base, un, pw):
        db_path = os.path.join(base, "user_session.db")
        time = datetime.now()
        try:    
            with sqlite3.connect(db_path) as conn:        
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS sign_in_users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    time TEXT NOT NULL)
                      ''',
                    )
                c.execute("INSERT INTO sign_in_users (username, password, time) VALUES (?, ?, ?)",
                    (un, pw, time))
                conn.commit()
        except sqlite3.OperationalError:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sign_in_users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    time TEXT NOT NULL)
                      ''',
                    )
            c.execute('''
                      INSERT INTO sign_in_users (username, password, time) VALUES (?, ?, ?)
                      
            ''', (un, pw, time))
            conn.commit()

def select_prompts(base, query="prompts"):
    if query == "prompts":    
        db_path = os.path.join(base, "prompts.db")
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM user_inputs")
            rows = c.fetchall()
        return rows
    else:
        if query == "signin":
            db_path = os.path.join(base, "user_session.db")
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM sign_in_users")
                rows = c.fetchall()
            return rows
@app.route("/register", methods=["GET", "POST"])
def register():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if request.method == "POST":
        pw = request.form.get("pass-word")
        pw2 = request.form.get("pass-word-2")
        un = request.form.get('user-name')
        bd = request.form.get('birthday')
        if pw == pw2:
            insert_register_data(BASE_DIR, un, pw, bd)
    return render_template("register.html")

def insert_register_data(base, username, password, birthday):
    # TODO FInish inserting to table
    return 1

@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if request.method == "POST":
        pw = request.form.get("password")
        un = request.form.get('user-name')
        insert_signin_data(BASE_DIR, un, pw)
        return render_template("signin.html")
    # after saving sign in data let's make sure that the user is logged out after 3600 seconds of inactivity


    return render_template("signin.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # check if admin account is signed in

    # assuming user is not signed in
    user_signed_in = False
    if request.method == "POST":
        user_name = os.getenv("ADMIN_USER")
        password = os.getenv("ADMIN_PASSWORD")
        user_name_input = request.form.get("username")
        password_input = request.form.get("password")
        if user_name == user_name_input and password == password_input:
            message = "SUCCESS"
            session['user_signed_in'] = True
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            prompt_table = select_prompts(BASE_DIR)
            session['prompt_table'] = prompt_table
            return redirect(url_for('admin'))
        else:
            message = "FAILURE"
            return render_template("admin.html", user_signed_in=False, message=message)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        prompt_table = select_prompts(BASE_DIR)
        user_signed_in = session.get('user_signed_in', False)
        return render_template("admin.html", user_signed_in=user_signed_in, prompt_table=prompt_table)
if __name__ == '__main__':
    init_db()
    print("hello world!")
    print(get_openai_version())
    app.run(debug=True)
    


    """
    print("main method: ")
    print(get_client_info(client))
    """