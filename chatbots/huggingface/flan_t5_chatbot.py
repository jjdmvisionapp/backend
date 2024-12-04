import requests
from flask import Flask

from chatbots.chatbot_controller import ChatBotController


class FlanT5ChatBot(ChatBotController):

    def __init__(self, flask_app: Flask):
        self.huggingface_token = flask_app.config["HUGGINGFACE"]
        self.api_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
        self.request_headers = {"Authorization": "Bearer %s" % self.huggingface_token}

    def ask_chatbot(self, message) -> str:
        prompt = {
            "inputs": message
        }
        response = requests.post(self.api_url, headers=self.request_headers, json=prompt).json()
        return response[0].get('generated_text', "Sorry, I couldn't generate a proper response.")