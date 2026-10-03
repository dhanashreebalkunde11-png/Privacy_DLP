# Privacy-First DLP

A student project that scans documents for common sensitive information. The Streamlit front end extracts supported files and sends their text to a local FastAPI backend, which returns masked findings and a suggested decision.

## Current prototype

Upload a TXT, PDF, DOCX, or CSV file up to 10 MB, scan it for emails, phone-like numbers, labeled passwords, and labeled API keys, then review or download a redacted text preview. The API accepts up to 200,000 extracted characters per scan. Image-only PDFs are not supported because OCR is not included. This is a learning prototype, not a production security product.

## Get the project

To work with this project as a team, clone the repository and enter its project folder:

```powershell
git clone https://github.com/dhanashreebalkunde11-png/Privacy_DLP.git
cd Privacy_DLP/Privacy-First-DLP
```

## Run it

1. Install Python 3.10 or newer.
2. Open a terminal in the `Privacy-First-DLP` project folder (after cloning, run `cd Privacy_DLP/Privacy-First-DLP`).
3. (Recommended) Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the front end, API, and document extraction dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Start the API in the first terminal:

   ```powershell
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
   ```

6. Open a second terminal in this folder and start the front end:

   ```powershell
   streamlit run app.py
   ```

While the API is running, its interactive docs are at `http://127.0.0.1:8000/docs`. The front end uses `http://127.0.0.1:8000` by default; set `DLP_API_URL` before launching Streamlit to use another API base URL.

The API has `GET /health` and `POST /scan`. Example request body for `/scan`:

```json
{"text":"Email: person@example.com\nPassword: example-password\nAPI_Key: example-token-1234"}
```

The API has no third-party API key: it runs locally and uses the project's Python detector. Do not expose this unauthenticated prototype API to a public network.

## Project layout

```text
Privacy-First-DLP/
├── app.py
├── api/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── README.md
├── PROJECT_OVERVIEW.md
├── WHAT_YOU_NEED.md
├── images/
│   └── architecture.svg
├── modules/
│   ├── __init__.py
│   ├── dlp_service.py
│   ├── file_processor.py
│   └── regex_detector.py
└── tests/
    ├── test_api.py
    ├── test_dlp.py
    └── test_file_processor.py
```

Run the automated checks from this folder with:

```powershell
python -m unittest discover -s tests -v
```

## Current behavior and next steps

- Current: Streamlit front end accepts TXT, PDF, DOCX, and CSV files, extracts their text locally, and sends that text to a local FastAPI backend. The results show counts, a demonstration score, decision reasoning, masked findings, and a downloadable redacted preview. The API rejects whitespace-only input, limits scans to 200,000 characters, and returns a documented response shape.
- Automated checks cover core detections/redaction, API request limits and behavior, and TXT/CSV/DOCX/PDF extraction. They confirm examples work; they do not establish real-world detector accuracy.
- Next: run the app with synthetic examples for every supported format. Then build a small labeled dataset and measure precision, recall, and F1 for each detector. Improve validation based on measured false positives and false negatives.
- Later: evaluate an NLP/ML layer with a documented dataset and metrics. Keep source documents out of logs and avoid sending them to external services.

The detector uses simple patterns and can miss sensitive data or flag ordinary numbers. Scanned text is sent from Streamlit to the local API over loopback and is not intentionally persisted. Do not use it to make real security decisions.
