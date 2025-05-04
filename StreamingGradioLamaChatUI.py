import gradio as gr
import ollama

MODEL = "llama3.2:1b"  # tai "llama3:1b" jos kone on kevyt

###############################################################################

def chat_with_local_llama(message, chat_history):
    # chat_history sisältää OpenAI-tyylisiä dict-viestejä kun type='messages'
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = ollama.chat(model=MODEL, messages=messages)
    reply = response["message"]["content"]

    return reply

##############################################################################

def stream_llama_reply(message, chat_history):
    messages = chat_history + [{"role": "user", "content": message}]
    
    full_reply = ""
    # Oletetaan että ollama.chat tukee stream-parametria
    for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
        token = chunk["message"]["content"]
        full_reply += token
        yield full_reply  # Tämä antaa välittömän osavastauksen Gradiolle


###############################################################################

chat_ui = gr.ChatInterface(
    fn=stream_llama_reply,
    title="💬 Chat with local AI, no internet needed",
    description=f"Used model`{MODEL}` locally via Ollama. For weak machine without GPUs",
    chatbot=gr.Chatbot(type="messages"),
    textbox=gr.Textbox(placeholder="Ask something...")
)

###############################################################################

if __name__ == "__main__":
    chat_ui.launch(share=True)
