"""Backend orchestration: detection, risk scoring, and a suggested decision."""

from modules.regex_detector import detect_sensitive_data, redact_text


def scan_document(text: str) -> dict:
    """Scan text and return masked findings plus a simple risk recommendation."""
    findings = detect_sensitive_data(text)
    # Demonstration weights only; these are not calibrated security scores.
    weights = {"Email": 20, "Phone-like number": 15, "Password": 50, "API key": 50}
    raw_score = sum(weights[item["type"]] for item in findings)
    risk_score = min(raw_score, 100)

    has_credential = any(item["risk"] == "Critical" for item in findings)
    if has_credential or risk_score >= 70:
        decision, reason = "BLOCK", "A credential or several potentially sensitive values were found. Review before sharing."
    elif risk_score > 0:
        decision, reason = "MASK", "Potentially sensitive values were found. Mask them before sharing."
    else:
        decision, reason = "ALLOW", "No supported patterns were detected; this does not guarantee the text is safe."

    return {
        "findings": findings,
        "finding_count": len(findings),
        "scanned_characters": len(text),
        "redacted_text": redact_text(text, findings),
        "risk_score": risk_score,
        "decision": decision,
        "reason": reason,
    }
