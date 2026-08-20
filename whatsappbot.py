import os
import requests
from flask import Flask, request

app = Flask(__name__)

# =============================
# META ENVIRONMENT VARIABLES
# =============================
META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")


# =============================
# HOME
# =============================
@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is Live!", 200


# =============================
# META WEBHOOK VERIFY
# =============================
@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("WEBHOOK VERIFY:", flush=True)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED", flush=True)
        return challenge, 200

    print("WEBHOOK VERIFICATION FAILED", flush=True)
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
        # GET WHATSAPP MESSAGE
        # -----------------------------
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]

        user_text = message.get("text", {}).get("body", "")

        print("USER:", user_text, flush=True)


        # -----------------------------
        # IGNORE NON-TEXT MESSAGES
        # -----------------------------
        if not user_text:
            return "OK", 200


        # =============================
        # FIXED REPLY
        # =============================
        reply = "Hi 👋 Welcome to TechHubX Digital Solutions! How can we help you?"


        print("REPLY:", reply, flush=True)


        # =============================
        # SEND REPLY THROUGH META
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