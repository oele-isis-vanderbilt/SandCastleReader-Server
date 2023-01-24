# Built-in
import pathlib
import logging

# Third-party Imports
from flask import Flask, session, request, jsonify
import pandas as pd

# Setup Logger
logger = logging.getLogger()

# Determine the application's location
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

# Create app instance
app = Flask(__name__)

# Loading super simple CSV user database
user_database = pd.read_csv(str(ROOT_DIR/'assets'/'login_database.csv'))

# Add routes
@app.route("/ping", methods=['GET'])
def ping():
    return jsonify({'respond': 'pong'})

@app.route("/login", methods=['POST'])
def login():

    # Sanitized username and password
    username = str(request.form['username'])
    password = str(request.form['password'])

    # Search in the database
    matching_usernames = user_database[user_database['username'] == username]
    if len(matching_usernames) == 0:
        return jsonify({'success': False, 'msg': 'Incorrect username'})
    else:
        series = matching_usernames.iloc[0]
        if str(series['password']) == password:
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'msg': 'Incorrect password'})

if __name__ == "__main__":
    app.run()
