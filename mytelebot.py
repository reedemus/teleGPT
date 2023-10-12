import logging
import time
import os
import telebot
import model_openai
from telebot import types
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

BOT_NAME = "gpt123bot"

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

# List of dictionaries of format:
# [
#  { "user": user_id, "instance": class instance },
# ]
users_chat_history = []

# set threaded=False if deploy on host provider
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)


# ------------------ Flask functions -----------------------------------------------
@app.get("/healthcheck")
def health() -> Response:
    """For the health endpoint, reply with a simple plain text message."""
    response = make_response("The bot is still running fine :)", HTTPStatus.OK)
    response.mimetype = "text/plain"
    return response


# Return a simple message for root path
@app.route("/", methods=["GET", "HEAD"])
def index() -> str:
    return "hello there!"


# Process webhook calls
@app.post(WEBHOOK_URL_PATH)
def webhook() -> Response:
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        print(json_string)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return Response(status=HTTPStatus.OK)
    else:
        logging.info("Webhook payload is invalid")


# ------------------ End of Flask functions ----------------------------------------


# ------------------ Bot functions -------------------------------------------------
# Handle "/start" and "/help"
@bot.message_handler(commands=["help", "start"])
def send_welcome(message: types.Message) -> None:
    """Return a string when start or help command is received"""
    bot.send_message(
        message.chat.id,
        "Hi, I'm a chatbot powered by chatGPT.\
        I can summarize paragraphs of text, translate any \
        sentence, generate contents such as poems, lyrics, \
        or email. Ask me anything.",
    )


# Handle "/clear"
@bot.message_handler(commands=["clear"])
def clear_command(message: types.Message) -> None:
    """Clear chat history to release embedding tokens"""
    user_id = message.from_user.id
    for idx, _ in enumerate(users_chat_history):
        if user_id == users_chat_history[idx]["user"]:
            users_chat_history[idx]["instance"].clear_messages()
            break
    bot.send_message(message.chat.id, "Chat history cleared.")


# llm response handler
def response_handler(user_id: int, prompt: str) -> str:
    """Response handler

    Args:
        user_id: user id from Update
        prompt: user's message

    Returns:
        response string from llm
    """
    # Initialize message list for chatGPT model
    if len(users_chat_history) == 0:
        users_chat_history.append({"user": user_id, "instance": model_openai.ChatGPT()})
        response = users_chat_history[0]["instance"].handle_response(prompt)
    else:
        found = False
        for idx, _ in enumerate(users_chat_history):
            if user_id == users_chat_history[idx]["user"]:
                response = users_chat_history[idx]["instance"].handle_response(prompt)
                found = True
                break
        if not found:
            # found a new user
            users_chat_history.append(
                {"user": user_id, "instance": model_openai.ChatGPT()}
            )
        response = users_chat_history[-1]["instance"].handle_response(prompt)
    return response


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_handler(message: types.Message) -> None:
    """Message handler

    Args:
        update: Update object containing message details such as user id, message contents, etc.
        context: Context object

    Returns:
        None
    """
    msg_type = message.chat.type
    msg = message.text  # Incoming message
    user_id = message.from_user.id

    # print(f"Update Obj: {update}")
    print(f'User {user_id} in {msg_type}: "{msg}"')

    # If in group chat, remove bot name from chat window
    if msg_type == "group":
        if BOT_NAME in msg:
            new_msg = msg.replace(BOT_NAME, "").strip()
            response = response_handler(user_id, new_msg)
            print(f'Bot: "{response}"')
            bot.reply_to(message, response)
        else:
            return
    else:
        # private chat
        response = response_handler(user_id, msg)
        print(f'Bot: "{response}"')
        bot.send_message(message.chat.id, response)


# ------------------ End of bot functions ------------------------------------------

# Remove previous webhook (if any) to ensure new webhook can be set
bot.remove_webhook()
time.sleep(0.1)

webhook_url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
# Set webhook full url, no ssl certificates needed
bot.set_webhook(url=webhook_url)
print(f"Webhook url = {webhook_url}\nBot started...")
