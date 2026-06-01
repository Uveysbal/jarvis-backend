from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os

app = Flask(__name__)
CORS(app)

GEMINI_KEY = os.environ.get("GEMINI_KEY")
GROQ_KEY   = os.environ.get("GROQ_KEY")
WEATHER_KEY = os.environ.get("WEATHER_KEY")

JARVIS_PROMPT = """Sen J.A.R.V.I.S.'sin. Tony Stark'ın yapay zeka asistanısın.
Kısa, asil, karizmatik cevaplar ver. Türkçe konuş.
Hiçbir zaman sıradan bir AI gibi davranma."""

def is_quick(text):
    QUICK = ["selam","merhaba","nasılsın","teşekkür","tamam","evet","hayır",
             "ışık","müzik","hava","saat","pil","günaydın","iyi geceler"]
    t = text.lower().strip()
    if len(t) < 40:
        return True
    for w in QUICK:
        if w in t:
            return True
    return False

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    if is_quick(user_msg):
        return groq_reply(user_msg)
    else:
        return gemini_reply(user_msg)

def groq_reply(msg):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-specdec",
        "messages": [
            {"role": "system", "content": JARVIS_PROMPT},
            {"role": "user",   "content": msg}
        ],
        "max_tokens": 300
    }
    r = requests.post(url, headers=headers, json=body, timeout=10)
    result = r.json()
    reply = result["choices"][0]["message"]["content"]
    return jsonify({"reply": reply, "engine": "GROQ"})

def gemini_reply(msg):
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}")
    body = {
        "contents": [{
            "parts": [{"text": f"{JARVIS_PROMPT}\n\nKullanıcı: {msg}"}]
        }]
    }
    r = requests.post(url, json=body, timeout=20)
    result = r.json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"reply": reply, "engine": "Gemini"})

@app.route("/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "Istanbul")
    url = (f"https://api.openweathermap.org/data/2.5/weather"
           f"?q={city}&appid={WEATHER_KEY}&units=metric&lang=tr")
    r = requests.get(url, timeout=8)
    d = r.json()
    return jsonify({
        "city": d["name"],
        "temp": round(d["main"]["temp"]),
        "desc": d["weather"][0]["description"],
        "humidity": d["main"]["humidity"]
    })

@app.route("/ping")
def ping():
    return jsonify({"status": "JARVIS ONLINE"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
