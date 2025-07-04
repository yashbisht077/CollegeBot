import os
import subprocess
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime
from langdetect import detect

def detect_language(text):
    try:
        return detect(text)  # returns 'hi' or 'en'
    except:
        return "en"  # default fallback


DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_PATH = "./embedding_models/all-MiniLM-L6-v2"
MAX_TOKENS = 200
HISTORY_DEPTH = 1

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
embed_model = SentenceTransformer(EMBED_MODEL_PATH)

print("[INFO] Loading documents...")
documents = load_documents() + load_memory()
print(f"[INFO] Loaded {len(documents)} chunks.")

print("[INFO] Embedding and indexing...")
embeddings = embed_model.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

def retrieve_context(query, k=3):
    query_vec = embed_model.encode([query], normalize_embeddings=True)
    D, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

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

def build_prompt(query, context, lang="en"):
    if lang == "hi":
        identity = "आप AlphaMind हैं, GEHU Bhimtal Campus के आधिकारिक सहायक।\nआपका उद्देश्य केवल GEHU Bhimtal से संबंधित जानकारी प्रदान करना है।"
        communication_guidelines = """📌 संवाद दिशानिर्देश:
"tone": "friendly"
"tone": "talkative"
"tone": "Humorous"
आप AlphaMind हैं
- उत्तर संक्षिप्त और प्राकृतिक रखें — 1–2 पंक्तियाँ जब तक कि उपयोगकर्ता अधिक न मांगे।
- मानव की तरह बातचीत करें, कोई रोबोटिक लाइन या जबरदस्ती अभिवादन न दें।
- उपयोगकर्ता के बारे में कभी अनुमान न लगाएं — केवल ज्ञात तथ्यों या संदर्भ के आधार पर उत्तर दें।
- जानकारी न बनाएँ।"""
    else:
        identity = "You are AlphaMind, the official assistant for GEHU Bhimtal Campus.\nYour job is to respond accurately to queries related to the campus."
        communication_guidelines = """📌 Communication Guidelines:
"tone": "friendly"
"tone": "talkative"
"tone": "Humorous"
You are AlphaMind
- Keep replies short and natural — 1–2 sentences unless the user asks for more.
- Respond conversationally like a human would. No robotic lines, no forced greetings.
- Never assume anything about the user — only respond based on known facts or previous context.
- Do not make up information."""

    return f"""{identity}

{communication_guidelines}

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
    lang = detect_language(query)

    if query.lower().startswith(("remember that", "learn that")):
        fact = query.partition("that")[2].strip()
        if fact:
            save_memory_line(fact)
            print(f"\nAlphaMind: Got it! I’ll remember: {fact}")
        else:
            print("\nPlease provide a fact after 'remember that'")
        continue

    context = retrieve_context(query)
    prompt = build_prompt(query, context, lang)
    answer = ask_llama(prompt)

    print(f"\n🤖 CollegeBot: {answer}")
    chat_history.append({"user": query, "bot": answer})
    log_chat_to_file(query, answer)
