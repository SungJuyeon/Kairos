import speech_recognition as sr

def speak():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening... Please speak into the microphone.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='ko')
        print("[User] " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")