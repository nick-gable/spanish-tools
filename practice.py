"""
Spanish practice tool that alternates requesting English and Spanish translations of things,
using GPT-3 to generate content.

Author: Nick Gable
"""

from openai import OpenAI
from phone_numbers import say
from gtts import gTTS
from random import random, randint

from ratelimit import limits, sleep_and_retry

SECRET_KEY = open('key.txt','r').read().strip()
client = OpenAI(api_key=SECRET_KEY)

P_TOPIC_WORD =  """
Please respond with one sentence in Spanish on the topic '%s' using any form of the word or phrase '%s'. 
After this, please respond with the same sentence in English. 
Format your response as two lines, the first being 'Spanish: ' followed by the Spanish sentence, 
the second being 'English: ' followed by the English sentence."""


P_TOPIC_NWORD = """
Please respond with one sentence in Spanish on the topic '%s'. 
After this, please respond with the same sentence in English. 
Format your response as two lines, the first being 'Spanish: ' followed by the Spanish sentence, 
the second being 'English: ' followed by the English sentence.
"""

P_NTOPIC_WORD = """
Please respond with one sentence in Spanish on any topic using any form of the word or phrase '%s'.
After this, please respond with the same sentence in English. 
Format your response as two lines, the first being 'Spanish: ' followed by the Spanish sentence, 
the second being 'English: ' followed by the English sentence.
"""

P_NTOPIC_NWORD = """
Please respond with one sentence in Spanish on any topic.
After this, please respond with the same sentence in English. 
Format your response as two lines, the first being 'Spanish: ' followed by the Spanish sentence, 
the second being 'English: ' followed by the English sentence.
"""

VARIATION_MESSAGE = """
When prompted repeatedly, please vary your responses.
"""

REPEAT_MESSAGE = "Please generate another unique response to the previous prompt."

REPEAT_NEW_WORD = "Please generate another unique response to the previous prompt, this time making sure to use any form of the word or phrase '%s'."


@sleep_and_retry
@limits(calls=500, period=60)
def prompt(message: str, existing_messages=[]):
    result = client.chat.completions.create(model="gpt-3.5-turbo",
                                            messages=existing_messages + [
                                                message
                                            ])

    return result.choices[0].message


def get_content(topic, messages, speaking_ratio):
    words = [] # list of (word,score) tuples (0->1 value indicating if it should be picked)
    
    try:
        file = open(f'practice-{topic}.csv', 'r', encoding="utf_8")
        print("Topic has been visited prior, loading history from file")

        for line in file.readlines():
            line = line.strip().split(',')
            words.append((line[0], float(line[1])))
    except IOError:
        print("First time on this topic, starting new topic file")

    word = None
    word_idx = None
    if len(messages) == 0:
        message = {'role': 'user', 'content': P_TOPIC_NWORD % (topic,) + " " + VARIATION_MESSAGE}
    elif len(words) == 0:
        message = {'role': 'user', 'content': REPEAT_MESSAGE}
    else:
        word = None
        word_idx = None
        while word is None:
            word_idx = randint(0, len(words) - 1)
            possible_word, score = words[randint(0, len(words) - 1)]
            if random() < score:
                word = possible_word
        
        message = {'role': 'user', 'content': REPEAT_NEW_WORD % (word,)}
    
    #print(messages)
    response = prompt(message, existing_messages=messages)

    messages.append(message)
    messages.append({
        'content': response.content,
        'role': response.role
    })

    if random() < speaking_ratio:
        type = 'speak'
    else:
        type = 'listen'
        tts = gTTS(text=response.content.split('\n')[0].split("Spanish: ")[1], lang='es')
        tts.write_to_fp(open('output.mp3', 'wb'))
    
    return {
        'type': type,
        'messages': messages,
        'word': word,
        'word_idx': word_idx
    }


def update_words(score, new_words, word, word_idx, topic):
    words = [] # list of (word,score) tuples (0->1 value indicating if it should be picked)
    
    try:
        file = open(f'practice-{topic}.csv', 'r', encoding='utf_8')
        print("Topic has been visited prior, loading history from file")

        for line in file.readlines():
            line = line.strip().split(',')
            words.append((line[0], float(line[1])))
    except IOError:
        print("First time on this topic, starting new topic file")

    if score < 1:
        for word in new_words:
            words.append((word, 1-score))
    elif len(words) > 0 and (word is not None):  # reduce chance of this word appearing again
        words[word_idx] = (word, words[word_idx][1] / 2) # make it half as likely we encounter this word again
        if words[word_idx][1] < 0.10:
            # just delete it at this point
            del words[word_idx]

    # write out topics file
    with open(f'practice-{topic}.csv', 'w', encoding='utf_8') as file:
        for (word, score) in words:
            file.write(f'{word},{score}\n')


if __name__ == "__main__":
    topic = input("Enter a topic: ")

    messages = []
    words = [] # list of (word,score) tuples (0->1 value indicating if it should be picked)
    
    try:
        file = open(f'practice-{topic}.csv', 'r', encoding='utf_8')
        print("Topic has been visited prior, loading history from file")

        for line in file.readlines():
            line = line.strip().split(',')
            words.append((line[0], float(line[1])))
    except IOError:
        print("First time on this topic, starting new topic file")

    while True:
        word = None
        word_idx = None
        if len(messages) == 0:
            message = {'role': 'user', 'content': P_TOPIC_NWORD % (topic,) + " " + VARIATION_MESSAGE}
        elif len(words) == 0:
            message = {'role': 'user', 'content': REPEAT_MESSAGE}
        else:
            word = None
            word_idx = None
            while word is None:
                word_idx = randint(0, len(words) - 1)
                possible_word, score = words[randint(0, len(words) - 1)]
                if random() < score:
                    word = possible_word
            
            message = {'role': 'user', 'content': REPEAT_NEW_WORD % (word,)}
        
        response = prompt(message, existing_messages=messages)

        messages.append(message)
        messages.append(response)

        response = response.content
        spanish = response.split('\n')[0].split("Spanish: ")[1]

        if random() < 0.5:
            say(spanish)
        else:
            print(response.split('\n')[1])

        input("Enter your translation: ")
        print()
        print(response)

        score = float(input("Self score (0 to 1): "))
        if score < 1:
            new_words = input("Enter words you would like to improve, separated by commas: ")
            new_words = new_words.split(',')
            for word in new_words:
                words.append((word, 1-score))
        elif len(words) > 0 and (word is not None):  # reduce chance of this word appearing again
            words[word_idx] = (word, words[word_idx][1] / 2) # make it half as likely we encounter this word again
            if words[word_idx][1] < 0.01:
                # just delete it at this point
                del words[word_idx]

        # write out topics file
        with open(f'practice-{topic}.csv', 'w', encoding="utf_8") as file:
            for (word, score) in words:
                file.write(f'{word},{score}\n')

        input("Press enter to try again! ")
