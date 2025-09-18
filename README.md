# 🩻 Medical Report Diagnosis Agent

A Medical Report Diagnosis Agent build on agno powered by Gemini 2.0 Flash that provides AI-assisted analysis of medical images of various scans. The agent acts as a medical imaging diagnosis expert to analyze various types of medical images and videos, providing detailed diagnostic insights and explanations.

## Features

- **Comprehensive Image Analysis**
  - Image Type Identification (X-ray, MRI, CT scan, ultrasound)
  - Anatomical Region Detection
  - Key Findings and Observations
  - Potential Abnormalities Detection
  - Image Quality Assessment# 🏥 Medical Imaging Diagnosis Agent

A lightweight Streamlit app that analyzes a single medical image using Google Gemini and generates a clean, readable PDF report. The app shows the exact image you see in the UI (with optional enhancement), produces a structured markdown analysis, and lets you download the same content as a PDF. The download button appears only after the analysis is complete and has a transparent hover effect.

⚠️ Educational use only. Do not use this tool for medical decision-making without review by qualified clinicians.

---

## ✨ Features

- Upload a single image (JPG/PNG)
- Optional on-the-fly enhancement (contrast/sharpness)
- Structured, concise analysis via Gemini:
  - Primary finding (smaller heading)
  - Image type & region
  - Key findings with confidence
  - Diagnostic assessment
  - Patient-friendly explanation
  - References
- Download report as a readable PDF with:
  - The exact displayed image
  - The same markdown content shown in the UI
- Transparent, hover-styled download button
- Robust PDF generation (avoids width/rendering errors)

---

## 🧰 Tech Stack

- Streamlit
- PIL (Pillow) for lightweight image enhancement
- FPDF (fpdf2) for PDF generation
- Agno Agent + Google Gemini (via Google AI Studio API)

---

## 📦 Requirements

- Python 3.9+
- A Google AI Studio API key for Gemini

Install dependencies:

```bash
pip install streamlit pillow fpdf2 agno google-generativeai
```

Alternatively, use a requirements.txt:

```txt
streamlit
pillow
fpdf2
agno
google-generativeai
```

---

## 🚀 Quickstart

1) Clone this repository and enter the project directory.

2) Install dependencies:
```bash
pip install -r requirements.txt
# or
pip install streamlit pillow fpdf2 agno google-generativeai
```

3) Run the app:
```bash
streamlit run image-diagnose-agent.py
```

4) In the app:
- Enter your Google API key in the sidebar (get it from https://aistudio.google.com/apikey).
- Fill in patient info (optional).
- Upload a medical image (JPG/PNG).
- Toggle “Enhance image” if you want.
- Click “Analyze Image.”
- Review the analysis, then download the PDF.

---

## 🖼️ What the PDF Contains

- Patient info (name, age, sex, study date)
- The exact image shown in the UI (enhanced or original based on your toggle)
- The same markdown analysis displayed in the app
- A short footer disclaimer

No duplicate images, no unreadable formatting.

---

## 🔐 Privacy & Safety

- Images are processed locally and sent to Google’s Gemini API for analysis.
- Avoid uploading identifiable patient data (PHI).
- This tool is intended for educational and quality-improvement contexts only.

---

## ⚙️ Configuration

- API Key: Enter via the app sidebar (stored in session state only).
- Model: gemini-2.0-flash (configured in the code; change if needed).
- Enhancement: Toggle on/off in the UI (Pillow-based, no OpenCV required).
- Styling: Transparent hover style for the download button via simple CSS.

Optional: If you prefer reading the API key from an environment variable, you can modify the code to default to:
```python
import os
st.session_state.GOOGLE_API_KEY = st.session_state.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
```

---

## 🧠 How It Works (High-level)

1) User uploads a single image and optionally enhances it (PIL).
2) The displayed image is saved to a temp file and sent to Gemini via Agno.
3) The model returns a structured markdown analysis.
4) The app renders this markdown and builds a PDF from the same content.
5) A download button appears once the PDF is ready.

---

## 🛠️ Troubleshooting

- Streamlit download error “Invalid binary data format: bytearray”
  - The app ensures the PDF is returned as bytes, so this should not occur. If you modify the code, ensure you pass bytes, not bytearray, to st.download_button.

- FPDF error “Not enough horizontal space to render a single character”
  - The app sanitizes text, uses the effective page width for MultiCells, and splits very long tokens. If you paste exotic symbols or emojis into the markdown, consider switching to a Unicode TTF font (see below).

- Missing characters or squares in PDF (Unicode)
  - Core fonts are Latin-1. To keep emojis or non-Latin chars, add a Unicode font:
    ```python
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=11)
    ```
  - Then use that font instead of Helvetica across the PDF generation.

- Gemini errors or empty responses
  - Check your API key and network connectivity.
  - Ensure the model id (gemini-2.0-flash) is available for your key/region.

---

## 📁 Project Structure

```
.
├─ image-diagnose-agent.py   # Main Streamlit app
├─ README.md                 # You are here
└─ requirements.txt          # Optional
```

---

## 🗺️ Roadmap Ideas

- Optional multi-pass analysis (consistency/verification passes)
- Tool-assisted literature search with real links
- DICOM support with window/level controls
- Structured JSON export (FHIR ImagingStudy/DiagnosticReport draft)
- Multi-image/study support with series selection

---

## 🤝 Contributing

Pull requests welcome! For bigger changes, please open an issue to discuss your idea first.

---

## ⚖️ License

MIT License. See LICENSE for details.

---

## 🙏 Acknowledgements

- Streamlit: https://streamlit.io
- Pillow: https://python-pillow.org
- fpdf2: https://pyfpdf.github.io/fpdf2
- Agno: https://github.com/agnohq/agno
- Google Gemini (AI Studio): https://aistudio.google.com

---

## ❓ FAQ

- Can I keep the markdown instead of PDF?
  - Yes, you can adapt the code to also expose a markdown download; the current version focuses on a clean PDF.

- Does it store my images?
  - Images are processed in memory and saved temporarily for analysis and PDF generation. They’re not permanently stored by the app.

- Can I use a different model?
  - Yes. Change the Gemini model id in the code or swap in another Agno-supported model.

If you need a one-click deploy guide (Streamlit Community Cloud, Hugging Face Spaces, or Docker), say the word and I’ll add it.
  - Research and Reference

## Disclaimer

This tool is for educational and informational purposes only. All analyses should be reviewed by qualified healthcare professionals. Do not make medical decisions based solely on this analysis.
