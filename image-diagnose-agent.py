import re
import tempfile
from datetime import date

import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
from fpdf import FPDF

from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image as AgnoImage


# ---------------- Session State ----------------
for key, default in [
    ("GOOGLE_API_KEY", None),
    ("pdf_bytes", None),
    ("pdf_filename", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- Sidebar: API key + Info ----------------
with st.sidebar:
    st.title("ℹ️ Configuration")

    if not st.session_state.GOOGLE_API_KEY:
        api_key = st.text_input("Enter your Google API Key:", type="password")
        st.caption("Get your API key from Google AI Studio (https://aistudio.google.com/apikey) 🔑")
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("API Key saved!")
            st.rerun()
    else:
        st.success("API Key is configured")
        if st.button("🔄 Reset API Key"):
            st.session_state.GOOGLE_API_KEY = None
            st.rerun()

    st.info("AI-powered analysis of medical imaging data.")
    st.warning("⚠ For educational use only. Review with a qualified clinician.")


# ---------------- Agent ----------------
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=st.session_state.GOOGLE_API_KEY),
    markdown=True
) if st.session_state.GOOGLE_API_KEY else None

if not medical_agent:
    st.warning("Please configure your API key in the sidebar to continue.")


# ---------------- Utilities ----------------
def enhance_image(img: Image) -> Image:
    # Lightweight enhancement (no OpenCV)
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    return img


def sanitize_text(text: str) -> str:
    if not text:
        return ""
    t = str(text)
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2212": "-",  # minus sign
        "\u2022": "-",  # bullet
        "\u00B7": "-",  # middle dot
        "\u00A0": " ",  # non-breaking space
    }
    for k, v in replacements.items():
        t = t.replace(k, v)
    # Remove emojis / non-Latin-1 (fpdf Core fonts)
    t = t.encode("latin-1", "ignore").decode("latin-1")
    return t


def soft_wrap_tokens(text: str, max_len: int = 60) -> str:
    # Split very long tokens so MultiCell can wrap
    out = []
    for tok in str(text).split(" "):
        if len(tok) <= max_len:
            out.append(tok)
        else:
            chunks = [tok[i:i + max_len] for i in range(0, len(tok), max_len)]
            out.append("\n".join(chunks))
    return " ".join(out)


def build_pdf_from_markdown(patient_info: dict, markdown_text: str, image_path: str) -> bytes:
    def render_md_line(pdf: FPDF, epw: float, line_h: float, raw: str):
        s = sanitize_text(raw.rstrip())
        if not s.strip():
            pdf.ln(2)
            return

        # Headings
        if s.startswith("#### "):
            pdf.set_font("Helvetica", "B", 11)
            txt = s[5:].strip()
        elif s.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            txt = s[4:].strip()
        elif s.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            txt = s[3:].strip()
        elif s.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            txt = s[2:].strip()
        else:
            # Bullets and ordered lists
            pdf.set_font("Helvetica", "", 10)
            if re.match(r"^[-*]\s+", s):
                txt = "• " + s[2:].strip()
            elif re.match(r"^\d+[.)]\s+", s):
                txt = s
            else:
                txt = s

        txt = soft_wrap_tokens(txt, 60)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(epw, line_h, txt)

    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    epw = pdf.w - pdf.l_margin - pdf.r_margin
    line_h = 5.5

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.cell(epw, 10, "Medical Imaging Report", ln=1, align="C")

    # Patient info
    pdf.set_font("Helvetica", size=11)
    pi1 = f"Patient: {sanitize_text(patient_info.get('name',''))}    Age: {sanitize_text(patient_info.get('age',''))}    Sex: {sanitize_text(patient_info.get('sex',''))}"
    pi2 = f"Study Date: {sanitize_text(patient_info.get('study_date',''))}"
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(epw, line_h, pi1)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(epw, line_h, pi2)
    pdf.ln(2)

    # Single image (exactly the one shown in UI)
    try:
        from PIL import Image as PILImage
        img = PILImage.open(image_path)
        max_w = epw
        ratio = img.height / max(img.width, 1)
        img_h = max_w * ratio
        if pdf.get_y() + img_h + 8 > pdf.h - pdf.b_margin:
            pdf.add_page()
        pdf.set_x(pdf.l_margin)
        pdf.image(image_path, x=pdf.l_margin, y=pdf.get_y(), w=max_w)
        pdf.set_xy(pdf.l_margin, pdf.get_y() + img_h + 4)
    except Exception:
        pass

    # Render markdown lines
    for line in (markdown_text or "").splitlines():
        render_md_line(pdf, epw, line_h, line)

    # Footer
    pdf.ln(4)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(epw, 5, "AI-assisted report for educational purposes. Please have a qualified clinician review.")
    pdf.set_text_color(0, 0, 0)

    raw = pdf.output(dest="S")
    if isinstance(raw, bytes):
        return raw
    if isinstance(raw, (bytearray, memoryview)):
        return bytes(raw)
    return str(raw).encode("latin-1", errors="ignore")


