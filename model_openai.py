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
        self._messages = [{"role": "system", "content": "You are a helpful assistant."}]

    # a getter function
    @property
    def name(self) -> str:
        """Returns name of llm model

        Args:
            None

        Returns:
            string
        """
        return self._name

    def clear_messages(self) -> None:
        """Clear message list"""
        self._messages.clear()
        self._messages.append(
            {"role": "system", "content": "You are a helpful assistant."}
        )

    def handle_response(self, prompt: str) -> tuple:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.

        Args:
            prompt: user input message

        Returns:
            tuple: string response, message list

        TODO:
         1) use moderation API to detect hate speech and adhere to safety guidelines
         2) prevent prompt injection attacks
        """
        self._messages.append({"role": "user", "content": f"{prompt}"})
        response = openai.ChatCompletion.create(
            model=self._model,
            messages=self._messages,
            temperature=0,
        )
        resp = response.choices[0].message["content"]
        self._messages.append({"role": "assistant", "content": f"{resp}"})

        # return assistant's response and message list
        return (resp, self._messages)
