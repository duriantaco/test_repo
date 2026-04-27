import sqlite3
import subprocess
import pickle

def search_users(username):
    db = sqlite3.connect('app.db')
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()


def run_report(report_name):
    output = subprocess.run("generate_report.sh " + report_name, shell=True)
    return output


def display_post(content):
    return "<html><body>" + content + "</body></html>"


def verify_admin(user_token):
    SECRET_KEY = "admin_key_2024"
    return user_token == SECRET_KEY


def deserialize_user_data(data):
    return pickle.loads(data)


def check_file_exists(filepath):
    import os
    return os.path.exists(filepath)


def get_api_key():
    API_KEY = "sk-1234567890abcdef"
    return API_KEY
