# Built-in
import os
import pathlib
import logging
import threading
import copy
from dotenv import load_dotenv

load_dotenv()

# Third-party Imports
from flask import Flask, session, request, jsonify
from flask_cors import CORS
import pandas as pd

# Internal Imports
from .updated_json_provider import UpdatedJSONProvider

# Setup Logger
logger = logging.getLogger()

# Determine the application's location
ROOT_DIR = pathlib.Path(os.path.abspath(__file__)).parent.parent
LOGS_DIR = ROOT_DIR / "logs"

# Create app instance
app = Flask(__name__)
app.json = UpdatedJSONProvider(app)
app.secret_key = os.environ.get("SECRET_KEY")

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Loading super simple CSV user database
csv_writing_lock = threading.Lock()
user_database = pd.read_csv(str(ROOT_DIR / "scrs" / "assets" / "login_database.csv"))
glossary_database = pd.read_csv(str(ROOT_DIR / "scrs" / "assets" / "glossary_database.csv"))

# Add routes
@app.route("/", methods=["GET"])
def home():
    return "SandCastleReader Server Alive"


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"response": "pong"})


@app.route("/login", methods=["POST"])
def login():

    # Sanitized username and password
    username = str(request.form["username"])
    password = str(request.form["password"])

    # Search in the database
    matching_usernames = user_database[user_database["username"] == username]
    if len(matching_usernames) == 0:
        return jsonify({"success": False, "msg": "Incorrect username"})
    else:
        series = matching_usernames.iloc[0]
        if str(series["password"]) == password:
            session["logged_in"] = True
            session["username"] = copy.copy(username)
            return jsonify({"success": True})

    return jsonify({"success": False, "msg": "Incorrect password"})


@app.route("/logs", methods=["POST"])
def logs():

    # Extract the information (timestamp, topic, information)
    timestamp = request.form["timestamp"]
    topic = request.form["topic"]
    info = request.form["information"]
    username = request.form["username"]
    data = {"timestamp": timestamp, "topic": topic, "info": info}

    df: pd.DataFrame = pd.Series(data).to_frame().T

    # Compute the path
    user_csv_path = LOGS_DIR / f"{username}-records.csv"

    # Get the content and write it to the logs
    with csv_writing_lock:
        df.to_csv(
            str(user_csv_path), mode="a", header=not user_csv_path.exists(), index=False
        )

    return jsonify({"success": True, "record": "saved"})


@app.route('/glossary', methods=["GET", "POST"])
def glossary_list():

    if request.method == 'GET':
        
        # glossary = []
        # for i, row in glossary_database.iterrows():
        #     glossary.append(f"p{row['pdf_id']}w{row['word_id']}")
        glossary = glossary_database['pdf_word_id'].values.tolist()

        return jsonify({"success": True, "glossary": glossary})

    elif request.method == 'POST':
        
        # Get the inputs
        pdf_word_id = str(request.form['pdf_word_id'])
        matching_ids = glossary_database[glossary_database['pdf_word_id'] == pdf_word_id]
        if len(matching_ids) == 0:
            return jsonify({"success": False, "word": '', "definition": ''})
        else:
            series = matching_ids.iloc[0]
            return jsonify({"success": True, "word": series['word'], "definition": series['definition']})

    return jsonify({'success': False})


@app.route("/logout", methods=["POST"])
def logout():

    session.pop("logged_in", None)
    session.pop("username", None)

    return jsonify({"success": True, "username": request.form["username"]})
