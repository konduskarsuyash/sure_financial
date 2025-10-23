from typing import Optional, Dict, Any
import io
import re
import pdfplumber

ISSUERS = {"ICICI BANK": "ICICI Bank"}
DATE_RE = r"\d{1,2}/\d{1,2}/\d{2,4}"

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def detect_icici_issuer(text: str) -> Optional[str]:
    upper = text.upper()
    for key, name in ISSUERS.items():
        if key in upper:
            return name
    m = re.search(r"ICICI.*Credit Card Statement", upper)
    if m:
        return "ICICI Bank"
    return None

def extract_last4(text: str) -> Optional[str]:
    m = re.search(r"\d{4}X{4,8}(\d{4})", text)
    if m:
        return m.group(1)
    m2 = re.search(r"(?:ending|number|account)\D{0,10}(\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    return None

def extract_card_type(text: str) -> Optional[str]:
    m = re.search(r"\b(Visa|Mastercard|Master\s?Card|Amex|American Express|RuPay)\b", text, re.I)
    return m.group(1).title() if m else None

def extract_billing_period(text: str) -> Optional[str]:
    m = re.search(r"Statement period\s*[:\-]?\s*([A-Za-z0-9 ,/]+to[A-Za-z0-9 ,/]+)", text, re.I)
    if m:
        return m.group(1).strip()
    m2 = re.search(rf"({DATE_RE})\s*(?:to|–|-)\s*({DATE_RE})", text)
    if m2:
        return f"{m2.group(1)} - {m2.group(2)}"
    return None

def extract_due_date_icici(text: str) -> Optional[str]:
    m = re.search(r"Payment Due Date[^\d]{0,10}(\d{1,2}/\d{1,2}/\d{2,4})", text, re.I)
    if m:
        return m.group(1)

    m2 = re.findall(r"([A-Za-z]+ \d{1,2}, \d{4})", text)
    if len(m2) >= 2:
        return m2[1]

    m3 = re.search(r"due.{0,10}(\d{1,2}/\d{1,2}/\d{2,4})", text, re.I)
    return m3.group(1) if m3 else None

def parse_icici_bank(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_from_pdf_bytes(pdf_bytes)

    fields = {
        "issuer": detect_icici_issuer(text),
        "card_last4": extract_last4(text),
        "card_type": extract_card_type(text),
        "billing_period": extract_billing_period(text),
        "payment_due_date": extract_due_date_icici(text),
    }

    fields["confidence"] = round(sum(v is not None for v in fields.values()) / len(fields), 2)
    fields["raw_text_snippet"] = text[:800]

    return fields