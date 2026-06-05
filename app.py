import streamlit as st
import os
import io
import time
from PIL import Image
import numpy as np
import pytesseract

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedClear – Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── API key from Streamlit secrets only ───────────────────────────────────────
def get_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

# ── Groq client ───────────────────────────────────────────────────────────────
def get_groq_client():
    from groq import Groq
    key = get_api_key()
    return Groq(api_key=key) if key else None

# ── OCR – lazy load, graceful failure ─────────────────────────────────────────
def load_ocr():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception as e:
        st.error(f"OCR Error: {e}")
        return False


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # OCR accuracy improve
        image = image.convert("L")

        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--psm 6"
        )

        return text.strip()

    except Exception as e:
        st.error(f"Image OCR Error: {e}")
        return ""
# ── PDF extraction ────────────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception as e:
        st.error(f"PDF read error: {e}")
        return ""

# ── Language maps ─────────────────────────────────────────────────────────────
LANGUAGE_NAMES = {
    "English":  "English",
    "Hindi":    "Hindi (हिंदी)",
    "Kannada":  "Kannada (ಕನ್ನಡ)",
    "Tamil":    "Tamil (தமிழ்)",
    "Telugu":   "Telugu (తెలుగు)",
}

# ── Prompts ───────────────────────────────────────────────────────────────────
SUMMARY_SYSTEM = """You are MedClear, a compassionate medical communication AI.
Convert complex clinical text into easy-to-understand patient-friendly summaries.

STRICT RULES:
- Use ONLY information from the provided document. NEVER invent or assume anything.
- If a section has no data, write: "Not mentioned in the document."
- Always include the Safety Note at the end.
- Respond entirely in {language}.

OUTPUT FORMAT (use exactly these headers):

🩺 DIAGNOSIS
[Simple explanation of the condition(s)]

💊 MEDICATIONS
For each medicine:
- Name: [medicine name]
- Purpose: [what it treats]
- Instructions: [dosage / timing / special notes]

📅 FOLLOW-UP CARE
- Appointments: [dates/specialists]
- Tests: [required tests]
- Monitoring: [home monitoring requirements]

⚠️ WARNING SIGNS
[Symptoms requiring immediate medical attention]

🏠 HOME CARE INSTRUCTIONS
- Daily care: [guidance]
- Activity: [recommendations]
- Recovery tips: [advice]

🔒 SAFETY NOTE
This AI-generated summary is based solely on the uploaded document. It must be reviewed by a qualified healthcare professional before patient use.
"""

CHAT_SYSTEM = """You are MedClear, a helpful medical assistant.
Medical document on file:
---
{document}
---
RULES:
- Answer ONLY using the document above.
- If the answer is not there: "This information is not available in the provided document."
- Be clear, concise, and compassionate.
- Respond in {language}.
"""

def generate_summary(text: str, language: str) -> str:
    client = get_groq_client()
    if not client:
        return "⚠️ GROQ_API_KEY not configured. Add it to .streamlit/secrets.toml"
    system = SUMMARY_SYSTEM.replace("{language}", language)
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": f"Summarise this medical document:\n\n{text}"},
        ],
        temperature=0.3, max_tokens=2048,
    )
    return r.choices[0].message.content

def chat_with_document(messages: list, document: str, language: str) -> str:
    client = get_groq_client()
    if not client:
        return "⚠️ API key not configured."
    system = CHAT_SYSTEM.replace("{document}", document).replace("{language}", language)
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}] + messages,
        temperature=0.3, max_tokens=1024,
    )
    return r.choices[0].message.content

