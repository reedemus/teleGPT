import os
import logging
import model_openai
from dotenv import load_dotenv, find_dotenv
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
    llm.clear_messages()
    await update.message.reply_text("Chat history cleared.")


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prints error message"""
    print(f"Update {update} causes error {context.error}")


# Response handler
def handle_response(msg: str) -> str:
    """Pass user input to llm and returns the response as string"""
    return llm.handle_response(msg)


# Input message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message handler

    Args:
        update: Update object containing message details such as user id, message contents, etc.
        context: Context object

    Returns:
        None

    TODO :
    1) handle multiple users' responses - track each user's chat history from Update user id
    2) handle streaming response from chatGPT API (stream = true)
    """
    msg_type = update.message.chat.type
    msg = update.message.text  # Incoming message
    user = update.message.from_user.id  # User id

    # print(f"Update Obj: {update}")
    print(f'User {user} in {msg_type}: "{msg}"')

    # If in group chat, remove bot name from chat window
    if msg_type == "group":
        if BOT_NAME in msg:
            new_msg = msg.replace(BOT_NAME, "").strip()
            response, _ = handle_response(new_msg)
        else:
            return
    else:
        # private chat
        response, _ = handle_response(msg)

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
