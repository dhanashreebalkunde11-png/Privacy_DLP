import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)"
)

# Supports:
# Password: MyPassword123
# Password = MyPassword123
# Password
# MyPassword123
PASSWORD_PATTERN = re.compile(
    r"\b(?:password|passwd|pwd)\s*(?::|=|\n)\s*([^\s,;]+)",
    re.IGNORECASE
)

# Supports:
# API_Key: ABC123
# API_Key = ABC123
# API_Key
# ABC123fc
API_KEY_PATTERN = re.compile(
    r"\b(?:api[\_ -]?key|access[\_ -]?token|secret[\_ -]?key)"
    r"\s*(?::|=|\n)\s*([^\s,;]+)",
    re.IGNORECASE
)


def mask_email(value: str) -> str:
    local, separator, domain = value.partition("@")

    if not separator:
        return "*" * len(value)

    return f"{local[:1]}{'*' * max(3, len(local) - 1)}@{domain}"


def mask_phone(value: str) -> str:
    digits_seen = 0
    digit_count = sum(character.isdigit() for character in value)

    output = []

    for character in value:
        if character.isdigit():
            digits_seen += 1

            if digits_seen > digit_count - 2:
                output.append(character)
            else:
                output.append("*")
        else:
            output.append(character)

    return "".join(output)


def mask_secret(value: str) -> str:
    # Credentials should not reveal a recognizable suffix in the results.
    return "*" * max(8, len(value))


def detect_sensitive_data(text: str) -> list[dict[str, str | int]]:
    findings = []
    protected_spans = []

    # Password and API key detection
    for label, pattern in (
        ("Password", PASSWORD_PATTERN),
        ("API key", API_KEY_PATTERN),
    ):
        for match in pattern.finditer(text):

            start, end = match.span(1)

            value = match.group(1).rstrip(".])}")
            end = start + len(value)

            if not value:
                continue

            protected_spans.append((start, end))

            if label == "Password":
                masked = "*" * max(8, len(value))
            else:
                masked = mask_secret(value)

            findings.append({
                "type": label,
                "masked": masked,
                "risk": "Critical",
                "start": start,
                "end": end,
            })

    # Email detection. Credential matches take precedence because masking an
    # email exposes its domain, which is too weak for a credential value.
    email_spans = []
    for match in EMAIL_PATTERN.finditer(text):
        if any(
            match.start() < end and match.end() > start
            for start, end in protected_spans
        ):
            continue

        email_spans.append((match.start(), match.end()))

        findings.append({
            "type": "Email",
            "masked": mask_email(match.group()),
            "risk": "Medium",
            "start": match.start(),
            "end": match.end(),
        })

    # Do not count digit-only email names as phone numbers. This also keeps
    # redaction spans disjoint so one lower-priority match cannot weaken another.
    protected_spans.extend(email_spans)
    for match in PHONE_PATTERN.finditer(text):

        if any(
            match.start() < end and match.end() > start
            for start, end in protected_spans
        ):
            continue

        findings.append({
            "type": "Phone-like number",
            "masked": mask_phone(match.group()),
            "risk": "Medium",
            "start": match.start(),
            "end": match.end(),
        })

    return sorted(
        findings,
        key=lambda item: item["start"]
    )


def redact_text(
    text: str,
    findings: list[dict[str, str | int]]
) -> str:

    redacted = text

    for finding in sorted(
        findings,
        key=lambda item: item["start"],
        reverse=True
    ):
        redacted = (
            redacted[:finding["start"]]
            + finding["masked"]
            + redacted[finding["end"]:]
        )

    return redacted