def generate_pdf_report(summary: str, language: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    ss   = getSampleStyleSheet()
    teal = colors.HexColor("#0d9488")
    navy = colors.HexColor("#0f172a")
    grey = colors.HexColor("#64748b")

    title_s = ParagraphStyle("T", parent=ss["Title"],   fontSize=22, textColor=teal, alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4)
    sub_s   = ParagraphStyle("S", parent=ss["Normal"],  fontSize=10, textColor=grey, alignment=TA_CENTER, spaceAfter=16)
    body_s  = ParagraphStyle("B", parent=ss["Normal"],  fontSize=11, leading=16, textColor=navy, spaceAfter=8)
    hdr_s   = ParagraphStyle("H", parent=ss["Heading2"],fontSize=13, textColor=teal, fontName="Helvetica-Bold", spaceAfter=6)

    story = [
        Paragraph("MedClear Patient Summary", title_s),
        Paragraph(f"Language: {LANGUAGE_NAMES[language]}  |  Generated by MedClear AI", sub_s),
        HRFlowable(width="100%", thickness=1, color=teal, spaceAfter=16),
    ]
    for line in summary.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 8))
        elif any(line.startswith(h) for h in ["DIAGNOSIS","MEDICATIONS","FOLLOW-UP","WARNING","HOME CARE","SAFETY",
                                               "🩺","💊","📅","⚠","🏠","🔒"]):
            story += [Spacer(1,10), Paragraph(line, hdr_s)]
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, body_s))
    story += [
        Spacer(1,20),
        HRFlowable(width="100%", thickness=0.5, color=grey),
        Paragraph("AI-generated — review by a healthcare professional required.", sub_s),
    ]
    doc.build(story)
    return buf.getvalue()

# ── Session state defaults ────────────────────────────────────────────────────
for k, v in {
    "extracted_text": "",
    "summary": "",
    "chat_history": [],
    "language": "English",
    "camera_active": False,
    "source_label": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
      <div class="sidebar-cross">✚</div>
      <div class="sidebar-brand">MedClear</div>
      <div class="sidebar-tagline">Healthcare AI Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section-title">🌐 Output Language</div>',
        unsafe_allow_html=True
    )

    lang = st.selectbox(
        "lang",
        list(LANGUAGE_NAMES.keys()),
        index=list(LANGUAGE_NAMES.keys()).index(
            st.session_state["language"]
        ),
        label_visibility="collapsed"
    )

    st.session_state["language"] = lang

    st.caption(
        f"Summaries in **{LANGUAGE_NAMES[lang]}**"
    )

    st.markdown("---")

    api_ok = bool(get_api_key())

    if api_ok:
        st.markdown(
            '<div class="api-status ok">🟢 AI Engine: Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="api-status err">🔴 AI Engine: Not configured</div>',
            unsafe_allow_html=True
        )

    ocr_ok = load_ocr()

    if ocr_ok:
        st.markdown(
            '<div class="api-status ok" style="margin-top:6px">🟢 OCR Engine: Ready</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="api-status warn" style="margin-top:6px">🟡 OCR: Not available</div>',
            unsafe_allow_html=True
        )

    st.markdown("---") 
    if st.session_state["extracted_text"]:
        wc = len(st.session_state["extracted_text"].split())
        st.markdown(f'<div class="stat-chip">📝 {wc} words extracted</div>', unsafe_allow_html=True)
    if st.session_state["summary"]:
        st.markdown('<div class="stat-chip">✅ Summary ready</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-footer">MedClear v1.0 · Groq + Llama 3.1</div>', unsafe_allow_html=True)
st.write("Tesseract Test")

try:
    st.success(pytesseract.get_tesseract_version())
except Exception as e:
    st.error(e)

# ════════════════════════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-header">
  <div class="hero-bg-pattern"></div>
  <div class="hero-content">
    <div class="hero-badge">🏥 AI-Powered Medical Communication</div>
    <h1 class="hero-title">MedClear</h1>
    <p class="hero-subtitle">Transform complex hospital discharge notes &amp; medical reports
    into clear, patient-friendly summaries — instantly.</p>
    <div class="hero-stats">
      <div class="hstat"><span class="hstat-num">5</span><span class="hstat-lbl">Languages</span></div>
      <div class="hstat-div"></div>
      <div class="hstat"><span class="hstat-num">OCR</span><span class="hstat-lbl">Scanned Docs</span></div>
      <div class="hstat-div"></div>
      <div class="hstat"><span class="hstat-num">PDF</span><span class="hstat-lbl">Export</span></div>
      <div class="hstat-div"></div>
      <div class="hstat"><span class="hstat-num">Chat</span><span class="hstat-lbl">Q&amp;A Mode</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════════════════════
