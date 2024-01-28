from gtts import gTTS
import pygame
from io import BytesIO
from os import system
from time import sleep
from random import randint, random
from num2words import num2words
import sys

# probability that all four digits are said at the same time for last four
FOUR_DIGIT_PROB = 0.3

# probability that digits are read out individually for any section
ONE_DIGIT_PROB = 0.1

INITIAL_SLEEP_TIME = 3

# faster after streak of X in a row
FAST_AFTER = 1

INCORRECT_MULTIPLIER = 1
CORRECT_MULTIPLIER = 1

pygame.init()


def say(text, slow=False, lang='es'):
    tts = gTTS(text=text, lang=lang, slow=slow)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def random_phone_number():
    """
    Returns random ten digit phone number as (area, exchange, last 4) tuple
    """
    area = 100 * randint(1, 9) + 10 * randint(0, 9) + randint(0, 9)
    exchange = 100 * randint(1, 9) + 10 * randint(0, 9) + randint(0, 9)
    last_4 = 1000 * randint(0, 9) + 100 * randint(0, 9) + \
        10 * randint(0, 9) + randint(0, 9)

    return (str(area), str(exchange), "%04.f" % last_4)


def main():
    count = 1
    sleep_time = INITIAL_SLEEP_TIME
    slow = True
    streak = 0
    while True:
        print(f"Speaking number {count}, streak is {streak}")

        number = random_phone_number()
        correct_text = ""

        # print prompt string before we speak and sleep main thread
        print("Answer (XXX-XXX-XXXX): ", end='')
        sys.stdout.flush()

        for i in range(3):
            if random() < ONE_DIGIT_PROB:
                text = ' '.join(number[i])
            elif i == 2 and random() < FOUR_DIGIT_PROB:
                text = number[i][:2] + " " + number[i][2:]
            else:
                text = number[i]

            for word in text.split():
                correct_text += num2words(int(word), lang='es') + " "
            say(text, slow)

            if i < 2:
                sleep(sleep_time)
        
        answer = input()

        if answer.strip() != '-'.join(number):
            print(f"Incorrect! For {correct_text}")
            print(f"You said: {answer}")
            print(f"Correct:  {'-'.join(number)}")
            sleep_time *= INCORRECT_MULTIPLIER
            slow = True
            streak = 0
        else:
            print("Correct!")
            sleep_time *= CORRECT_MULTIPLIER
            streak += 1
            if streak >= FAST_AFTER:
                slow = False

        input("Press return to continue")
        print()
        count += 1


if __name__ == "__main__":
    main()
