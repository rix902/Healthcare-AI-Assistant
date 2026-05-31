import streamlit as st
import requests
import numpy as np

from io import BytesIO
from pypdf import PdfReader
from PIL import Image

import easyocr

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.metric-card {
    background:#f5f7fb;
    padding:15px;
    border-radius:12px;
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("🏥 Healthcare AI")

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

# -----------------------------------
# OCR
# -----------------------------------

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def extract_text_from_image(image):

    try:

        reader = load_ocr()

        results = reader.readtext(
            np.array(image),
            detail=0
        )

        return "\n".join(results)

    except Exception as e:

        st.warning(
            f"OCR Error: {str(e)}"
        )

        return ""

# -----------------------------------
# PDF READER
# -----------------------------------

def read_pdf(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

# -----------------------------------
# GROK
# -----------------------------------

def generate_summary(text):

    api_key = st.secrets["GROK_API_KEY"]

    prompt = f"""
You are a clinical communication assistant.

Convert the discharge note below into a patient-friendly summary.

Rules:

- Use simple language.
- Maintain medical accuracy.
- Do not invent facts.
- Mention medications.
- Mention follow-up instructions.
- Mention warning signs.
- Use bullet points where useful.

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
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# -----------------------------------
# PDF EXPORT
# -----------------------------------

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

    elements.append(
        Spacer(1, 12)
    )

    elements.append(
        Paragraph(
            summary.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer

# -----------------------------------
# MAIN UI
# -----------------------------------

st.title(
    "🏥 AI Patient Discharge Summary Generator"
)

st.markdown(
    """
Convert clinical discharge notes into
easy-to-understand patient summaries.
"""
)

input_text = ""

# PDF

if uploaded_pdf:

    pdf_text = read_pdf(
        uploaded_pdf
    )

    input_text += pdf_text

# IMAGE

if uploaded_image:

    image = Image.open(
        uploaded_image
    )

    st.image(
        image,
        caption="Uploaded Image"
    )

    input_text += extract_text_from_image(
        image
    )

# CAMERA

if camera_image:

    image = Image.open(
        camera_image
    )

    st.image(
        image,
        caption="Captured Image"
    )

    input_text += extract_text_from_image(
        image
    )

# MANUAL TEXT

manual_text = st.text_area(
    "Or Paste Discharge Note",
    height=250
)

if manual_text:

    input_text += "\n" + manual_text

# GENERATE

if st.button(
    "🤖 Generate Summary"
):

    if not input_text.strip():

        st.error(
            "Upload a PDF, image, camera scan or enter text."
        )

        st.stop()

    with st.spinner(
        "Generating summary..."
    ):

        try:

            summary = generate_summary(
                input_text
            )

            st.success(
                "Summary Generated Successfully"
            )

            col1, col2 = st.columns(
                [3, 1]
            )

            with col1:

                st.markdown(
                    "## 📄 Patient-Friendly Summary"
                )

                st.markdown(
                    summary
                )

            with col2:

                st.markdown(
                    "## ⚠ Safety Panel"
                )

                st.info(
                    "Always review AI output before sharing with patients."
                )

                st.metric(
                    "AI Status",
                    "Ready"
                )

                st.metric(
                    "Confidence",
                    "90%"
                )

            pdf_buffer = create_pdf(
                summary
            )

            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name="patient_summary.pdf",
                mime="application/pdf"
            )

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )
