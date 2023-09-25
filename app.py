import os
import logging
import model_openai
from dotenv import load_dotenv, find_dotenv
from enum import Enum, auto
from telegram import Update, constants
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
TELE_API_KEY = os.getenv("TELEGRAM_API_TOKEN")
BOT_NAME = "@gpt123bot"

logging.basicConfig(
    filename="telegpt.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
)

class UserEnum(Enum):
    UNKNOWN_USER = auto()

# List of dictionaries of format:
# [  
#  { "user": user_id, "messages": user_messages },
# ]
users_chat_history = [{"user": UserEnum.UNKNOWN_USER}]


class ChatHistory():
    def __init__(self):
        self._message = [{"role": "system", "content": "You are a helpful assistant."}]

    # a getter function
    @property
    def message(self):
        """Returns list of messages

        Args:
            None

        Returns:
            list
        """
        return self._message

    # setter function
    @message.setter
    def message(self, msg):
        self._message = msg


def update_chat_history(user_id: int, user_messages: ChatHistory) -> None:
    """Update chat history of the user"""
    found = False
    for idx, _ in enumerate(users_chat_history):
        if user_id == users_chat_history[idx]["user"]:
            found = True
            users_chat_history[idx]["messages"] = user_messages
            break
    if not found:
        users_chat_history.append({"user": user_id, "messages": user_messages})


def get_chat_history(user_id: int) -> ChatHistory:
    """Returns the chat history of the user"""
    # Initialize message list for chatGPT model
    if users_chat_history[0]["user"] == UserEnum.UNKNOWN_USER:
        users_chat_history[0]["user"] = user_id
        users_chat_history[0]["messages"] = ChatHistory()
    else:
        found = False
        for idx, _ in enumerate(users_chat_history):
            if user_id == users_chat_history[idx]["user"]:
                chat_history = users_chat_history[idx]["messages"]
                found = True
                break
        if not found:
            # found a new user
            chat_history = ChatHistory()
            users_chat_history.append({"user": user_id, "messages": chat_history})
    return chat_history

# start cmd handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return a string when start command is received"""
    await update.message.reply_text(
        f"Hi, I'm a chatbot powered by {llm.name}. Ask me anything."
    )


# help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return helpful information when help command is received"""
    await update.message.reply_text(
        "I can summarize paragraphs of text, translate any \
        sentence, generate contents such as poems, lyrics, \
        or email. Ask me anything."
    )


# clear command handler
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear chat history to release embedding tokens"""
    user_id = update.message.from_user.id
    llm.clear_messages(user_id)
    await update.message.reply_text("Chat history cleared.")


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prints error message"""
    print(f"Update {update} causes error {context.error}")


# llm response handler
async def response_handler(user_id: int, prompt: str) -> str:
    """Response handler

    Args:
        user_id: user id from Update
        prompt: user's message

    Returns:
        response string from llm
    """
    chat_history = get_chat_history(user_id)
    chat_history.append({"role": "user", "content": f"prompt"})
    response = llm.handle_response(chat_history)
    update_chat_history(user_id, response)
    return response[-1]["content"]

# Input message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message handler

    Args:
        update: Update object containing message details such as user id, message contents, etc.
        context: Context object

    Returns:
        None
    """
    msg_type = update.message.chat.type
    msg = update.message.text  # Incoming message
    user_id = update.message.from_user.id

    # print(f"Update Obj: {update}")
    print(f'User {user_id} in {msg_type}: "{msg}"')

    # If in group chat, remove bot name from chat window
    if msg_type == "group":
        if BOT_NAME in msg:
            new_msg = msg.replace(BOT_NAME, "").strip()
            response = response_handler(user_id, new_msg)
        else:
            return
    else:
        # private chat
        response = response_handler(user_id, msg)

    # print response message for debug
    print(f'Bot: "{response}"')
    # show anmation that bot is typing
    await context.bot.sendChatAction(
        chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING
    )
    await update.message.reply_text(response)


if __name__ == "__main__":
    print("Bot started...")
    llm = model_openai.ChatGPT()
    app = Application.builder().token(TELE_API_KEY).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # polling
    print("Running...")
    app.run_polling(poll_interval=1)
