from flask import Flask, request, render_template, session, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
import openai
from conversation import Conversation
import markdown
from markupsafe import Markup
import boto3
from botocore.exceptions import NoCredentialsError
import function_calling
import news_generator
import socket
from werkzeug.security import generate_password_hash
import psycopg
from user import User

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
# llama output and as a global variable
llama_output = ""
# conversations
conversations = []

create_table="""
                CREATE TABLE IF NOT EXISTS Accounts (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                user_name TEXT NOT NULL UNIQUE,
                time_made TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                birthdate DATE)"""

@app.route("/init_db", methods=["GET", "POST"])
def init_db():
    """Initialize the prompts database if it does not exist."""

    """
    db_url= os.getenv("DATABASE_URL")
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # create table for account
            cur.execute()
            tups = ( ('Cristiano Ronaldo', 'cristiano', '1985-02-05'),
                        ('Lionel Messi', 'leomessi', '1987-06-24'),
                        ('Kylian Mbappe', 'kmbappe', '1998-12-20'))
            cur.executemany("INSERT INTO Accounts (full_name, user_name, birthdate) VALUES (%s, %s, %s)",
                            tups                       
)
            cur.execute("SELECT * FROM Accounts")
            solution = cur.fetchall()

            # insert user account data into table
            conn.commit()
            return str(solution)
"""
    return "testing"

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


def get_llama_output(inp, user_name, fun_call=1, conversation_history=None, is_markdown=False):
    """Get output from the Llama model, optionally using conversation history and function calling."""
    # TODO: ADD MECHANISM TO LOAD CONVERSATION HISTORY FROM SPECIFIC USER 
    if conversation_history is None:
        conversation_history = []
    conversation_history.append({"role": "user", "content": inp})
    #General use of an llm without any function calls
    if fun_call == 1:
        try:
            completion = client.responses.create(
                model="gpt-4.1",
                input= inp,
                instructions="You are an all around assistant."
            )   
            # Extract output from completion object
            outp = completion.output[0].content[0].text
        except Exception as e:
            outp = None  # or some fallback value
        if is_markdown:
            outp = Markup(markdown.markdown(outp))
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        insert_conversation_history(BASE_DIR, inp, date, user_name, outp)
        return outp
    #LLM function call for fetching news
    elif fun_call==2:
        # Try to fetch from AWS S3 cache first (works around News API localhost restriction)
        try:
            aws_client = news_generator.initialize_boto_client()
            file_key = news_generator.get_most_recent_news(aws_client)

            if file_key is not None:
                # Check if cached news is recent (less than 6 hours old)
                sol = news_generator.show_contents_of_file(aws_client, file_key)
                output_list = parse_news_obj(sol)

                # If we have valid cached news, use LLM to process it
                if output_list and len(output_list) > 0:
                    # Format for LLM processing
                    news_text = "\n\n".join([f"{news.get_title()}\n{news.get_source()}\n{news.get_url()}"
                                           for news in output_list])

                    client_llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    completion = client_llm.responses.create(
                        model="gpt-4.1",
                        input=inp + f"\n\nHere are the latest news headlines:\n{news_text}",
                        instructions="Summarize the news headlines based on the user's request. Separate every headline into its own paragraph."
                    )
                    outp = completion.output[0].content[0].text
                    if is_markdown:
                        outp = Markup(markdown.markdown(outp))
                    return outp
        except Exception as e:
            print(f"S3 cache fetch failed: {e}")

        # Fallback: Try direct API call (only works on localhost for free tier)
        try:
            outp = function_calling.news_function_call(inp)
            if is_markdown:
                outp = Markup(markdown.markdown(outp))
            return outp
        except Exception as e:
            print(f"News API call failed: {e}")
            return "Unable to fetch news at this time. Please try again later or contact support."
    # LLM function call for reading wikipedia articles
    elif fun_call==3:
        # refer to function_calling.py
        outp = function_calling.wikipedia_function_call(inp)
        if is_markdown:
            outp = Markup(markdown.markdown(outp))
        return outp
    # WIKIPEDIA
    elif fun_call==4:
        # refer to function_calling.py
        outp=function_calling.weather_function_call(inp)
        if is_markdown:
            outp = Markup(markdown.markdown(outp))
        return outp
