from typing import Optional, Dict, Any
import io
import re
import pdfplumber

ISSUERS = {
    "AXIS BANK": "Axis Bank",
}

CARD_TYPES_RE = re.compile(r"\b(Visa|Master\s?Card|Mastercard|American Express|Amex|Discover)\b", re.I)
LAST4_RE = re.compile(r"(?:Card(?:\s*No\.?| number| ending| account)?\D{0,10}(\d{4}))", re.I)
DATE_RE = r"\d{1,2}/\d{1,2}/\d{2,4}"
BILLING_PERIOD_RE = re.compile(rf"(?:Statement Period|Billing Period)[^\d]*(?:{DATE_RE}\s*[-–]\s*{DATE_RE})", re.I)
DATE_RANGE_RE = re.compile(rf"({DATE_RE})\s*[-–]\s*({DATE_RE})")

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def detect_axis_issuer(text: str) -> Optional[str]:
    upper = text.upper()
    for key, name in ISSUERS.items():
        if re.search(rf"\b{re.escape(key)}\b", upper):
            return name
    m = re.search(r"([A-Za-z ]+) Credit Card Statement", text, re.I)
    if m:
        return m.group(1).strip()
    return None

def extract_last4(text: str) -> Optional[str]:
    masked_patterns = [
        re.compile(r"\b\d{4}\d{2}\*+\d{4}\b"),
        re.compile(r"\b\d{4}\*+\d{4}\b"),
        re.compile(r"\*+\d{4}\b"),
        re.compile(r"\b\d{6}\*+\d{4}\b")
    ]
    for pat in masked_patterns:
        m = pat.search(text)
        if m:
            return re.search(r"(\d{4})\b", m.group(0)).group(1)

    near_pattern = re.compile(r"(?:card|card no|card number|acct|account|ending)[^\d]{0,40}(\d{4})", re.I)
    near_matches = near_pattern.findall(text)
    if near_matches:
        return near_matches[-1]

    all4 = re.findall(r"\b(\d{4})\b", text)
    if all4:
        filtered = [s for s in all4 if not re.match(r"20\d{2}$", s)]
        if filtered:
            return filtered[-1]
        return all4[-1]
    return None

def extract_card_type(text: str) -> Optional[str]:
    m = CARD_TYPES_RE.search(text)
    if not m:
        return None
    val = m.group(1).lower()
    mapping = {
        "master card": "Mastercard",
        "mastercard": "Mastercard",
        "amex": "American Express",
        "american express": "American Express",
    }
    return mapping.get(val, val.title())

def extract_billing_period(text: str) -> Optional[str]:
    m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})\s*[-–]\s*(\d{1,2}/\d{1,2}/\d{2,4})", text)
    if m:
        return f"{m.group(1)} - {m.group(2)}"

    for label in ["Statement Period", "Billing Period", "Cycle"]:
        m = re.search(rf"{label}[^0-9]*([\d/ -]+)", text, re.I)
        if m:
            return m.group(1).strip()

    return None

def extract_due_date_axis(text: str) -> Optional[str]:
    m = re.search(r"(?:Payment Due|Due Date)[^\d]{0,10}(\d{1,2}/\d{1,2}/\d{2,4})", text, re.I)
    if m:
        return m.group(1)

    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "payment due" in line.lower():
            for j in range(i + 1, min(i + 3, len(lines))):
                dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", lines[j])
                if dates:
                    if len(dates) >= 3:
                        return dates[2]
                    elif len(dates) >= 2:
                        return dates[1]
                    else:
                        return dates[0]
    return None

def parse_axis_bank(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_from_pdf_bytes(pdf_bytes)

    fields = {
        "issuer": detect_axis_issuer(text),
        "card_last4": extract_last4(text),
        "card_type": extract_card_type(text),
        "billing_period": extract_billing_period(text),
        "payment_due_date": extract_due_date_axis(text),
    }

    confidence = round(sum(v is not None for v in fields.values()) / len(fields), 2)
    fields["confidence"] = confidence
    fields["raw_text_snippet"] = text[:800]

    return fields