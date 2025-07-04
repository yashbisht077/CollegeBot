import os
import re
import subprocess
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_PATH = "./embedding_models/all-MiniLM-L6-v2"
HISTORY_DEPTH = 1

# ----------------------------
# Memory & Document Loading
# ----------------------------

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

# ----------------------------
# Initialize
# ----------------------------

os.environ["TOKENIZERS_PARALLELISM"] = "false"
print("[INFO] Loading embedding model...")
embed_model = SentenceTransformer(EMBED_MODEL_PATH)

print("[INFO] Loading documents and memory...")
documents = load_documents() + load_memory()
print(f"[INFO] Loaded {len(documents)} chunks.")

print("[INFO] Embedding and indexing...")
embeddings = embed_model.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# ----------------------------
# Context + Chat Handling
# ----------------------------

chat_history = []
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("chats", exist_ok=True)
chat_file_path = f"chats/chat_{timestamp}.txt"

def log_chat_to_file(user, bot):
    with open(chat_file_path, "a", encoding="utf-8") as f:
        f.write(f"User: {user}\nBot: {bot}\n\n")

def format_history():
    return "\n".join([
        f"User: {turn['user']}\nBot: {turn['bot']}"
        for turn in chat_history[-HISTORY_DEPTH:]
    ])

def get_last_mentioned_entity():
    # Try to get name from last bot response
    for turn in reversed(chat_history):
        match = re.search(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', turn["bot"])
        if match:
            return match.group(0)

    # Fallback: get any name from memory
    memory = load_memory()
    for line in reversed(memory):
        match = re.search(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', line)
        if match:
            return match.group(0)

    return None


def resolve_pronouns(query):
    pronouns = ["he", "she", "they", "him", "her", "them", "his", "their"]
    tokens = query.lower().split()
    if any(p in tokens for p in pronouns):
        entity = get_last_mentioned_entity()
        if entity:
            for p in pronouns:
                query = re.sub(rf"\b{p}\b", entity, query, flags=re.IGNORECASE)
    return query

def retrieve_context(query, k=3):
    # First: if the query mentions a known name, pull it directly from memory
    memory = load_memory()
    for mem_line in memory:
        name_match = re.findall(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", mem_line)
        for name in name_match:
            if name.lower() in query.lower():
                print(f"[DEBUG] Exact name match from memory: {name}")
                return mem_line

    # Second: fallback to word overlap in memory
    memory_matches = [line for line in memory if any(word.lower() in line.lower() for word in query.split())]
    if memory_matches:
        print(f"[DEBUG] Fuzzy memory match found: {memory_matches}")
        return "\n".join(memory_matches)

    # Last resort: vector search
    query_vec = embed_model.encode([query], normalize_embeddings=True)
    D, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def build_prompt(query, context):
    return f"""You are a helpful college assistant at Graphic Era Hill University, Bhimtal Campus.

📌 Communication Guidelines:
"tone": "friendly"
"tone": "talkative"
"tone": "Humorous"
You are AlphaMind
- Keep replies short and natural — 1–2 sentences unless the user asks for more.
- Respond conversationally like a human would. No robotic lines, no forced greetings.
- Never assume anything about the user — only respond based on known facts or previous context.
- Do not make up information.

Conversation History:
{format_history()}

Context:
{context}

User: {query}
Answer:"""

def ask_llama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=30
        )
        if result.returncode != 0:
            print("[ERROR] Ollama CLI error:", result.stderr.decode("utf-8").strip())
            return "[ERROR] Ollama model failed."
        response = result.stdout.decode("utf-8").strip()
        if not response:
            return "[ERROR] Ollama returned empty response."
        return response
    except subprocess.TimeoutExpired:
        return "[ERROR] Ollama call timed out."
    except Exception as e:
        return f"[ERROR] Exception: {e}"

# ----------------------------
# Main Chat Loop
# ----------------------------

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

    resolved_query = resolve_pronouns(query)
    context = retrieve_context(resolved_query)
    prompt = build_prompt(resolved_query, context)
    answer = ask_llama(prompt)

    print(f"\n🤖 CollegeBot: {answer}")
    chat_history.append({"user": query, "bot": answer})
    log_chat_to_file(query, answer)
