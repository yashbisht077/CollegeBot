import gradio as gr
import os
import faiss
import subprocess
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer

DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
LLAMA_RUN = "llama.cpp/build/bin/llama-run"
MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MAX_TOKENS = 200
HISTORY_DEPTH = 3

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    docs = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    chunks = text.split("\n\n")
                    docs.extend([chunk.strip() for chunk in chunks if chunk.strip()])
    return docs

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_memory_line(line):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(line.strip() + "\n")

documents = load_documents() + load_memory()
embeddings = embed_model.encode(documents)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

chat_history = []
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
chat_file_path = f"chats/chat_{timestamp}.txt"

def log_chat_to_file(user, bot):
    with open(chat_file_path, "a", encoding="utf-8") as f:
        f.write(f"User: {user}\nBot: {bot}\n\n")

def format_history():
    return "\n".join([
        f"User: {h['user']}\nBot: {h['bot']}"
        for h in chat_history[-HISTORY_DEPTH:]
    ])

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def ask_llama(prompt):
    result = subprocess.run(
        [LLAMA_RUN, MODEL_PATH, prompt, f"--n-predict={MAX_TOKENS}"],
        capture_output=True
    )
    raw_output = result.stdout.decode("utf-8").strip()
    return ansi_escape.sub("", raw_output) 

def retrieve_context(query, k=3):
    query_vec = embed_model.encode([query])
    D, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def build_prompt(query, context):
    return f"""You are AlphaMind, the official assistant for Graphic Era Hill University, Bhimtal Campus.
Only mention your name if the user asks for it explicitly.

Respond clearly and concisely. Do not make up information.

Your job:
- Answer concisely (1–2 sentences unless asked)
- Be polite, relevant, and don't assume identity unless taught

Conversation History:
{format_history()}

Context:
{context}

User: {query}
Answer:"""

def chat(user_input, history):
    if user_input.lower().startswith(("remember that", "learn that")):
        fact = user_input.partition("that")[2].strip()
        if fact:
            save_memory_line(fact)
            reply = f"Learned and saved: {fact}"
        else:
            reply = "Please provide a fact after 'remember that'"
        return {"role": "assistant", "content": reply}

    context = retrieve_context(user_input)
    prompt = build_prompt(user_input, context)
    response = ask_llama(prompt)

    chat_history.append({"user": user_input, "bot": response})
    log_chat_to_file(user_input, response)

    return {"role": "assistant", "content": response}

gr.ChatInterface(
    fn=chat,
    title="🎓 AlphaMind | GEHU Bhimtal Assistant",
    chatbot=gr.Chatbot(type="messages")
).launch(share=True)