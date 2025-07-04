import os
import subprocess
import faiss
import re
import numpy as np
import soundfile as sf
import simpleaudio as sa
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
from datetime import datetime
from TTS.api import TTS
from kokoro import KPipeline
from googletrans import Translator

# ---------------- Initial Language Preference ----------------
user_lang = input("\U0001F310 Select language (en/hi): ").strip().lower()
assert user_lang in ["en", "hi"], "Please choose either 'en' or 'hi'"

translator = Translator()

# ---------------- Text-to-Speech ----------------
tts_en = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
MALE_SPEAKER = "p233"
pipeline_hi = KPipeline(lang_code="hi")

def speak_en(text):
    tts_en.tts_to_file(text=text, speaker=MALE_SPEAKER, file_path="speech_en.wav")
    sa.WaveObject.from_wave_file("speech_en.wav").play().wait_done()

def split_text_hi(text):
    return [chunk.strip() for chunk in re.split(r'(?<=[।!?])\s*', text) if chunk.strip()]

def speak_hi(text):
    chunks = split_text_hi(text)
    audio_parts = []
    for chunk in chunks:
        for _, _, audio in pipeline_hi(chunk, voice="hm_omega", speed=1.3):
            if audio is not None:
                audio_parts.append(audio)
    if audio_parts:
        combined = np.concatenate(audio_parts)
        sf.write("speech_hi.wav", combined, samplerate=24000, subtype='PCM_16')
        sa.WaveObject.from_wave_file("speech_hi.wav").play().wait_done()

def speak(text):
    if user_lang == "hi":
        speak_hi(text)
    else:
        speak_en(text)

# ---------------- Speech Input ----------------
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\U0001F3A4 Speak now...")
        audio = recognizer.listen(source)
    try:
        lang_code = "hi-IN" if user_lang == "hi" else "en-US"
        return recognizer.recognize_google(audio, language=lang_code)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return ""

# ---------------- Config ----------------
DATA_DIR = "college_data"
MEMORY_FILE = "memory.txt"
EMBED_MODEL_PATH = "./embedding_models/all-MiniLM-L6-v2"
HISTORY_DEPTH = 1

# ---------------- Load Data ----------------
def load_documents():
    docs = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    for chunk in f.read().split("\n\n"):
                        if chunk.strip():
                            docs.append(chunk.strip())
    return docs

def load_memory():
    return [line.strip() for line in open(MEMORY_FILE, "r", encoding="utf-8")] if os.path.exists(MEMORY_FILE) else []

def save_memory_line(line):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(line.strip() + "\n")

# ---------------- Embedding ----------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"
print("[INFO] Loading embedding model...")
embed_model = SentenceTransformer(EMBED_MODEL_PATH)
documents = load_documents() + load_memory()
print(f"[INFO] Loaded {len(documents)} chunks.")
embeddings = embed_model.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# ---------------- LLM + Prompt ----------------
def retrieve_context(query, k=3):
    query_vec = embed_model.encode([query], normalize_embeddings=True)
    _, I = index.search(query_vec, k)
    return "\n---\n".join([documents[i] for i in I[0]])

def ask_llama(prompt):
    try:
        result = subprocess.run(["ollama", "run", "llama3.2"], input=prompt.encode("utf-8"),
                                capture_output=True, timeout=30)
        if result.returncode != 0:
            print("[ERROR] Ollama error:", result.stderr.decode())
            return "[ERROR] LLM failure."
        return result.stdout.decode().strip()
    except Exception as e:
        return f"[ERROR] Llama call failed: {e}"

def build_prompt(query, context):
    history = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in chat_history[-HISTORY_DEPTH:]])
    return f"""You are a helpful college assistant at Graphic Era Hill University, Bhimtal Campus.

📌 Communication Guidelines:
"tone": "friendly"
"tone": "talkative"
"tone": "Humorous"
You are AlphaMind.
- Keep replies short and natural — 1–2 sentences unless asked otherwise.
- Speak conversationally like a real person.
- Don't invent facts.

Conversation History:
{history}

Context:
{context}

User: {query}
Answer:"""

# ---------------- Chat Loop ----------------
chat_history = []
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("chats", exist_ok=True)
chat_log_path = f"chats/chat_{timestamp}.txt"

def log_chat(user, bot):
    with open(chat_log_path, "a", encoding="utf-8") as f:
        f.write(f"User: {user}\nBot: {bot}\n\n")

print("\n🤖 CollegeBot is ready with Speech Input. Type or say something! (Type 'exit' to quit)")
while True:
    user_input = input("\n🧑 You (type or press Enter to speak): ")
    if user_input.strip() == "":
        user_input = recognize_speech()
        print(f"🔊 You (from speech): {user_input}")

    if user_input.lower() == "exit":
        break

    if user_input.lower().startswith(("remember that", "learn that")):
        fact = user_input.partition("that")[2].strip()
        if fact:
            save_memory_line(fact)
            print("✅ Remembered.")
        else:
            print("⚠️ Please provide a fact after 'remember that'")
        continue

    if user_lang == "hi":
        translated_input = translator.translate(user_input, src="hi", dest="en").text
        context = retrieve_context(translated_input)
        prompt = build_prompt(translated_input, context)
        raw_reply = ask_llama(prompt)
        final_reply = translator.translate(raw_reply, src="en", dest="hi").text
    else:
        context = retrieve_context(user_input)
        prompt = build_prompt(user_input, context)
        raw_reply = ask_llama(prompt)
        final_reply = raw_reply

    print(f"\n🤖 CollegeBot: {final_reply}")
    speak(final_reply)
    chat_history.append({"user": user_input, "bot": raw_reply})
    log_chat(user_input, raw_reply)