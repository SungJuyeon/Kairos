from gtts import gTTS
import os
from playsound import playsound

def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    #os.system("start output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")



if __name__ == "__main__":
    user_input = input("읽어줄 텍스트를 입력하세요: ")
    text_to_speech(user_input)
