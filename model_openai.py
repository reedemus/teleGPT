import openai
import os
from dotenv import load_dotenv, find_dotenv

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_TOKEN")


class ChatGPT:
    """chatGPT class"""

    def __init__(self, model="gpt-3.5-turbo") -> None:
        print("chatGPT initialized.")
        self._name = "chatGPT-3.5"
        self._model = model
        self._message = [{"role": "system", "content": "You are a helpful assistant."}]

    # a getter function
    @property
    def name(self):
        """Returns name of llm model

        Args:
            None

        Returns:
            string
        """
        return self._name

    # setter function
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def message(self):
        """Return all prompts

        Args:
            None

        Returns:
            list of dictionaries
        """
        return self._message

    # setter function
    @message.setter
    def message(self, msg):
        self._message = msg

    def clear_messages(self, user_id: int) -> None:
        """Clear message list"""
        self._message.clear()
        self._message.append(
            {"role": "system", "content": "You are a helpful assistant."}
        )

    def handle_response(self, prompt: str) -> list:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.

        Args:
            prompt: user input message

        Returns:
            list of dict of prompts

        TODO:
         1) use moderation API to detect hate speech and adhere to safety guidelines
         2) prevent prompt injection attacks
        """
        # retrieve user's message list
        conversation = self._message.append({"role": "user", "content": f"{prompt}"})
        response = openai.ChatCompletion.create(
            model=self._model,
            messages=conversation,
            temperature=0,
        )
        resp = response.choices[0].message["content"]
        conversation.append({"role": "assistant", "content": f"{resp}"})
        return conversation
