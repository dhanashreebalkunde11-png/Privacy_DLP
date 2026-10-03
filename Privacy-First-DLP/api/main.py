"""Local REST API endpoints used by the Streamlit front end."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from modules.dlp_service import scan_document


app = FastAPI(
    title="Privacy-First DLP API",
    description="Local API for scanning text for common sensitive-data patterns.",
    version="0.1.0",
)


class ScanRequest(BaseModel):
    text: str = Field(min_length=1, max_length=200_000)

    class Config:
        extra = "forbid"


class Finding(BaseModel):
    type: str
    masked: str
    risk: str
    start: int
    end: int


class ScanResponse(BaseModel):
    findings: list[Finding]
    finding_count: int
    scanned_characters: int
    redacted_text: str
    risk_score: int
    decision: str
    reason: str


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple endpoint for checking whether the local API is running."""
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
def scan(request: ScanRequest) -> dict:
    """Return masked findings and a demonstration risk recommendation."""
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Text must contain at least one non-whitespace character.")
    return scan_document(request.text)