def parse_news_obj(news):
    inside_brackets=False
    inside_url=False
    inside_title=False
    inside_news_attr=False
    news_source_attr=""
    PROTOCOL_STR = "http"
    news_attr=""
    news_url_attr=""
    news_title_attr=""
    news_article = news_generator.News("NO_SOURCE", "NO_TITLE", "NO_URL")
    article_list = []
    # if string doesn't look like protocol string then it is news_title
    for i in news:
        if i=="{":
            inside_brackets=True
            news_source_attr=i
            continue
        if i == "}":
            news_source_attr+=i
            continue
        if inside_brackets and i!="\n":
            news_source_attr+=i
            continue
        if i=="\n" and inside_brackets:
            news_article.set_source(news_source_attr)
            inside_brackets=False
            news_source_attr=""
            continue
        else:
            if inside_news_attr:
                if len(news_attr)==4 and news_attr==PROTOCOL_STR:
                    news_url_attr = news_attr
                    news_attr=""
                    news_url_attr+=i
                    inside_url=True
                    continue
                if inside_url:
                    if i=="\n":
                        news_article.set_url(news_url_attr)
                        inside_url=False
                        news_url_attr=""
                        article_list.append(news_article)
                        news_article = news_generator.News("NO_SOURCE", "NO_TITLE", "NO_URL")
                        continue
                    news_url_attr+=i
                    continue
                if len(news_attr)>4 and not inside_url:
                    inside_title=True
                    news_title_attr=news_attr
                    news_attr=""
                    news_title_attr+=i
                    continue
                if inside_title:
                    if i=="\n":
                        news_article.set_title(news_title_attr)
                        inside_title=False
                        news_title_attr=""
                        continue
                    news_title_attr+=i
                    continue
                else:
                    news_attr+=i
                    continue
            else:
                news_attr=i
                inside_news_attr=True

    return article_list
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
        return "AWS credentials not found. Login data not saved to S3."
    except Exception as e:
        return f"Error saving login data to S3: {e}"

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

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for chat interface. Handles user input and displays Llama output."""
    openai_version = get_openai_version()
    if request.method == "POST":
        user_input = request.form.get("user_input")
        user_name = request.form.get('user_name')
        if request.form.get("function_calling")=="Weather":
            news_function_call=False
            weather_ouput = get_llama_output(user_input, user_name, fun_call=4,is_markdown=True)
            conv_object = Conversation(user_input, weather_ouput, is_news=False)
            conversations.append(conv_object)
            return render_template('index.html', user_input=user_input, conversations=conversations, openai_version=openai_version, news_function_call=news_function_call, )     
        if request.form.get("function_calling") == "News":
            news_function_call=True
            news_list = get_llama_output(user_input, user_name, fun_call=2,is_markdown=True)
            conv_object = Conversation(user_input, news_list, is_news=True)
            conversations.append(conv_object)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('index.html', user_input=user_input, conversations=conversations, openai_version=openai_version, news_function_call=news_function_call, )
        if request.form.get("function_calling") == "Wikipedia":
            news_function_call=False
            wiki_text = get_llama_output(user_input, user_name, fun_call=3, is_markdown=True)
            conv_object=Conversation(user_input, wiki_text)
            conversations.append(conv_object)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('index.html', user_input=user_input, conversations=conversations, openai_version=openai_version, news_function_call=news_function_call)
        else:
            llama_output = get_llama_output(user_input, user_name, is_markdown=True)
            conv_object = Conversation(user_input,llama_output)
            conversations.append(conv_object)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('index.html', user_input=user_input, conversations=conversations, openai_version=openai_version)
    else:
        return render_template('index.html', openai_version=openai_version)

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    global conversations
    conversations.clear()
    return redirect(url_for("index"))
@app.route("/register", methods=["GET", "POST"])
def register():
    """Route for user registration. Handles registration form submission."""
    if request.method=="POST":
        fullname = request.form.get("full-name")
        username = request.form.get("user-name")
        birthday = request.form.get("birthday")
        password = request.form.get("pass-word")
        password2 = request.form.get("pass-word-2")
        if password == password2:
            user = User(fullname, username, birthday, password)
            print(user)
        else:
            print("passwords don't match")
            return redirect(url_for("register"))    
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
    prompt_table = select_prompts(BASE_DIR)
    message = None
    admin_valid = False
    if request.method == "POST":
        pw = request.form.get("password")
        un = request.form.get("username")
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
    app.run(debug=False)
    #init_db("rodrigo")