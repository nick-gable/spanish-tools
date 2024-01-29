"""
Flask app for command line practice tool.

Author: Nick Gable (nick@gable.page)
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return open("practice.html").read()