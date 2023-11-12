import os
import logging
import model_openai
from dotenv import load_dotenv, find_dotenv
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
    CallbackQueryHandler
)

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
TELE_API_KEY = os.getenv("TELEGRAM_API_TOKEN")
BOT_NAME = os.getenv("TELEGRAM_BOT_NAME")

logging.basicConfig(
    filename=f"{BOT_NAME}.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
)

# List of dictionaries of format:
# [
#  { "user": user_id, "instance": class instance, "model": selected model},
# ]
users_chat_history = []

# model options
model = {"GPT-3.5": "gpt-3.5-turbo", "GPT-4": "gpt-4-1106-preview", "GPT-4V": "gpt-4-vision-preview"}

# start cmd handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return a string when start command is received"""
    await update.message.reply_text(
        "Hi, I'm a chatbot powered by chatGPT. Ask me anything."
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
    for idx, _ in enumerate(users_chat_history):
        if user_id == users_chat_history[idx]["user"]:
            users_chat_history[idx]["instance"].clear_messages()
            break
    await update.message.reply_text("Chat history cleared.")


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prints error message"""
    print(f"Update {update} causes error {context.error}")


async def choice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("GPT-3.5", callback_data=model["GPT-3.5"]),
            InlineKeyboardButton("GPT-4", callback_data=model["GPT-4"]),
        ],
        [InlineKeyboardButton("GPT-4 Vision", callback_data=model["GPT-4V"])],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your model:", reply_markup=reply_markup)


async def callback_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    if query.data == model["GPT-3.5"]:
        ans = "GPT-3.5"
    elif query.data == model["GPT-4"]:
        ans = "GPT-4"
    elif query.data == model["GPT-4V"]:
        ans = "GPT-4 Vision"
    else:
        ans = "nothing selected"
    await query.answer()
    await query.edit_message_text(f"Selected {ans}.")
    save_model_name(query.from_user.id, query.data)


def save_model_name(user_id: int, model_name: str) -> None:
    """Save model name in user's chat history and in model class property"""
    if len(users_chat_history) == 0:
        users_chat_history.append(
            {
                "user": user_id,
                "instance": model_openai.ChatGPT(model_name),
                "model": model_name,
            }
        )
    else:
        found = False
        for idx, _ in enumerate(users_chat_history):
            if user_id == users_chat_history[idx]["user"]:
                users_chat_history[idx]["model"] = model_name
                users_chat_history[idx]["instance"].model = model_name
                found = True
                break
        if not found:
            # found a new user
            users_chat_history.append(
                {
                    "user": user_id,
                    "instance": model_openai.ChatGPT(model_name),
                    "model": model_name,
                }
            )


async def get_choice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns a reply about the model selected by the user"""
    user_id = update.message.from_user.id
    if len(users_chat_history) != 0:
        for idx, _ in enumerate(users_chat_history):
            if user_id == users_chat_history[idx]["user"]:
                model_choice = users_chat_history[idx]["instance"].model
                await update.message.reply_text(f"Your model selection is {model_choice}.")
                break
            else:
                await update.message.reply_text(f"You have not selected any model.")


def isNewUser(user_id: int):
    """Insert new user to user_chat_history list if not found.

    Args:
        status: bool = True if new user is found, False otherwise
        index: int = user's index position in the list

    Returns:
        (status, index)
    """
    retVal: bool = False
    index: int = 0

    # Initialize message list for chatGPT model
    if len(users_chat_history) == 0:
        users_chat_history.append(
            {
                "user": user_id,
                "instance": model_openai.ChatGPT(),
                "model": "none",
            }
        )
        retVal = True
    else:
        for idx, _ in enumerate(users_chat_history):
            if user_id == users_chat_history[idx]["user"]:
                index = idx
                break
            else:
                # found a new user
                users_chat_history.append(
                    {
                        "user": user_id,
                        "instance": model_openai.ChatGPT(),
                        "model": "none",
                    }
                )
                index = idx + 1
                retVal = True
    return (retVal, index)


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
    is_new_user, idx = isNewUser(user_id)
    if is_new_user == True or users_chat_history[idx]["model"] == "none":
        response = "model not selected"
    else:
        response = users_chat_history[idx]["instance"].handle_response(prompt)
    return response


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
    if response == "model not selected":
        await update.message.reply_text("Please choose a model before we begin.")
        await choice_command(update, context)
    else:
        await update.message.reply_text(response)


async def handle_message_with_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle receiving photo attachment with text caption

    Args:
        update: Update object containing message details such as user id, message contents, etc.
        context: Context object

    Returns:
        None
    """
    user_id = update.message.from_user.id

    # choose 2nd largest photo size (600 x 800) to reduce cost
    photo_id = update.message.photo[-2].file_id

    # get photo URL file path
    file = await context.bot.get_file(photo_id)
    image_url = file.file_path
    # print(image_url)

    if update.message.caption == None:
        # default prompt
        prompt = "describe the contents of this photo."
    else:
        prompt = update.message.caption

    # check if user_id of this message is a new user
    is_new_user, idx = isNewUser(user_id)

    if is_new_user == True or users_chat_history[idx]["model"] == "none":
        await update.message.reply_text("Please choose a model before we begin.")
        await choice_command(update, context)
    else:
        if users_chat_history[idx]["model"] != model["GPT-4V"]:
            await update.message.reply_text("switching to GPT-4V model...")
            users_chat_history[idx]["model"] = model["GPT-4V"]
            users_chat_history[idx]["instance"].model = model["GPT-4V"]

        response = users_chat_history[0]["instance"].handle_response_with_image(
            prompt, image_url)
        # await context.bot.sendChatAction(
        #     chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING
        # )
        await update.message.reply_text(response)


if __name__ == "__main__":
    print("Bot started...")
    app = Application.builder().token(TELE_API_KEY).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("choice", choice_command))
    app.add_handler(CommandHandler("get", get_choice_command))
    app.add_handler(CallbackQueryHandler(callback_button_handler))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message_with_photo))

    # Errors
    app.add_error_handler(error)

    # polling
    print("Running...")
    app.run_polling()
