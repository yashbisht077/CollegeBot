import os
import subprocess
import time
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
import faiss

# Config
DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_PATH = "./embedding_models/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"
CPP_EXECUTABLE = "llama.cpp/build/bin/llama-run"
CPP_MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MAX_TOKENS = 200

# Questions to benchmark
queries = [
    "What are the hostel facilities at GEHU Bhimtal?",
    "Who is the dean of the computer science department?",
    "Can you list some clubs available on campus?",
    "Tell me about the placement statistics.",
    "What are the library timings?",
    "Does GEHU Bhimtal offer scholarships?"
]

# Load documents and build index
def load_documents():
    docs = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    docs.extend([chunk.strip() for chunk in text.split("\n\n") if chunk.strip()])
    return docs

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

embed_model = SentenceTransformer(EMBED_MODEL_PATH)
documents = load_documents() + load_memory()
embeddings = embed_model.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

def retrieve_context(query, k=3):
    vec = embed_model.encode([query], normalize_embeddings=True)
    D, I = index.search(vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def build_prompt(query, context):
    return f"""You are a helpful college assistant at Graphic Era Hill University, Bhimtal Campus.

Tone: friendly, talkative, humorous
You are AlphaMind

Context:
{context}

User: {query}
Answer:"""

def measure_response_time(prompt, command):
    start = time.time()
    subprocess.run(command, input=prompt.encode("utf-8"), capture_output=True)
    return time.time() - start

# Store response times
ollama_times = []
cpp_times = []

for query in queries:
    context = retrieve_context(query)
    prompt = build_prompt(query, context)

    # Ollama
    ollama_command = ["ollama", "run", OLLAMA_MODEL]
    t1 = measure_response_time(prompt, ollama_command)
    ollama_times.append(t1)

    # llama.cpp
    cpp_command = [CPP_EXECUTABLE, CPP_MODEL_PATH, prompt, f"--n-predict={MAX_TOKENS}"]
    t2 = measure_response_time(prompt, cpp_command)
    cpp_times.append(t2)

# Plot results
x_labels = [f"Q{i+1}" for i in range(len(queries))]

plt.figure(figsize=(10, 5))
plt.plot(x_labels, ollama_times, label="Ollama (CLI)", marker="o")
plt.plot(x_labels, cpp_times, label="llama.cpp", marker="x")
plt.ylabel("Response Time (s)")
plt.title("Ollama vs llama.cpp: Response Time Comparison")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
