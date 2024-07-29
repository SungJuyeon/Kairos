import openai
import os
from dotenv import load_dotenv
from weather_info import get_weather_info

# Load environment variables from a .env file
load_dotenv()

# Set your API key
openai.api_key = os.getenv("GPT_API_KEY")

# Start with a system message
messages = [
    {"role": "system", "content": (
        "Your name is Herobot and you are a personal assistant AI. "
        "Your tasks are, first, to inform me of the weather in Seoul. "
        "Second, you act as a calendar assistant."
    )}
]

# Function to determine forecast day based on user input
def determine_forecast_day(user_input):
    if "오늘" in user_input or "today" in user_input:
        return 0
    elif "내일" in user_input or "tomorrow" in user_input:
        return 1
    elif "모레" in user_input:
        return 2
    else:
        return None

# Conversation loop
while True:
    # Get user input
    user_content = input("user: ")

    # Check for weather-related queries and determine forecast day
    forecast_day = determine_forecast_day(user_content)
    if forecast_day is not None:
        weather_info = get_weather_info(forecast_day)
        print(f"assistant: {weather_info}")
        continue

    # Add user message to conversation
    messages.append({"role": "user", "content": user_content})

    # Generate a response from the GPT model
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )

    # Get the assistant's message and add it to the conversation
    ai_message = completion.choices[0].message["content"].strip()
    messages.append({"role": "assistant", "content": ai_message})

    # Print the AI's response
    print(f"assistant: {ai_message}")

    # Optional: add a condition to break the loop
    if user_content.lower() in ['exit', 'bye']:
        print("! bye !")
        break
