# 🎓 AlphaMind — GEHU Bhimtal Campus Assistant
![preview](https://github.com/yashbisht077/CollegeBot/blob/main/Photo.png?raw=true)
**AlphaMind** is an offline, fast, campus-specific AI assistant built using LLaMA 3.2 (via `llama.cpp`), local vector search with FAISS, and a lightweight Gradio web app interface.  
It provides students, faculty, and visitors with instant answers about **Graphic Era Hill University, Bhimtal Campus**.

---

## ⚙️ Features

- 🔍 Context-aware retrieval with FAISS and Sentence Transformers
- 💬 Conversational memory (short-term + long-term)
- 🧠 Learns new facts during chat (`remember that ...`)
- 💻 100% offline — no API or internet required
- 🚀 Fast C++ backend with `llama.cpp`
- 🌐 Web interface via Gradio (easy to host or demo)

---


## 📂 Project Structure


```
CollegeBot/
├── college_data/         # All organized text files for RAG (brochures, faculty, placements, etc.)
├── memory.txt            # Learned facts (persistent)
├── chats/                # Saved conversations per session
├── models/               # GGUF models (e.g., Llama-3.2-3B-Instruct-Q4_K_M.gguf)
├── llama.cpp/            # llama.cpp C++ inference engine
├── temp.py               # Main Gradio chat app
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧪 Installation

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

```
cd llama.cpp
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

Your model path should look like:
models/Llama-3.2-3B-Instruct-Q4_K_M.gguf

---

## 🚀 Run the Assistant

```
python temp.py
```

Access it at: http://localhost:7860

Use share=True in .launch() to generate a public demo link.

---

## 📦 Requirements

See [requirements.txt](https://github.com/yashbisht077/CollegeBot/blob/main/requirements.txt)

---

## 🙋 Contributing

Pull requests are welcome! For major changes, please open an issue first.


## 📜 License

MIT License © 2025 Shankar Singh