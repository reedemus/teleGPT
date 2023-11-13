from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())


class ChatGPT:
    """chatGPT class"""

    def __init__(self, model="gpt-3.5-turbo") -> None:
        print("chatGPT initialized.")
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_TOKEN"))
        self._model = model
        self._message = [{"role": "system", "content": "You are a helpful assistant."}]

    # a getter function
    @property
    def model(self):
        """Returns name of llm model

        Args:
            None

        Returns:
            string
        """
        return self._model

    # setter function
    @model.setter
    def model(self, model):
        self._model = model

    def clear_messages(self) -> None:
        """Clear message list"""
        self._message.clear()
        self._message.append(
            {"role": "system", "content": "You are a helpful assistant."}
        )

    def handle_response(self, prompt: str) -> str:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.

        Args:
            prompt: user input message

        Returns:
            response string

        TODO:
        - prevent prompt injection attacks
        """
        # retrieve user's message list
        self._message.append({"role": "user", "content": f"{prompt}"})
        self._response = self._client.chat.completions.create(
            model=self._model,
            messages=self._message,
            temperature=0,
        )
        # resp = self._response.choices[0].message["content"]
        resp = self._response.choices[0].message.content
        self._message.append({"role": "assistant", "content": f"{resp}"})
        return resp

    def handle_response_with_image(self, prompt: str, image_url: str) -> str:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.

        Args:
            prompt: user input message
            image: base64-encoded image

        Returns:
            response string

        TODO:
        - prevent prompt injection attacks
        """
        # retrieve user's message list
        content = [
            {
                "type": "text",
                "text": str(prompt)
            },
            {
                "type": "image_url",
                "image_url": str(image_url)
            }
        ]
        self._message.append({"role": "user", "content": content})
        self._response = self._client.chat.completions.create(
            model=self._model,
            messages=self._message,
            temperature=0,
            max_tokens=400
        )
        resp = self._response.choices[0].message.content
        self._message.append({"role": "assistant", "content": f"{resp}"})
        return resp
