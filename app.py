import os
import model_openai
from dotenv import load_dotenv, find_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
TELE_API_KEY = os.getenv('TELEGRAM_API_TOKEN')
BOT_NAME = '@gpt123bot' 

# /start cmd handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return a string when start command is received"""
    await update.message.reply_text(f"Hi, I'm a chatbot powered by {llm.name}. Ask me anything.")


# Command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return helpful information when help command is received"""
    await update.message.reply_text(
        'I can summarize paragraphs of text, translate any \
        sentence, generate contents such as poems, lyrics, \
        or email. Ask me anything.')


# Custom command handler
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return a string when custom command is received"""
    await update.message.reply_text('Custom cmd!')


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} causes error {context.error}')


# Response handler
def handle_response(msg: str) -> str:
    return llm.handle_response(msg)


# Input message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message handler

    update: Update object containing message details such as user id, message contents, etc.
    context: Context object

    TODO :
    1) handle multiple users' responses - track each user's chat history from Update user id
    2) handle streaming response from chatGPT API (stream = true)
    """
    msg_type = update.message.chat.type
    msg = update.message.text           # Incoming message

    print(f'User {update.message.chat.id} in {msg_type}: "{msg}"')

    # If in group chat, remove bot name from chat window
    if msg_type == 'group':
        if BOT_NAME in msg:
            new_msg = msg.replace(BOT_NAME, '').strip()
            response = handle_response(new_msg)
        else:
            return
    else:
    # private chat
        response = handle_response(msg)

    # print response message for debug
    print(f'Bot: "{response}"')
    await update.message.reply_text(response)


if __name__ == '__main__':
    print('Bot started...')
    llm = model_openai.ChatGPT()
    app = Application.builder().token(TELE_API_KEY).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    #Errors
    app.add_error_handler(error)

    # polling
    print('Running...')
    app.run_polling(poll_interval=3)
