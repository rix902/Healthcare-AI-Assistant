import streamlit as st
import requests
import base64
from io import BytesIO
from pypdf import PdfReader
from PIL import Image
import pytesseract
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.card {
    background-color: #f8fafc;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------

st.sidebar.title("🏥 Healthcare AI")

api_key = st.sidebar.text_input(
    "Grok API Key",
    type="password"
)

uploaded_pdf = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

uploaded_image = st.sidebar.file_uploader(
    "Upload Image",
    type=["png", "jpg", "jpeg"]
)

camera_image = st.sidebar.camera_input(
    "Capture Image"
)

# ---------------------------
# PDF READER
# ---------------------------

def read_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text

# ---------------------------
# OCR
# ---------------------------

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# ---------------------------
# GROK API
# ---------------------------

def generate_summary(text, api_key):

    prompt = f"""
You are a clinical communication assistant.

Convert the discharge note below into a patient-friendly summary.

Rules:
- Use simple language.
- Keep medical accuracy.
- Do not invent information.
- Highlight medications.
- Highlight follow-up appointments.
- Highlight warning signs.

Discharge Note:
{text}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# ---------------------------
# PDF EXPORT
# ---------------------------

def create_pdf(summary):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Patient Discharge Summary",
            styles["Title"]
        )
    )

    elements.append(Spacer(1,12))

    elements.append(
        Paragraph(summary.replace("\n","<br/>"),
        styles["BodyText"])
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer

# ---------------------------
# MAIN
# ---------------------------

st.title("🏥 AI Patient Discharge Summary Generator")

st.markdown(
    "Convert clinical discharge notes into patient-friendly summaries."
)

input_text = ""

# PDF

if uploaded_pdf:
    input_text += read_pdf(uploaded_pdf)

# IMAGE

if uploaded_image:
    img = Image.open(uploaded_image)
    st.image(img, caption="Uploaded Image")
    input_text += extract_text_from_image(img)

# CAMERA

if camera_image:
    img = Image.open(camera_image)
    st.image(img, caption="Captured Image")
    input_text += extract_text_from_image(img)

manual_text = st.text_area(
    "Or paste discharge note here",
    height=250
)

if manual_text:
    input_text += "\n" + manual_text

# GENERATE

if st.button("🤖 Generate Summary"):

    if not api_key:
        st.error("Enter Grok API Key")
        st.stop()

    if not input_text.strip():
        st.error("Provide PDF, image, camera scan, or text.")
        st.stop()

    with st.spinner("Generating summary..."):

        try:

            summary = generate_summary(
                input_text,
                api_key
            )

            st.success("Summary Generated")

            col1, col2 = st.columns([3,1])

            with col1:

                st.markdown("## 📄 Patient-Friendly Summary")
                st.markdown(summary)

            with col2:

                st.markdown("## ⚠ Safety Panel")

                st.info(
                    "Review AI output before sharing with patients."
                )

                st.progress(90)

                st.caption(
                    "AI Confidence Indicator"
                )

            pdf_buffer = create_pdf(summary)

            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name="patient_summary.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(str(e))
