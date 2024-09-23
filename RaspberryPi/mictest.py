import pyaudio
import wave

# 오디오 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "test_audio.wav"

# PyAudio 객체 생성
audio = pyaudio.PyAudio()

# 스트림 열기
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("녹음 시작...")

frames = []

# 5초 동안 오디오 데이터 수집
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("녹음 완료.")

# 스트림 정지 및 닫기
stream.stop_stream()
stream.close()
audio.terminate()

# 녹음된 데이터를 WAV 파일로 저장
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"오디오가 {WAVE_OUTPUT_FILENAME}로 저장되었습니다.")