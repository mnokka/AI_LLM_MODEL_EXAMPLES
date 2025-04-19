import ollama
import argparse
import sys

MODEL = "llama3.2:1b"  # for weak machines

def main():
    parser = argparse.ArgumentParser(
        description="Ask a question from local LLaMA model via Ollama.",
        usage="python ask_llama.py --question 'What is Python?'"
    )
    parser.add_argument(
        "--question",
        type=str,
        help="The question to ask the LLaMA model"
    )
    
    args = parser.parse_args()

    if not args.question:
        parser.print_help()
        sys.exit(1)

    messages = [{"role": "user", "content": args.question}]
    
    print(f"Using model: {MODEL}")
    print(f"Asking: {args.question}")
    print("Waiting for response...\n")

    response = ollama.chat(model=MODEL, messages=messages)
    print("=== Response ===\n")
    print(response['message']['content'])

if __name__ == "__main__":
    main()
