import openai, os
from dotenv import load_dotenv, find_dotenv

# Get API tokens from environment file
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_TOKEN')

class ChatGPT:
    def __init__(self, model="gpt-3.5-turbo") -> None:
        print("chatGPT initialized.")
        self._name = "chatGPT-3.5"
        self._model = model
        self._messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]


    # a getter function
    @property
    def name(self) -> str:
        return self._name    

    def clear_messages(self):
        self._messages.clear()
        self._messages.append({"role": "system", "content": "You are a helpful assistant."})

    def handle_response(self, prompt: str) -> str:
        """Retain user messages and append assistant's responses in a message list.
        This is due to the model does not store chat history after each query is sent.
        
        prompt: user input message
        return: string response from model
        
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
        self._messages.append({"role":"assistant", "content":f"{response}"})

        # return assistant's response
        return response.choices[0].message["content"]