# ---------------- UI ----------------
st.title("🏥 Medical Imaging Diagnosis Agent")

# Patient info
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
with col1:
    patient_name = st.text_input("Patient Name", value="")
with col2:
    patient_age = st.text_input("Age", value="")
with col3:
    patient_sex = st.selectbox("Sex", options=["", "Male", "Female", "Other"], index=0)
with col4:
    study_date = st.date_input("Study Date", value=date.today())

patient_info = {
    "name": (patient_name or "").strip(),
    "age": (patient_age or "").strip(),
    "sex": patient_sex,
    "study_date": study_date.isoformat(),
}

st.write("Upload a medical image for analysis")
uploaded_file = st.file_uploader("Upload Medical Image", type=["jpg", "jpeg", "png"])

# Reset when a new file is uploaded
if uploaded_file is not None:
    st.session_state.pdf_bytes = None
    st.session_state.pdf_filename = None

if uploaded_file is not None and medical_agent:
    try:
        img = Image.open(uploaded_file).convert("RGB")

        # Optional lightweight enhancement
        enhance = st.toggle("Enhance image", value=True)
        shown_img = enhance_image(img) if enhance else img

        st.image(shown_img, caption="Displayed Medical Image", use_container_width=True)

        if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
            with st.spinner("🔄 Analyzing image..."):
                # Save displayed image to a temp file (used for model + PDF)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name
                    shown_img.save(tmp_path)

                agno_image = AgnoImage(filepath=tmp_path)

                # Single-pass analysis (concise, structured markdown; small primary heading)
                prompt = (
                    "You are a medical imaging expert. Analyze the attached image and write a concise, structured "
                    "markdown report with these sections:\n"
                    "### Primary finding: <finding> (<confidence>% confidence)\n"
                    "1) Image Type & Region (modality, region, positioning, quality)\n"
                    "2) Key Findings (bulleted; include confidence %)\n"
                    "3) Diagnostic Assessment (primary diagnosis with confidence; differentials with brief rationale)\n"
                    "4) Patient-Friendly Explanation (plain language)\n"
                    "5) References (2–3 items)\n"
                    "Be precise and avoid unsupported claims."
                )
                resp = medical_agent.run(prompt, images=[agno_image])
                report_md = (resp.content or "").strip()

                # Show the same markdown in the UI
                st.markdown("### 📋 Analysis Results")
                st.divider()
                st.markdown(report_md)
                st.divider()
                st.caption("Note: AI-generated analysis. Please have a qualified clinician review.")

                # Build a readable PDF from the same markdown, with the displayed image
                pdf_bytes = build_pdf_from_markdown(patient_info, report_md, image_path=tmp_path)
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_filename = (
                    f"report_{patient_info.get('name','patient')}_{patient_info.get('study_date','')}"
                    .strip("_").replace(" ", "_")
                )

    except Exception as e:
        st.error(f"Analysis error: {e}")

elif uploaded_file is None:
    st.info("👆 Please upload a medical image to begin analysis")


# ---------------- Download Button (only after analysis) ----------------
if st.session_state.pdf_bytes:
    # Transparent hover style
    st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] > button {
            background: transparent !important;
            color: #0F6FFF !important;
            border: 1px solid #0F6FFF !important;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            transition: background-color .2s ease, border-color .2s ease, color .2s ease, transform .05s ease;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background: rgba(15, 111, 255, 0.08) !important;
            border-color: #0B5ED7 !important;
            color: #0B5ED7 !important;
        }
        div[data-testid="stDownloadButton"] > button:active {
            transform: translateY(1px);
        }
        </style>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📝 Download Report")
    data_bytes = st.session_state.pdf_bytes if isinstance(st.session_state.pdf_bytes, bytes) else bytes(st.session_state.pdf_bytes)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=data_bytes,
        file_name=f"{st.session_state.pdf_filename}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf_btn",
    )