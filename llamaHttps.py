# local llama model used via request library usage

import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display


OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2:1b"


messages = [
    {"role": "user", "content": "Find Finnish national holidays. Tell web site addresses where info found"},
    {"role": "user", "content": "Tell me about Finnish Independence Day."}
]


payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }


print (f"Using model:{MODEL}")
for message in messages:
    print(f"Role: {message['role']}, Content: {message['content']}")
print (f"Starting working............")

response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
print(response.json()['message']['content'])