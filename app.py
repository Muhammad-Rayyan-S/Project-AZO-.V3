#Imports
import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import re


#Word Brake Text Capitalisation Bolding ect...
def format_markdown(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = text.replace("\n", "<br>")
    return text

#Loading Api Frm Env
load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

#Temprory Chat History
chat_history = []


def load_website_info():
    path = "info/website_info.md"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
    
website_info = load_website_info()


# Initialize chat with system message
chat_history.append({"role": "user", "parts": [website_info]})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "").strip()
    
    if not user_input:
        return jsonify({"reply": "⚠️ Please enter a question!"})

    chat_history.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(chat_history)
        reply = (response.text or "").strip()
        if not reply:
            raise ValueError("Empty response")
        
        chat_history.append({"role": "assistant", "parts": [reply]})
        formatted_reply = format_markdown(reply)
        return jsonify({"reply": formatted_reply})

    except Exception:
        return jsonify({"reply": "⚠️ Oops, I couldn't answer that properly. Try asking something related to Rayyan!"})
    
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "user", "parts": [website_info]}]
    return jsonify({"status": "reset"})

@app.route('/ping')
def ping():
    return 'pong' , 200

#Starting App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
