import os
import subprocess
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
LLAMA_RUN = "llama.cpp/build/bin/llama-run"
MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MAX_TOKENS = 200
HISTORY_DEPTH = 3

def load_documents(path=DATA_DIR):
    docs = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
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

os.environ["TOKENIZERS_PARALLELISM"] = "false"
print("[INFO] Loading embedding model...")
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

print("[INFO] Loading documents...")
documents = load_documents() + load_memory()
print(f"[INFO] Loaded {len(documents)} chunks.")

print("[INFO] Embedding and indexing...")
embeddings = embed_model.encode(documents)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

def retrieve_context(query, k=3):
    query_vec = embed_model.encode([query])
    D, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def ask_llama(prompt):
    result = subprocess.run(
        [LLAMA_RUN, MODEL_PATH, prompt, f"--n-predict={MAX_TOKENS}"],
        capture_output=True
    )
    return result.stdout.decode("utf-8").strip()

chat_history = []

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
chat_file_path = f"chats/chat_{timestamp}.txt"

def log_chat_to_file(user, bot):
    with open(chat_file_path, "a", encoding="utf-8") as f:
        f.write(f"User: {user}\nBot: {bot}\n\n")

def format_history():
    return "\n".join([
        f"User: {turn['user']}\nBot: {turn['bot']}"
        for turn in chat_history[-HISTORY_DEPTH:]
    ])

def build_prompt(query, context):
    return f"""You are AlphaMind, the official assistant for Graphic Era Hill University, Bhimtal Campus.
Only mention your name if the user asks for it explicitly.

Respond clearly and concisely. Do not make up information.

Your job is to:
- Answer clearly in 1–2 sentences unless asked for a detailed response
- Respond kindly to casual replies like \"hi\" or \"good to hear\" without repeating yourself
- If the user says \"Do you know me?\" or \"You know who I am?\", say you don't know unless they've told you earlier — and do not assume conversation is interrupted
- Never say \"Let's start fresh\" or \"message was interrupted\" unless explicitly told
- Stay focused on college-related information but be friendly in tone

Conversation History:
{format_history()}

Context:
{context}

User: {query}
Answer:"""

print("\n🤖 CollegeBot is ready. Type 'exit' to quit.")
while True:
    query = input("\n🧑 You: ")
    if query.lower() == "exit":
        break

    if query.lower().startswith(("remember that", "learn that")):
        fact = query.partition("that")[2].strip()
        if fact:
            save_memory_line(fact)
            print(f"\nAlphaMind: Got it! I’ll remember: {fact}")
        else:
            print("\nPlease provide a fact after 'remember that'")
        continue

    context = retrieve_context(query)
    prompt = build_prompt(query, context)
    answer = ask_llama(prompt)

    print(f"\n🤖 CollegeBot: {answer}")
    chat_history.append({"user": query, "bot": answer})
    log_chat_to_file(query, answer)
