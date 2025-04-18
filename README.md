# AI_LLM_MODEL_EXAMPLES

📚 Examples of using local LLMs (LLaMA via Ollama) on low-end computers without GPU



## ⚙️ Tech Stack

- **Language Model**: LLaMA 3.2 1B (via [Ollama](https://ollama.com/))  
- **Hardware**: Runs locally on a Lenovo ThinkCentre M710q  
  _(Intel Core i5-7400T, 4 cores, 25 GB RAM, no GPU)_  
> Chosen LLM is lightweight and fast, suitable for low-end machines.

---
## 🛠️ Installation (Linux)

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Download the model

```bash
ollama run llama3.2:1b
```

### 3. Clone the repository and install Python dependencies

```bash
git https://github.com/mnokka/AI_LLM_MODEL_EXAMPLES
cd AI_LLM_MODEL_EXAMPLES
pip install -r requirements.txt
```

---


# 💡 Examples

| File | Description |
|------|-------------|
| [`llamaHttps.py`](./llamaHttps.py) | Uses `requests` to interact with the local Ollama server. Example: fetches Finnish Independence Day info. |
| [`llamaLibrary.py`](./llamaLibrary.py) | Uses the `ollama` Python library directly. Same task as above, but using the higher-level library interface. |
| [`brochuregen.py`](./brochuregen.py) | Improved course example, includes web page summary data including data from links. Provides brochery of this web page |
| [`brochure.py`](./brochure.py) | Same task as above, but simpler version with several development steps left into code. |
