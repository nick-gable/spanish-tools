"""
Flask app for command line practice tool.

Author: Nick Gable (nick@gable.page)
"""

from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import practice
import json

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {}
with open('users.txt', 'r') as users_file:
    for line in users_file.readlines():
        users[line.strip().split()[0]] = line.strip().split()[1]


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route("/")
@auth.login_required
def index():
    return open("practice.html").read()


@app.route("/getContent", methods=['POST'])
@auth.login_required
def get_content():
    """
    Get content from the backend system, and return it to the frontend.
    """
    request_data = json.loads(request.get_data())

    topic = request_data['topic']  # topic string
    context = request_data['context']  # conversation context, as fed into GPT
    # (0,1) likelihood the question is a speaking question
    speaking_ratio = request_data['speakingRatio']

    return practice.get_content(topic, context, speaking_ratio)


@app.route("/updateWords", methods=['POST'])
@auth.login_required
def update_words():
    """
    Update internal words file based off of results from previous practice.
    """
    request_data = json.loads(request.get_data())
    topic = request_data['topic']
    words = request_data['words']  # list of strings
    word = request_data['word']
    word_idx = request_data['word_idx']
    score = request_data['score']  # 0-1

    practice.update_words(score, words, word, word_idx, topic)

    return {'success': True}


@app.route("/getAudio")
@auth.login_required
def get_audio():
    return send_file("output.mp3")


@app.route("/getAudioSlow")
@auth.login_required
def get_audio_slow():
    return send_file("outputSlow.mp3")
