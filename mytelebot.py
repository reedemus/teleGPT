# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import logging
import time
import os
import telebot
from http import HTTPStatus
from flask import Flask, Response, make_response, request
from dotenv import load_dotenv, find_dotenv

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# PUBLIC_URL = FQDN provided by host provider
# FQDN should include "https://" from environment variable stored at host provider
WEBHOOK_HOST = os.getenv("PUBLIC_URL")
WEBHOOK_URL_BASE = f"{WEBHOOK_HOST}"
WEBHOOK_URL_PATH = "/webhook"

# Since HTTPS is handled by webhost provider, not required to set HTTPS port 443 or 8443
# WEBHOOK_PORT = 10000
# WEBHOOK_LISTEN = "127.0.0.1"

logging.basicConfig(
    filename="telegpt.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# set threaded=False if deploy on host provider
bot = telebot.TeleBot(API_TOKEN, threaded=False)


app = Flask(__name__)


@app.get("/healthcheck")
def health() -> Response:
    """For the health endpoint, reply with a simple plain text message."""
    response = make_response("The bot is still running fine :)", HTTPStatus.OK)
    response.mimetype = "text/plain"
    return response


# Return a simple message for root path
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "hello there!"


# Process webhook calls
@app.post(WEBHOOK_URL_PATH)
def webhook() -> Response:
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        print(json_string)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        response = make_response("Got an update from Telegram!", HTTPStatus.OK)
        return response
    else:
        logging.info("Webhook payload is invalid")


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    # print("Command msg received")
    bot.reply_to(
        message,
        ("Hi there, I am EchoBot.\n" "I am here to echo your kind words back to you."),
    )


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_message(message):
    # print("Other type of messages received")
    bot.reply_to(message, message.text)


# Remove previous webhook (if any) to ensure new webhook can be set
bot.remove_webhook()
time.sleep(0.1)

webhook_url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
# Set webhook full url, no ssl certificates needed
bot.set_webhook(url=webhook_url)
# print(f"Webhook url = {webhook_url}")
