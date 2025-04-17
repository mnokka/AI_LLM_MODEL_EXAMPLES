# local llama model used directly via ollama Python library


import ollama

# model needs to be run in Linux as: ollama run llama3.2:1b
MODEL = "llama3.2:1b" # for weak machines

messages = [
    {"role": "user", "content": "Find Finnish national holidays. Tell web site addresses where info found"},
    {"role": "user", "content": "Tell me about Finnish Independence Day."}
]

print (f"Using model:{MODEL}")
for message in messages:
    print(f"Role: {message['role']}, Content: {message['content']}")
print (f"Starting working............")

response = ollama.chat(model=MODEL, messages=messages)
print(response['message']['content'])