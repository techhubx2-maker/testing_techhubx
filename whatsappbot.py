import os
import requests
from flask import Flask, request

app = Flask(__name__)


# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ==========================================
# HOME
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return "WhatsApp AI Bot is Live!", 200


# ==========================================
# META WEBHOOK VERIFY
# ==========================================

@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("WEBHOOK VERIFY REQUEST", flush=True)

    if mode == "subscribe" and token == VERIFY_TOKEN:

        print("WEBHOOK VERIFIED SUCCESSFULLY", flush=True)

        return challenge, 200

    print("WEBHOOK VERIFICATION FAILED", flush=True)

    return "Verification failed", 403


# ==========================================
# RECEIVE WHATSAPP MESSAGE
# ==========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("INCOMING:", data, flush=True)

    try:

        # --------------------------------------
        # GET MESSAGE
        # --------------------------------------

        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]

        user_text = message.get("text", {}).get("body", "").strip()

        print("USER:", user_text, flush=True)


        # --------------------------------------
        # IGNORE NON-TEXT MESSAGE
        # --------------------------------------

        if not user_text:

            return "OK", 200


        # ======================================
        # CHECK GROQ API KEY
        # ======================================

        if not GROQ_API_KEY:

            print("ERROR: GROQ_API_KEY IS MISSING", flush=True)

            return "OK", 200


        # ======================================
        # SEND USER MESSAGE TO GROQ AI
        # ======================================

        groq_url = "https://api.groq.com/openai/v1/chat/completions"


        groq_headers = {

            "Authorization": f"Bearer {GROQ_API_KEY}",

            "Content-Type": "application/json"

        }


        groq_data = {

            "model": "llama-3.3-70b-versatile",

            "messages": [

                {
                    "role": "system",

                    "content": (
                        "You are a helpful WhatsApp customer support "
                        "assistant for TechHubX Digital Solutions. "

                        "Answer customer questions clearly and "
                        "professionally. "

                        "Keep replies short and useful. "

                        "If the customer says hi, hello or hii, "
                        "reply naturally and ask how you can help. "

                        "Do not mention that you are an AI unless "
                        "the customer asks."
                    )
                },

                {
                    "role": "user",

                    "content": user_text

                }

            ],

            "max_completion_tokens": 300,

            "temperature": 0.5

        }


        print("SENDING MESSAGE TO GROQ...", flush=True)


        ai_response = requests.post(

            groq_url,

            headers=groq_headers,

            json=groq_data,

            timeout=30

        )


        # ======================================
        # GROQ RESPONSE
        # ======================================

        print(
            "GROQ STATUS:",
            ai_response.status_code,
            flush=True
        )


        print(
            "GROQ RESPONSE:",
            ai_response.text,
            flush=True
        )


        # ======================================
        # CHECK GROQ ERROR
        # ======================================

        if ai_response.status_code != 200:

            print(
                "GROQ ERROR:",
                ai_response.text,
                flush=True
            )

            return "OK", 200


        # ======================================
        # GET AI RESPONSE TEXT
        # ======================================

        ai_data = ai_response.json()


        reply = ai_data["choices"][0]["message"]["content"]


        print(
            "AI REPLY:",
            reply,
            flush=True
        )


        # ======================================
        # SEND AI REPLY TO WHATSAPP
        # ======================================

        meta_url = (
            f"https://graph.facebook.com/v23.0/"
            f"{PHONE_ID}/messages"
        )


        meta_headers = {

            "Authorization": f"Bearer {META_TOKEN}",

            "Content-Type": "application/json"

        }


        meta_data = {

            "messaging_product": "whatsapp",

            "to": sender,

            "type": "text",

            "text": {

                "body": reply

            }

        }


        print(
            "SENDING AI REPLY TO WHATSAPP...",
            flush=True
        )


        meta_response = requests.post(

            meta_url,

            headers=meta_headers,

            json=meta_data,

            timeout=30

        )


        # ======================================
        # META RESPONSE
        # ======================================

        print(
            "META STATUS:",
            meta_response.status_code,
            flush=True
        )


        print(
            "META RESPONSE:",
            meta_response.text,
            flush=True
        )


    except Exception as e:

        print(
            "ERROR:",
            str(e),
            flush=True
        )


    return "OK", 200


# ==========================================
# RUN APPLICATION
# ==========================================

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