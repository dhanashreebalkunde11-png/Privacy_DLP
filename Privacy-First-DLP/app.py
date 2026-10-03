import os
from pathlib import Path

import requests
import streamlit as st

from modules.file_processor import extract_text_from_file


MAX_UPLOAD_MB = 10
API_URL = os.environ.get("DLP_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Privacy-First DLP",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp, [data-testid="stAppViewContainer"] {
        background: #f4f7fb;
        color: #152536;
      }
      [data-testid="stSidebar"] {
        background: #eaf1f7;
        color: #152536;
      }
      [data-testid="stHeader"] { background: rgba(244, 247, 251, .92); }
      .stMarkdown, .stMarkdown p, .stMarkdown span, label,
      [data-testid="stCaptionContainer"],
      [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
      [data-testid="stMetricDelta"], h1, h2, h3, h4 {
        color: #152536;
      }
      div[data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #152536 !important;
        -webkit-text-fill-color: #152536 !important;
        opacity: 1 !important;
        border: 1px solid #cbd7e3;
      }
      [data-testid="stCaptionContainer"] code {
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
      }
      .hero { padding: 1.6rem 1.8rem; border-radius: 18px; color: white;
        background: linear-gradient(115deg, #102c4a, #176b87); margin-bottom: 1.25rem; }
      .hero-title { color: #ffffff !important; margin: 0 0 .35rem 0;
        font-size: 2.1rem; font-weight: 700; line-height: 1.2; }
      .hero p { color: #d9edf4; margin: 0; font-size: 1rem; }
      .eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .74rem;
        font-weight: 700; color: #72d3cf; margin-bottom: .45rem; }
      div[data-testid="stMetric"] { background: white; padding: 1rem 1.2rem;
        border: 1px solid #e1e8f0; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About this scanner")
    st.write("Scans files on this device using a local API.")
    st.markdown("**Supported files**\n\nTXT · PDF · DOCX · CSV")
    st.markdown(f"**Upload limit**\n\n{MAX_UPLOAD_MB} MB per file")
    st.divider()
    st.caption("Prototype only. Pattern matching can miss sensitive data or flag ordinary text.")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Local document review</div>
      <div class="hero-title" role="heading" aria-level="1">Privacy-First DLP</div>
      <p>Find common sensitive values, review masked results, and decide what to do before sharing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

intro, status_col = st.columns([3, 1])
with intro:
    st.write("Upload a document to scan for email addresses, phone-like numbers, labeled passwords, and labeled API keys.")
with status_col:
    st.caption(f"API endpoint: `{API_URL}`")

uploaded_file = st.file_uploader(
    "Choose a document",
    type=["txt", "pdf", "docx", "csv"],
    max_upload_size=MAX_UPLOAD_MB,
    help=f"Files are processed for this scan only. Maximum size: {MAX_UPLOAD_MB} MB.",
)

if uploaded_file is None:
    with st.container(border=True):
        st.subheader("How it works")
        steps = st.columns(3)
        steps[0].markdown("**1 · Upload**\n\nChoose a TXT, PDF, DOCX, or CSV file.")
        steps[1].markdown("**2 · Scan locally**\n\nText is extracted in the app and sent to the local API.")
        steps[2].markdown("**3 · Review**\n\nInspect masked matches and the suggested action.")
    st.stop()

file_bytes = uploaded_file.getvalue()
file_size_mb = len(file_bytes) / (1024 * 1024)
st.caption(f"Selected: **{Path(uploaded_file.name).name}** · {file_size_mb:.2f} MB")

try:
    with st.spinner("Extracting text from the document…"):
        text = extract_text_from_file(uploaded_file.name, file_bytes)
except Exception as error:
    st.error(f"Could not read this file. Check that it is a valid, unencrypted {Path(uploaded_file.name).suffix.upper()} document.")
    st.caption(f"Details: {error}")
    st.stop()

if not text.strip():
    st.warning("No readable text was found. Scanned PDFs need a text layer; image-only PDFs need OCR, which this prototype does not include yet.")
    st.stop()

try:
    with st.spinner("Scanning with the local DLP API…"):
        response = requests.post(f"{API_URL}/scan", json={"text": text}, timeout=30)
        response.raise_for_status()
        result = response.json()
except requests.ConnectionError:
    st.error("The local DLP API is not responding. Start it in a terminal with `python -m uvicorn api.main:app --host 127.0.0.1 --port 8000`.")
    st.stop()
except requests.HTTPError as error:
    if response.status_code == 422:
        st.error("The extracted document is too large for the API limit (200,000 characters). Try a smaller document.")
    else:
        st.error(f"The API could not scan this document (HTTP {response.status_code}).")
    st.caption(f"Details: {error}")
    st.stop()
except requests.RequestException as error:
    st.error("The scan request failed. Check that the API is running and try again.")
    st.caption(f"Details: {error}")
    st.stop()
except ValueError:
    st.error("The API returned an unreadable response. Restart the API and try again.")
    st.stop()

findings = result.get("findings", [])
decision = result.get("decision", "UNKNOWN")
score = result.get("risk_score", 0)

st.divider()
st.subheader("Scan results")
summary = st.columns(3)
summary[0].metric("Potential findings", result.get("finding_count", len(findings)))
summary[1].metric("Demo risk score", f"{score} / 100")
summary[2].metric("Suggested action", decision)
st.caption(result.get("reason", "No decision details were returned."))

preview, finding_col = st.columns([1.35, 1])
with preview:
    st.markdown("#### Redacted preview")
    st.text_area(
        "Sensitive matches are replaced with masked values",
        result.get("redacted_text", ""),
        height=360,
        disabled=True,
        label_visibility="collapsed",
    )
    st.download_button(
        "Download redacted text",
        data=result.get("redacted_text", ""),
        file_name=f"{Path(uploaded_file.name).stem}.redacted.txt",
        mime="text/plain",
        width="stretch",
    )

with finding_col:
    st.markdown("#### Findings")
    if not findings:
        st.success("No supported patterns were detected. This does not guarantee the document is safe.")
    else:
        st.dataframe(
            [{"Type": item["type"], "Masked value": item["masked"], "Risk": item["risk"]} for item in findings],
            width="stretch",
            hide_index=True,
        )

st.info("The original extracted text is not shown in the results screen. This prototype does not intentionally save scan contents; avoid using real confidential files while evaluating it.")
