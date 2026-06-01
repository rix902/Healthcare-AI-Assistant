# 🏥 MedClear – Healthcare AI Assistant

> Transform complex medical reports into clear, patient-friendly summaries using AI.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 PDF Upload | Extract text from discharge summaries, lab reports |
| 🖼 Image / OCR | EasyOCR on scanned documents, prescriptions, X-ray reports |
| 📷 Camera Capture | Live document scanning from device camera |
| ✏️ Manual Input | Paste clinical text directly |
| 🤖 AI Summary | Groq + Llama 3.1 converts clinical language to plain language |
| 🌐 Multilingual | English, Hindi, Kannada, Tamil, Telugu |
| 💬 Medical Chat | Ask questions answered only from your document |
| ⬇️ PDF Export | Download patient-friendly summary as formatted PDF |
| 🛡 Safety Layer | AI never invents medical data; warns before patient use |

---

## 🚀 Quick Start

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/medclear-healthcare-ai.git
cd medclear-healthcare-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Groq API key
export GROQ_API_KEY="gsk_your_key_here"

# 4. Run the app
streamlit run app.py
```

### Get a Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Create an API key under **API Keys**
4. Paste it into the sidebar when the app loads

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your GitHub repo
4. Set **Main file path**: `app.py`
5. Under **Advanced settings → Secrets**, add:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

6. Click **Deploy** 🚀

---

## 📁 Project Structure

```
medclear-healthcare-ai/
├── app.py                  # Main Streamlit application
├── style.css               # Custom healthcare-themed CSS
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme & server config
└── README.md
```

---

## 🏗 Technical Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Groq API · Llama 3.1 8B Instant |
| OCR | EasyOCR |
| PDF Reading | PyPDF |
| PDF Generation | ReportLab |
| Image Processing | Pillow + NumPy |

---

## ⚠️ Safety & Disclaimer

- This application is for **assistive purposes only**
- AI summaries are based **solely on the uploaded document**
- No medical information is invented or assumed
- All summaries must be **reviewed by a qualified healthcare professional** before patient use
- Not a substitute for professional medical advice, diagnosis, or treatment

---

## 📄 License

MIT License – see [LICENSE](LICENSE)
