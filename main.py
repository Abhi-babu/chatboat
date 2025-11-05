import ollama
import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclib
import requests
import time

# ------------------- CONFIG -------------------
NEWS_API_KEY = "e6e9c3b8ba3f44ac8f1ea8db9e36316e"
NEWS_URL = "https://newsapi.org/v2/top-headlines"

country_codes = {
    "india": "in",
    "us": "us",
    "america": "us",
    "united states": "us",
    "uk": "gb",
    "england": "gb",
    "australia": "au",
    "canada": "ca"
}

# Init TTS + STT + LLM client
engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    print("Jarvis:", text)  # Log in console
    engine.stop()
    engine.say(text)
    engine.runAndWait()

# ------------------- LLM FUNCTION -------------------

def ask_llm(query):
    try:
        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI voice assistant."},
                {"role": "user", "content": query}
            ]
        )
        answer = response["message"]["content"]
    except Exception as e:
        print("LLM Error:", repr(e))
        # fallback to another model
        try:
            response = ollama.chat(
                model="mistral",   # if you install mistral or another one
                messages=[
                    {"role": "system", "content": "You are Jarvis, a helpful AI voice assistant."},
                    {"role": "user", "content": query}
                ]
            )
            answer = response["message"]["content"]
        except:
            answer = "Sorry, I could not process that request."

    speak(answer)
    return answer


# ------------------- NEWS FUNCTION -------------------
def get_news(country="us"):
    params = {"country": country, "apiKey": NEWS_API_KEY}
    response = requests.get(NEWS_URL, params=params)
    data = response.json()
    if data.get("status") == "ok":
        articles = data.get("articles", [])
        if not articles:
            speak("Sorry, no news found right now.")
        else:
            speak(f"Here are the top 5 headlines for {country.upper()}")
            for i, article in enumerate(articles[:5], 1):  # only 5 headlines
                title = article.get("title")
                print(f"{i}. {title}")
                speak(title)
    else:
        speak("Sorry, I could not fetch the news.")

# ------------------- COMMAND PROCESSING -------------------
def process(c):
    c = c.lower()

    if "open google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open facebook" in c:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")

    elif "open insta" in c:
        speak("Opening Instagram")
        webbrowser.open("https://instagram.com")

    elif "open linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")

    elif "open chatgpt" in c:
        speak("Opening ChatGPT")
        webbrowser.open("https://chatgpt.com")

    elif c.startswith("play"):
        song = c.split(" ", 1)[1] if len(c.split()) > 1 else None
        if song and song in musiclib.music:
            speak(f"Playing {song}")
            webbrowser.open(musiclib.music[song])
        else:
            speak("Sorry, I don't know that song.")

    elif "news" in c:
        country = "in"  # default
        for name, code in country_codes.items():
            if name in c:
                country = code
                break
        speak(f"Fetching news for {country.upper()}")
        get_news(country)

    elif "search" in c or "explain" in c:
        query = c.replace("search", "").replace("explain", "").strip()
        if query:
            speak(f"Searching for {query}")
            ask_llm(query)
        else:
            speak("What should I search for?")

    elif "exit" in c or "quit" in c:
        speak("Goodbye, shutting down.")
        exit()

    else:
        speak("Sorry, I don't know how to do that.")

if __name__ == "__main__":
    speak("Initializing Jarvis")

    while True:
        try:
            # --- Listen for wake word ---
            with sr.Microphone() as source:
                print("Listening for wake word...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            try:
                text = recognizer.recognize_google(audio)
                print("You said:", text)
            except sr.UnknownValueError:
                print("Could not understand wake word")
                continue
            except sr.RequestError as e:
                print("Recognition service error:", e)
                speak("There was an error connecting to the recognition service.")
                continue

            # --- Wake word detected ---
            if "jarvis" in text.lower():
                # Speak acknowledgment AFTER mic is closed
                engine.stop()  # clear queued speech
                speak("Yes?")  # will reliably speak

                # --- Listen for command ---
                with sr.Microphone() as source:
                    print("Listening for command...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    command = recognizer.recognize_google(audio)
                    print("Command is:", command)
                    process(command)
                except sr.UnknownValueError:
                    speak("Sorry, I could not understand the command.")
                except sr.RequestError as e:
                    speak("There was an error with the recognition service.")

        except Exception as e:
            print("Unexpected error:", e)
            speak("An unexpected error occurred.")