tab_input, tab_summary, tab_chat = st.tabs([
    "📂  Upload & Extract",
    "📋  AI Summary",
    "💬  Ask MedClear",
])

# ─── TAB 1 ───────────────────────────────────────────────────────────────────
with tab_input:
    st.markdown('<div class="tab-section-title">Choose your input method</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📁 Upload Document</div>', unsafe_allow_html=True)

        input_method = st.radio(
            "method", ["PDF Report", "Image File", "Camera Capture"],
            horizontal=True, label_visibility="collapsed",
        )

        if input_method == "PDF Report":
            uploaded_pdf = st.file_uploader(
                "Upload PDF", type=["pdf"], label_visibility="collapsed",
                help="Discharge summaries, lab reports, prescriptions…"
            )
            if uploaded_pdf:
                with st.spinner("📄 Reading PDF…"):
                    text = extract_text_from_pdf(uploaded_pdf)
                if text:
                    st.session_state["extracted_text"] = text
                    st.session_state["source_label"]   = uploaded_pdf.name
                    st.success(f"✅ Extracted **{len(text.split())} words** from {uploaded_pdf.name}")
                else:
                    st.warning("⚠️ No text found. The PDF may be image-based — try the Image File option.")

        elif input_method == "Image File":
            if not ocr_ok:
                st.warning("⚠️ OCR engine not available in this environment. Use PDF or Manual Text input instead.")
            else:
                uploaded_img = st.file_uploader(
                    "Upload Image", type=["jpg","jpeg","png"], label_visibility="collapsed"
                )
                if uploaded_img:
                    img_bytes = uploaded_img.read()
                    st.image(img_bytes, caption="Uploaded image", use_container_width=True)
                    with st.spinner("🔍 Running OCR…"):
                        text = extract_text_from_image(img_bytes)
                    if text:
                        st.session_state["extracted_text"] = text
                        st.session_state["source_label"]   = uploaded_img.name
                        st.success(f"✅ Extracted **{len(text.split())} words** via OCR")
                    else:
                        st.warning("⚠️ Could not extract text. Try a higher-quality image.")

        elif input_method == "Camera Capture":
            if not ocr_ok:
                st.warning("⚠️ OCR engine not available in this environment. Use PDF or Manual Text input instead.")
            else:
                btn_label = "⏹ Turn Camera OFF" if st.session_state["camera_active"] else "📷 Turn Camera ON"
                if st.button(btn_label, use_container_width=True):
                    st.session_state["camera_active"] = not st.session_state["camera_active"]
                    st.rerun()

                if st.session_state["camera_active"]:
                    cam_img = st.camera_input("Point camera at document", label_visibility="collapsed")
                    if cam_img:
                        img_bytes = cam_img.getvalue()
                        with st.spinner("🔍 OCR on captured image…"):
                            text = extract_text_from_image(img_bytes)
                        if text:
                            st.session_state["extracted_text"] = text
                            st.session_state["source_label"]   = "Camera Capture"
                            st.success(f"✅ Extracted **{len(text.split())} words** from camera")
                            st.session_state["camera_active"] = False
                            st.rerun()
                        else:
                            st.warning("⚠️ No text detected. Try better lighting or a closer shot.")
                else:
                    st.info("🎥 Click **Turn Camera ON** to scan a document live.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card card-green">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">✏️ Manual Text Input</div>', unsafe_allow_html=True)
        manual_text = st.text_area(
            "manual", height=240,
            placeholder="Paste discharge notes, prescriptions, lab results, or any medical text here…",
            label_visibility="collapsed",
        )
        if st.button("✅ Use This Text", use_container_width=True, disabled=not manual_text.strip()):
            st.session_state["extracted_text"] = manual_text.strip()
            st.session_state["source_label"]   = "Manual Input"
            st.success("✅ Text ready for processing")
        st.markdown('</div>', unsafe_allow_html=True)

    # Preview + generate
    if st.session_state["extracted_text"]:
        st.markdown("---")
        with st.expander(
            f"👁 Preview extracted text — {len(st.session_state['extracted_text'].split())} words",
            expanded=False
        ):
            st.text_area("preview", st.session_state["extracted_text"],
                         height=180, label_visibility="collapsed", disabled=True)

        st.markdown("---")
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            if st.button("🚀 Generate Patient-Friendly Summary",
                         use_container_width=True, type="primary"):
                if not get_api_key():
                    st.error("⚠️ GROQ_API_KEY not found. Add it to .streamlit/secrets.toml")
                else:
                    with st.spinner("🧠 MedClear is analysing the document…"):
                        prog = st.progress(0)
                        for i in range(0, 85, 10):
                            time.sleep(0.07)
                            prog.progress(i)
                        summary = generate_summary(
                            st.session_state["extracted_text"],
                            st.session_state["language"],
                        )
                        prog.progress(100)
                        time.sleep(0.15)
                        prog.empty()
                    st.session_state["summary"]      = summary
                    st.session_state["chat_history"] = []
                    st.success("✅ Summary ready! Switch to the **AI Summary** tab.")

# ─── TAB 2 ───────────────────────────────────────────────────────────────────
with tab_summary:
    if not st.session_state["summary"]:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>No summary yet</h3>
          <p>Upload a document in <strong>Upload &amp; Extract</strong> and click <em>Generate Summary</em>.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div class="meta-chip">📄 {st.session_state["source_label"]}</div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="meta-chip">🌐 {LANGUAGE_NAMES[st.session_state["language"]]}</div>', unsafe_allow_html=True)
        with mc3:
            st.markdown('<div class="meta-chip ok">🟢 Confidence: High</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        st.markdown(st.session_state["summary"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

        _, dc, _ = st.columns([1, 2, 1])
        with dc:
            try:
                pdf_bytes = generate_pdf_report(
                    st.session_state["summary"],
                    st.session_state["language"],
                )
                st.download_button(
                    "⬇️ Download Summary as PDF",
                    data=pdf_bytes,
                    file_name=f"medclear_{st.session_state['language'].lower()}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")

        st.markdown("""
        <div class="ai-warning">
          ⚠️ <strong>AI-Generated Content:</strong> This summary is intended to assist — not replace —
          professional medical advice. A qualified healthcare professional must review it before patient use.
        </div>
        """, unsafe_allow_html=True)

# ─── TAB 3 ───────────────────────────────────────────────────────────────────
with tab_chat:
    if not st.session_state["extracted_text"]:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">💬</div>
          <h3>No document loaded</h3>
          <p>Upload a document first to start asking questions.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="tab-section-title">💬 Ask Questions About Your Document</div>', unsafe_allow_html=True)
        st.caption("MedClear answers using only the information in your uploaded document.")

        st.markdown("**Quick questions:**")
        qc1, qc2 = st.columns(2)
        quick_qs = [
            "What medicines should I take?",
            "What precautions should I follow?",
            "What symptoms should I watch for?",
            "When should I visit the doctor again?",
        ]
        for i, q in enumerate(quick_qs):
            with (qc1 if i % 2 == 0 else qc2):
                if st.button(q, key=f"qb_{i}", use_container_width=True):
                    st.session_state["chat_history"].append({"role": "user", "content": q})
                    with st.spinner("🤔 Thinking…"):
                        reply = chat_with_document(
                            st.session_state["chat_history"],
                            st.session_state["extracted_text"],
                            st.session_state["language"],
                        )
                    st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                    st.rerun()

        st.divider()

        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user"><strong>You:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bot"><strong>🏥 MedClear:</strong><br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

        user_q = st.chat_input("Ask a question about the document…")
        if user_q:
            st.session_state["chat_history"].append({"role": "user", "content": user_q})
            with st.spinner("🤔 Thinking…"):
                reply = chat_with_document(
                    st.session_state["chat_history"],
                    st.session_state["extracted_text"],
                    st.session_state["language"],
                )
            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
            st.rerun()

        if st.session_state["chat_history"]:
            if st.button("🗑 Clear Chat"):
                st.session_state["chat_history"] = []
                st.rerun()
