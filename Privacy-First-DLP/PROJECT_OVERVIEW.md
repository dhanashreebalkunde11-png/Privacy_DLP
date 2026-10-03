# Project Overview

## Title

**Privacy-First Data Loss Prevention (DLP) Prototype**

## Problem

People may accidentally share documents containing personal or confidential information. Manually checking every document is slow, and sensitive values can be exposed in the review process.

## Aim

Build a local-first prototype that identifies common sensitive information in a document, displays redacted findings, estimates risk, and recommends an action.

## Objectives

1. Accept a document and extract its text.
2. Detect email addresses, phone-like numbers, and labeled credentials using transparent rules.
3. Mask values in the results view.
4. Assign a simple risk level and recommend allow, mask, or block.
5. Evaluate detection quality with a labeled test dataset before adding machine learning.

## Current prototype scope

- Input: TXT, PDF, DOCX, and CSV files, up to 10 MB each; text-based PDFs only.
- Detection: email addresses, phone-like number strings, and credentials following labels such as `Password:` and `API_Key:`.
- Output: redacted text preview, masked findings, and a demonstration risk recommendation.
- Processing: text extraction in the Streamlit session and scan through a local FastAPI service; no database or external AI service.

## Next extensions

- Evaluate current detection rules on a labeled synthetic dataset before claiming accuracy.
- Add OCR for image-only PDFs if it is needed for the project demonstration.
- Add patterns for credentials and financial identifiers with careful validation.
- Add named-entity recognition for names, organizations, and locations.
- Compare a TF-IDF plus Logistic Regression classifier against a rule-only baseline.
- Add an audit report that stores counts and decisions without storing original sensitive values.

## Evaluation plan

Create a small labeled dataset and report precision, recall, F1 score, and a confusion matrix for each detector. Include false positives and false negatives in the discussion. Test with synthetic examples rather than real personal documents.

## Limitations

Pattern matching is approximate. A phone-like number is not necessarily a phone number, and formats vary by country. This prototype is for education and demonstration; it is not a substitute for an organization's security controls.
