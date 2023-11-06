# TeleGPT
![python-version](https://img.shields.io/badge/python-3.9-blue.svg)
[![openai-version](https://img.shields.io/badge/openai-0.28.0-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-GPL%202.0-brightgreen.svg)](LICENSE)

A minimal [Telegram bot](https://core.telegram.org/bots/api) that integrates with OpenAI's [ChatGPT](https://openai.com/blog/chatgpt/) with minimal configuration required.

## Screenshots

### Demo
![demo](/demo/telegpt.png)


## Features
- [x] run locally using `main` branch, or
- [x] deploy to any online server as a Flask app using `telebot2` branch
- [ ] generate images using text prompt (coming soon!)


## Prerequisites
- Python 3.9+
- A [Telegram bot](https://core.telegram.org/bots#6-botfather) and its token (see [tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))
- An [OpenAI](https://openai.com) account (see [configuration](#configuration) section)

## Getting started

### Configuration
Customize the configuration by copying `.env.example` and renaming it to `.env`, then editing the required parameters as desired:

| Parameter                   | Description                                                                                                                                                  |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `OPENAI_API_TOKEN`          | Your OpenAI API key from [here](https://platform.openai.com/account/api-keys)                                                                                |
| `TELEGRAM_API_TOKEN`        | Your Telegram bot's token, obtained using [BotFather](http://t.me/botfather) (see [tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)) |
| `TELEGRAM_BOT_NAME`         | Your Telegram bot's name                                                                                                                                     |
| `PUBLIC_URL`                | Web service provider's URL for your app e.g. https://www.yourapp-heroku.com  (only for `telebot2` branch)                                                    |

### Installing
Clone the repository and navigate to the project directory:

```shell
git clone https://github.com/reedemus/teleGPT.git
cd teleGPT
```

#### From Source
1. Create a virtual environment:
```shell
python -m venv venv
```

2. Activate the virtual environment:
```shell
# For Linux or macOS:
source venv/bin/activate

# For Windows:
venv\Scripts\activate
```
To deploy bot online, skip to [Deploy to web host](#deploy-to-web-host) section.


#### Run locally on your PC
3. Install the dependencies using `requirements.txt` file:
```shell
pip install -r requirements.txt
```

4. Checkout `main` branch
```
git checkout main
```

5. Use the following command to start the bot:
```
python app.py
```


#### Deploy to web host
3. Install the dependencies using `requirements.txt` file:
```shell
pip install -r requirements.txt
```

4. Checkout `telebot2` branch
```
git checkout telebot2
```

5. Use the following command to start the bot
The bot is deployed as a Flask app with gunicorn wsgi server with the command below:
```
gunicorn wsgi:app
```


## Credits
- [ChatGPT](https://chat.openai.com/chat) from [OpenAI](https://openai.com)
- [python-telegram-bot](https://python-telegram-bot.org)


## Disclaimer
This is a personal project and is not affiliated with OpenAI or StabilityAI in any way.

## License
This project is released under the terms of the GPL 2.0 license. For more information, see the [LICENSE](LICENSE) file included in the repository.