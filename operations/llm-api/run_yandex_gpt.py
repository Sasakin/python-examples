import requests
import os

def generate_text(prompt):
    api_key = os.environ["API_KEY"]
    response = requests.post("https://api.yandexcloud.net/v1/generations", json={
        "task": {
            "generation_type": "text",
            "model_id": "YandexGPT",
            "input": prompt
        },
        "parameters": {
            "api_key": api_key
        }
    })

    return response.json()["generation"]

if __name__ == "__main__":
    prompt = "Привет, как у тебя дела?"
    print(generate_text(prompt))