from flask import Flask, request, jsonify
from googletrans import Translator
from sentence_transformers import SentenceTransformer
from datetime import datetime
import faiss
import requests
import os

app = Flask(__name__)
translator = Translator()

# ---------------- Config ----------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"
DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_PATH = "./embedding_models/all-MiniLM-L6-v2"
HISTORY_DEPTH = 1

# ---------------- Chat History Setup ----------------
chat_history = []
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("chats", exist_ok=True)
chat_file_path = f"chats/chat_{timestamp}.txt"

def format_history():
    return "\n".join([
        f"User: {turn['user']}\nBot: {turn['bot']}"
        for turn in chat_history[-HISTORY_DEPTH:]
    ])

def log_chat_to_file(user, bot):
    with open(chat_file_path, "a", encoding="utf-8") as f:
        f.write(f"User: {user}\nBot: {bot}\n\n")

# ---------------- Load Documents ----------------
def load_documents():
    docs = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    for chunk in f.read().split("\n\n"):
                        if chunk.strip():
                            docs.append(chunk.strip())
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            docs += [line.strip() for line in f if line.strip()]
    return docs

print("[INFO] Loading embedding model and data...")
embed_model = SentenceTransformer(EMBED_MODEL_PATH)
documents = load_documents()
embeddings = embed_model.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
print(f"[INFO] {len(documents)} context documents loaded.")

# ---------------- Helper Functions ----------------
def translate_to_english(text):
    return translator.translate(text, src='hi', dest='en').text

def translate_to_hindi(text):
    return translator.translate(text, src='en', dest='hi').text

def retrieve_context(query, k=3):
    query_vec = embed_model.encode([query], normalize_embeddings=True)
    _, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def build_prompt(query, context):
    return f"""You are a helpful college assistant at Graphic Era Hill University, Bhimtal Campus.

📌 Communication Guidelines:
"tone": "friendly"
"tone": "talkative"
"tone": "humorous"
- Keep replies short and natural — 1–2 sentences unless asked otherwise.
- Speak conversationally like a real person.
- Don't invent facts.

Conversation History:
{format_history()}

Context:
{context}

User: {query}
Answer:"""

def query_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()

# ---------------- API Endpoint ----------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    user_lang = data.get("lang", "en")  # default to English if not provided

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Translate input to English if user is using Hindi mode
    if user_lang == 'hi':
        translated_input = translate_to_english(user_message)
    else:
        translated_input = user_message

    # Retrieve relevant college data
    context = retrieve_context(translated_input)
    prompt = build_prompt(translated_input, context)

    try:
        raw_reply = query_ollama(prompt)
    except Exception as e:
        return jsonify({"error": f"Ollama request failed: {str(e)}"}), 500

    # Translate reply back to Hindi if needed
    final_reply = translate_to_hindi(raw_reply) if user_lang == 'hi' else raw_reply

    # Save to history and log
    chat_history.append({"user": user_message, "bot": final_reply})
    log_chat_to_file(user_message, final_reply)

    return jsonify({"response": final_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)