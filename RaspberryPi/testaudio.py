from gtts import gTTS
import os
import asyncio

async def text_to_audio(text, lang='ko'):
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, play_audio)

def play_audio():
    os.system("mpg321 output.mp3")

async def infinite_audio_loop():
    while True:
        text = input("재생할 텍스트를 입력하세요 (종료하려면 'q' 입력): ")
        if text.lower() == 'q':
            break
        await text_to_audio(text)

if __name__ == "__main__":
    asyncio.run(infinite_audio_loop())