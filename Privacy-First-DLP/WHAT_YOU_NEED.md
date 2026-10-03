# What else you need

## For the current prototype

- Python 3.10 or newer.
- A code editor such as Visual Studio Code.
- The files in this folder and an internet connection only to install the listed Python packages.
- Synthetic TXT, PDF, DOCX, and CSV samples for demos. Do not use real personal or confidential documents while developing.

## Front end and back end in this project

- **Front end:** `app.py` uses Streamlit for a guided upload flow, 10 MB upload limit, redacted preview, summary, findings table, decision display, and redacted-text download. It does not display the original extracted text in the results screen.
- **REST API:** `api/main.py` uses FastAPI. `GET /health` checks availability and `POST /scan` scans up to 200,000 characters. The endpoint rejects blank text and documents its response shape. FastAPI provides interactive docs at `/docs`.
- **Back end:** `modules/dlp_service.py` runs the scan and returns finding counts, scanned character count, a demonstration score, and recommendation.
- **Detection logic:** `modules/regex_detector.py` finds email and phone-like patterns plus credentials after labels like `Password:` and `API_Key:`, then masks detected values.
- **Data storage:** none yet. The prototype does not need a database for its first milestone.

## Suggested build order

1. **Implemented:** upload supported document formats, extract text locally, scan through the local API, display masked output and findings, and download the redacted preview.
2. **Your next action:** install/update dependencies with `pip install -r requirements.txt`, then run `python -m unittest discover -s tests -v`. Start the API and Streamlit in separate terminals and try synthetic files in all four formats. Use an image-only PDF once to confirm the app explains the OCR limitation.
3. **Then:** build a small labeled dataset with both positive and negative examples. Record expected entity types and spans, then measure precision, recall, and F1 per detector. The automated tests prove example behavior, but they do not measure real-world accuracy.
4. Improve patterns based on false positives and false negatives. Document what each detector can and cannot find.
5. Add OCR for image-only PDFs or additional formats only if they are needed for your demonstration; evaluate each new format with sample files.
6. Consider NLP/NER only after the rule baseline has measured results. Treat ML as a later experiment, not a replacement for evaluation.
7. Prepare the final report and presentation with architecture, requirements, methodology, screenshots, evaluation results, limitations, and future work.

## Important limitation

The credential rules require labels such as `Password:` or `API_Key:`. The current risk score is a demonstration rule, not a calibrated security score. A detected pattern may be a false positive, and missing matches do not mean a document is safe. Keep this as a local educational prototype unless it receives a proper security review.
