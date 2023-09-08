import openai, os
from dotenv import load_dotenv, find_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_TOKEN')
TELE_API_KEY = os.getenv('TELEGRAM_API_TOKEN')
BOT_NAME = '@gpt123bot' 


# /start cmd handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Type stg to get started!')


# Command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Ask Google loh!')


# Custom command handler
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Custom cmd!')


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} causes error {context.error}')


# Response handler
def handle_response(msg: str) -> str:
    msg_lowercase = msg.lower()

    if 'hello' in msg_lowercase:
        response = 'Nice to meet you'
        return response

    if 'happy' in msg_lowercase:
        response = 'happy to meet you too'
        return response

    # If not getting expected responses, return default msg
    return "I don't understand"


# Input message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    print('Bot response:', response)
    await update.message.reply_text(response)


if __name__ == '__main__':
    print('Bot started...')
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
