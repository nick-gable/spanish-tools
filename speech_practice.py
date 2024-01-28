import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

try:
    print("You said: " + r.recognize_whisper(audio, language="spanish"))
except sr.UnknownValueError:
    print("Unable to understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
