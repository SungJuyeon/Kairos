
current_emotion = 'None'
current_emotion_probability = 0.0


def set_current_emotion(emotion, probability):
    global current_emotion, current_emotion_probability
    current_emotion = emotion
    current_emotion_probability = probability

def get_current_emotion():
    return current_emotion, current_emotion_probability