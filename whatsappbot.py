import os
import requests
from flask import Flask, request
import os
import requests
from flask import Flask, request

app = Flask(__name__)

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# -----------------------------
# HOME
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Bot is Live!"


# -----------------------------
# META WEBHOOK VERIFY
# -----------------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# -----------------------------
# RECEIVE WHATSAPP MESSAGE
# -----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("INCOMING:", data, flush=True)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]
        user_text = message.get("text", {}).get("body", "")

        print("USER:", user_text, flush=True)

        if not user_text:
            return "OK", 200

        # -----------------------------
        # AI RESPONSE
        # -----------------------------
        ai_response = requests.post(
            "https://api.llama.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {LLAMA_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "Llama-3.3-70B-Instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful WhatsApp customer support assistant "
                            "for TechHubX Digital Solutions. "
                            "Reply briefly and professionally."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ],
                "max_tokens": 150
            },
            timeout=30
        )

        ai_data = ai_response.json()

        print("AI RESPONSE:", ai_data, flush=True)

        reply = ai_data["completion_message"]["content"]["text"]

        # -----------------------------
        # SEND REPLY THROUGH META
        # -----------------------------
        url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {META_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": sender,
                "type": "text",
                "text": {
                    "body": reply
                }
            },
            timeout=30
        )

        print("META RESPONSE:", response.status_code, response.text, flush=True)

    except Exception as e:
        print("ERROR:", str(e), flush=True)

    return "OK", 200


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)