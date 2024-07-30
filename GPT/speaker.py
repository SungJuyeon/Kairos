import speech_recognition as sr

def speak():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # 마이크의 샘플 레이트 확인
        sample_rate = source.SAMPLE_RATE
        print(f"Using sample rate: {sample_rate}")

        print("Listening... Please speak into the microphone.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='ko')
        print("[User] " + text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

speak()