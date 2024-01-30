"""
Flask app for command line practice tool.

Author: Nick Gable (nick@gable.page)
"""

from flask import Flask, request, send_file
import practice
import json

app = Flask(__name__)


@app.route("/")
def index():
    return open("practice.html").read()


@app.route("/getContent", methods=['POST'])
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
def update_words():
    """
    Update internal words file based off of results from previous practice.
    """
    request_data = json.loads(request.get_json())
    topic = request_data['topic']
    words = request_data['words']  # list of strings
    word_idx = request_data['word_idx']
    score = request_data['score']  # 0-1

    practice.update_words(score, words, word_idx, topic)

    return {'success': True}


@app.route("/getAudio")
def get_audio():
    return send_file("output.mp3")