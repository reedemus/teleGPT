import openai
import os
from dotenv import load_dotenv, find_dotenv
from enum import Enum

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_TOKEN")


class UserEnum(Enum):
    UNKNOWN_USER = 0


class ChatGPT:
    """chatGPT class"""

    def __init__(self, model="gpt-3.5-turbo") -> None:
        print("chatGPT initialized.")
        self._name = "chatGPT-3.5"
        self._model = model
        self._chat_history = [
            {
                "user": UserEnum.UNKNOWN_USER,
                "message": [
                    {"role": "system", "content": "You are a helpful assistant."}
                ],
            }
        ]

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

    def clear_messages(self, user_id: int) -> None:
        """Clear message list"""
        conversation = self._get_chat_history(user_id)
        conversation.clear()
        conversation.append(
            {"role": "system", "content": "You are a helpful assistant."}
        )
        self._update_chat_history(user_id, conversation)

    def handle_response(self, user_id: int, prompt: str) -> str:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.

        Args:
            user_id: user id
            prompt: user input message

        Returns:
            response string

        TODO:
         1) use moderation API to detect hate speech and adhere to safety guidelines
         2) prevent prompt injection attacks
        """
        # retrieve user's message list
        conversation = self._get_chat_history(user_id)
        conversation.append({"role": "user", "content": f"{prompt}"})

        response = openai.ChatCompletion.create(
            model=self._model,
            messages=conversation,
            temperature=0,
        )
        resp = response.choices[0].message["content"]
        conversation.append({"role": "assistant", "content": f"{resp}"})
        # update the message list
        self._update_chat_history(user_id, conversation)
        return resp

    def _update_chat_history(self, user_id: int, user_messages: list) -> None:
        """Update chat history of the user"""
        found = False
        for idx, _ in enumerate(self._chat_history):
            if user_id == self._chat_history[idx]["user"]:
                found = True
                # shallow copy
                self._chat_history[idx]["message"] = user_messages
                break
        if not found:
            self._chat_history.append({"user": user_id, "message": user_messages})

    def _get_chat_history(self, user_id: int) -> list:
        """Returns the chat history of the user"""
        # Initialize message list for chatGPT model
        if self._chat_history[0]["user"] == UserEnum.UNKNOWN_USER:
            self._chat_history[0]["user"] = user_id
            messages = self._chat_history[0]["message"]
        else:
            found = False
            for idx, _ in enumerate(self._chat_history):
                if user_id == self._chat_history[idx]["user"]:
                    messages = self._chat_history[idx]["message"]
                    found = True
                    break
            if not found:
                # found a new user
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant.",
                    }
                ]
                self._chat_history.append({"user": user_id, "message": messages})
        return messages
