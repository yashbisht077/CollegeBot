# 🎓 AlphaMind — GEHU Bhimtal Campus Assistant

![preview](https://github.com/yashbisht077/CollegeBot/blob/main/Photo.png?raw=true)

**AlphaMind** is an offline, fast, campus-specific AI assistant built using **LLaMA 3.2** (via `llama.cpp` or `Ollama`), local vector search with FAISS, and a lightweight **Gradio** web app or Android app interface.  
It provides students, faculty, and visitors with instant answers about **Graphic Era Hill University, Bhimtal Campus**.

---

## 📽️ Preview Video
[![Watch the demo](https://github.com/yashbisht077/CollegeBot/blob/main/SrBanner.png?raw=true)](https://github.com/yashbisht077/CollegeBot/blob/main/sr.mp4)

---

## ⚙️ Features

- 🔍 Context-aware retrieval with FAISS and Sentence Transformers
- 💬 Conversational memory (short-term + long-term)
- 🧠 Learns new facts during chat (`remember that ...`)
- 💻 100% offline — no API or internet required
- 🧠 LLaMA 3.2 via `llama.cpp` (desktop) or `Ollama` (mobile)
- 🎙️ Voice-based input/output for Android version
- 🌐 Web interface via Gradio (desktop) or native mobile UI

---

## 📂 Project Structure

```
CollegeBot/
├── college_data/         # All organized text files for RAG (brochures, faculty, placements, etc.)
├── memory.txt            # Learned facts (persistent)
├── chats/                # Saved conversations per session
├── models/               # GGUF models (e.g., Llama-3.2-3B-Instruct-Q4_K_M.gguf)
├── llama.cpp/            # llama.cpp C++ inference engine (for desktop use)
├── temp.py               # Main Gradio chat app (desktop UI)
├── android_app/          # Kotlin Jetpack Compose app (mobile)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧪 Installation (Desktop Version)

```bash
git clone https://github.com/your-username/CollegeBot.git
cd CollegeBot

# Setup virtual environment
python -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate on Windows

# Install Python dependencies
pip install -r requirements.txt
```

---

## 🏗️ llama.cpp Setup

```bash
cd llama.cpp
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

Your model path should look like:
```
models/Llama-3.2-3B-Instruct-Q4_K_M.gguf
```

---

## 🚀 Run the Assistant

```bash
python temp.py
```

Access it at: http://localhost:7860

Use `share=True` in `.launch()` to generate a public demo link.

---

## 📦 Requirements

See [requirements.txt](https://github.com/yashbisht077/CollegeBot/blob/main/requirements.txt)

---

## 📲 Android Voice Assistant Version

### 🔧 Core Highlights

- 🎙️ Hindi or English voice input (via SpeechRecognizer API)
- 🗣️ TTS with:
  - English: Coqui TTS
  - Hindi: kokoro.KPipeline (Devanagari only)
- 👄 Animated avatar (Lottie) that lip-syncs with TTS
- ⚡ Fast response time (~1.5s)
- 📁 Persistent memory with FAISS + MiniLM

### 🔀 Workflow

```
Startup → Language Select (hi/en)
   → Accept Voice → Translate (if needed)
     → LLaMA 3.2 (Ollama)
       → Translate Back (if Hindi)
         → TTS Speak + Lottie Avatar
```

---

## 🔁 RAG System

- FAISS + `sentence-transformers/all-MiniLM-L6-v2`
- Custom prompt injects relevant passages
- Retrieval from structured campus data files

---

## 🧠 Memory

- Learns on-the-fly: `"remember that the placement head is Mr. Sharma"`
- Stored in `memory.txt`, survives app restarts
- Used for resolving pronouns and personal facts

---

## 💡 Résumé Highlights

```latex
\resumeItem{Built Bilingual Assistant}{Created offline assistant using LLaMA 3.2 via Ollama for Hindi-English college queries.}
\resumeItem{Integrated RAG Pipeline}{Used FAISS and MiniLM-L6-v2 for efficient context-aware retrieval over college data.}
\resumeItem{Enabled Voice Interaction}{Added voice input and TTS with real-time lip-sync Lottie animation.}
\resumeItem{Dynamic Learning}{Enabled persistent memory for learning without retraining.}
\resumeItem{Optimized Performance}{Achieved ~1.5s response time using caching and model tuning.}
```

---

## 📄 GitHub Description

**Title:** AlphaMind: GEHU Bhimtal Campus Assistant (Offline AI Chatbot)

**Short Description:**  
An offline AI chatbot built using LLaMA 3.2, FAISS, and Gradio/Android. Responds to Hindi and English queries with real-time voice interaction and persistent memory for the GEHU Bhimtal campus.

---

## 📝 Blog Outline

**Title:** How We Built an Offline, Bilingual College Assistant Using LLaMA 3.2 and FAISS

### Sections:
1. Why Offline? Why Bilingual?
2. LLaMA 3.2 + llama.cpp vs Ollama
3. College Data → FAISS → Retrieval
4. Hindi ↔ English Translation Logic
5. Speech and Lip Sync (Android)
6. Persistent Learning with Memory.txt
7. Challenges & Fixes (STT, Hinglish, Memory)
8. Final Results and Benchmarks

---

## 📣 Social Post Ideas

> Introducing **AlphaMind**: a 100% offline bilingual campus assistant for GEHU Bhimtal. Built with LLaMA 3.2, FAISS, and Kotlin — it talks, learns, and responds instantly in Hindi or English.

> From brochures to placement queries — AlphaMind answers it all. No internet, no delay. Voice in, voice out. 🎙️

> Avatar + TTS + RAG + Memory — everything offline. Try it now.

---

## 🙋 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📜 License

MIT License © 2025 Shankar Singh

---