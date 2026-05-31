# 🏥 Healthcare AI Assistant

An AI-powered healthcare application that converts complex clinical discharge notes into patient-friendly summaries using Grok AI.

Built with Streamlit, OCR, PDF Processing, and Grok API.

---

## 🚀 Features

### 📄 Clinical Note Processing

* Paste discharge notes manually
* Upload PDF discharge reports
* Upload medical document images
* Capture documents using device camera

### 🤖 AI Summary Generation

* Converts complex medical language into simple patient-friendly language
* Maintains medical accuracy
* Highlights:

  * Reason for Hospital Stay
  * Medications
  * Home Care Instructions
  * Follow-Up Appointments
  * Warning Signs

### 🔍 OCR Support

* Extract text from scanned documents
* Read uploaded images
* Read camera-captured documents

### 📥 PDF Export

* Download generated summaries as PDF
* Easy sharing with patients and caregivers

### 🏥 Professional Dashboard

* Modern healthcare UI
* Safety panel
* AI confidence indicator
* Responsive layout

---

## 🛠 Tech Stack

| Technology  | Purpose               |
| ----------- | --------------------- |
| Streamlit   | Frontend Dashboard    |
| Grok API    | AI Summary Generation |
| PyPDF       | PDF Processing        |
| Pytesseract | OCR                   |
| Pillow      | Image Handling        |
| ReportLab   | PDF Export            |

---

## 📂 Project Structure

```text
healthcare-ai-assistant/
│
├── app.py
├── requirements.txt
├── README.md
└── assets/
```

---

## ⚙ Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/healthcare-ai-assistant.git

cd healthcare-ai-assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶ Run Application

```bash
streamlit run app.py
```

Application will open at:

```text
http://localhost:8501
```

---

## 🔑 Grok API Setup

Get your API key from xAI Console.

Add your API key inside the application sidebar when running locally.

For production deployment use Streamlit Secrets.

Example:

```toml
GROK_API_KEY="YOUR_API_KEY"
```

---

## ☁ Deploy on Streamlit Cloud

### Step 1

Push code to GitHub.

```bash
git add .
git commit -m "Initial Commit"
git push origin main
```

### Step 2

Open Streamlit Community Cloud.

### Step 3

Connect GitHub account.

### Step 4

Select Repository.

### Step 5

Choose:

```text
Main File:
app.py
```

### Step 6

Click Deploy.

---

## 📸 Application Workflow

```text
PDF / Image / Camera Input
            ↓
      OCR Extraction
            ↓
      Clinical Notes
            ↓
         Grok AI
            ↓
 Patient-Friendly Summary
            ↓
      PDF Download
```

---

## ⚠ Medical Disclaimer

This application is intended for educational and communication assistance purposes only.

AI-generated summaries must always be reviewed by qualified healthcare professionals before being provided to patients.

The system does not provide diagnoses, treatment recommendations, or medical advice.

---

## 👨‍💻 Author

Ravi Prajapati

Healthcare AI Assistant Project
Built with Streamlit + Grok AI
