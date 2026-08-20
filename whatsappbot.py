import os
import requests
from flask import Flask, request

app = Flask(__name__)

# =============================
# ENVIRONMENT VARIABLES
# =============================
META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =============================
# HOME
# =============================
@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Bot is Live!"


# =============================
# META WEBHOOK VERIFY
# =============================
@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# =============================
# RECEIVE WHATSAPP MESSAGE
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("INCOMING:", data, flush=True)

    try:

        # -----------------------------
        # GET MESSAGE
        # -----------------------------
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]

        user_text = message.get("text", {}).get("body", "")

        print("USER:", user_text, flush=True)

        if not user_text:
            return "OK", 200


        # -----------------------------
        # CHECK GROQ KEY
        # -----------------------------
        if not GROQ_API_KEY:

            print("ERROR: GROQ_API_KEY is missing", flush=True)

            return "OK", 200


        # =============================
        # GROQ AI
        # =============================
        ai_response = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },

            json={

                "model": "llama-3.3-70b-versatile",

                "messages": [

                    {
                        "role": "system",
                        "content": (
                            "You are a helpful WhatsApp customer support "
                            "assistant for TechHubX Digital Solutions. "
                            "Reply briefly and professionally."
                        )
                    },

                    {
                        "role": "user",
                        "content": user_text
                    }

                ],

                "max_completion_tokens": 150

            },

            timeout=30
        )


        # =============================
        # GROQ RESPONSE
        # =============================
        ai_data = ai_response.json()

        print(
            "AI STATUS:",
            ai_response.status_code,
            flush=True
        )

        print(
            "AI RESPONSE:",
            ai_data,
            flush=True
        )


        # =============================
        # CHECK GROQ ERROR
        # =============================
        if ai_response.status_code != 200:

            print(
                "GROQ ERROR:",
                ai_data,
                flush=True
            )

            return "OK", 200


        # =============================
        # GET AI REPLY
        # =============================
        reply = ai_data["choices"][0]["message"]["content"]

        print(
            "AI REPLY:",
            reply,
            flush=True
        )


        # =============================
        # SEND MESSAGE TO WHATSAPP
        # =============================
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


        # =============================
        # META RESPONSE
        # =============================
        print(
            "META STATUS:",
            response.status_code,
            flush=True
        )

        print(
            "META RESPONSE:",
            response.text,
            flush=True
        )


    except Exception as e:

        print(
            "ERROR:",
            str(e),
            flush=True
        )


    return "OK", 200


# =============================
# RUN
# =============================
if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )