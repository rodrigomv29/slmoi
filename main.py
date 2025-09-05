from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import openai
# import function_calling
import markdown
from markupsafe import Markup
import boto3
from botocore.exceptions import NoCredentialsError

# Initializing Flask App
app = Flask(__name__)
# Configuring OpenAI app using environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# base_url = "https://api.llama-api.com"
client = OpenAI(
    api_key = api_key,
)
# Set Flask secret key
app.secret_key = os.getenv("SECRET_KEY")

def init_db():
    """Initialize the prompts database if it does not exist."""
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

# TODO DEFINE A FUNCTION WHERE USER CAN CUSTOMIZE 
def get_openai_version():
    """Return the current version of the openai package."""
    return openai.__version__

# TODO GET CHAT COMPLETIONS INFO
def get_chat_completions_info(client):
    """Return total tokens used from a chat completion object."""
    if isinstance(client, openai.types.chat.chat_completion.ChatCompletion):
        return client.usage.total_tokens
    return 0

def get_llama_output(inp, user_name, fun_call=1, conversation_history=None):
    """Get output from the Llama model, optionally using conversation history and function calling."""
    # TODO: ADD MECHANISM TO LOAD CONVERSATION HISTORY FROM SPECIFIC USER 
    if conversation_history is None:
        conversation_history = []
    conversation_history.append({"role": "user", "content": inp})

    if fun_call == 1:
        # role_system = [ {"role": "system", "content": "You are a helpful assistant that answer questions in a grandiloquent  way"},]
        try:
            completion = client.responses.create(
                model="gpt-4.1",
                input= inp,
                instructions="You are an all around assistant."
            )   
            # Extract output from completion object
            outp = completion.output[0].content[0].text
        except Exception as e:
            print("An error occurred:", e)
            outp = None  # or some fallback value
        outp = Markup(markdown.markdown(outp))
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        insert_conversation_history(BASE_DIR, inp, date, user_name, outp)
        # print("TOTAL TOKENS: ", end="")
        # print(get_chat_completions_info(response))

        return outp
    elif fun_call==2:
        # refer to function_calling.py
        pass
    elif fun_call==3:
        # refer to function_calling.py
        pass

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for chat interface. Handles user input and displays Llama output."""
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
    """Insert a conversation record into the conversations database."""
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
    """Insert a user prompt into the prompts database."""
    db_path = os.path.join(base, "prompts.db")
    with sqlite3.connect(db_path) as conn:        
        c = conn.cursor()
        c.execute("INSERT INTO user_inputs (input_text, date, user_name) VALUES (?, ?, ?)",
                (inp, d, uname))
        conn.commit()

def insert_signin_data(base, un, pw):
    """Insert sign-in data into the user session database and save to AWS S3 bucket."""
    db_path = os.path.join(base, "user_session.db")
    time = datetime.now()
    # Save to local database as before
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
    # Save login data to AWS S3 bucket
    s3 = boto3.client('s3')
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    object_key = f"logins/{un}_{int(time.timestamp())}.txt"
    login_data = f"username: {un}\npassword: {pw}\ntime: {time}"
    try:
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=login_data)
    except NoCredentialsError:
        print("AWS credentials not found. Login data not saved to S3.")
    except Exception as e:
        print(f"Error saving login data to S3: {e}")

def select_prompts(base, query="prompts"):
    """Select prompts or sign-in data from the appropriate database table."""
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
    """Route for user registration. Handles registration form submission."""
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
    """Insert registration data into the database (to be implemented)."""
    # TODO FInish inserting to table
    return 1

@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    """Route for user sign-in. Handles sign-in form submission and session management."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    message = None
    user_valid = False
    if request.method == "POST":
        pw = request.form.get("password")
        un = request.form.get('user-name')
        try:
            db_path = os.path.join(BASE_DIR, "user_session.db")
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM sign_in_users WHERE username=? AND password=?", (un, pw))
                user = c.fetchone()
                if user:
                    user_valid = True
                    message = "Sign-in successful!"
                    session['user_valid'] = True
                    session['last_activity'] = datetime.now().timestamp()
                else:
                    message = "Invalid username or password."
        except Exception as e:
            user_valid = False
            message = "An error occurred during sign-in."
        return render_template("signin.html", message=message, user_valid=user_valid)
    else:
        # Implement session timeout: log out after 3600 seconds of inactivity
        last_activity = session.get('last_activity')
        if last_activity:
            now = datetime.now().timestamp()
            if now - last_activity > 3600:
                session.pop('user_valid', None)
                session.pop('last_activity', None)
                message = "Session timed out. Please sign in again."
                user_valid = False
            else:
                session['last_activity'] = now
                user_valid = session.get('user_valid', False)
        return render_template("signin.html", message=message, user_valid=user_valid)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Route for admin sign-in. Handles admin signin form submission and session management."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    init_db()
    prompt_table = select_prompts(BASE_DIR)
    message = None
    admin_valid = False
    if request.method == "POST":
        pw = request.form.get("password")
        un = request.form.get('user name')
        try:
            # db_path = os.path.join(BASE_DIR, "user_session.db")
            actual_admin_un = os.getenv("ADMIN_USER")
            actual_admin_pw = os.getenv("ADMIN_PASSWORD")
            if un == actual_admin_un and pw==actual_admin_pw:
                admin_valid = True
                message = "Sign-in successful!"
                session['admin_valid'] = True
                session['last_activity'] = datetime.now().timestamp()
            else:
                message = "Invalid username or password."
        except Exception as e:
            admin_valid = False
            message = "An error occurred during sign-in."
        return render_template("admin.html", message=message, admin_valid=admin_valid, prompt_table=prompt_table)
    else:
        # Implement session timeout: log out after 3600 seconds of inactivity
        last_activity = session.get('last_activity')
        if last_activity:
            now = datetime.now().timestamp()
            if now - last_activity > 3600:
                session.pop('admin_valid', None)
                session.pop('last_activity', None)
                message = "Session timed out. Please sign in again."
                admin_valid = False
            else:
                session['last_activity'] = now
                admin_valid = session.get('admin_valid', False)
        return render_template("admin.html", message=message, admin_valid=admin_valid)
if __name__ == '__main__':
    # Entry point for running the Flask app
    init_db()
    app.run(debug=True)

    """
    print("main method: ")
    print(get_client_info(client))
    """