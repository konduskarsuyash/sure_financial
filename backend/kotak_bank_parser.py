from typing import Optional, Dict, Any
import io
import re
import pdfplumber

ISSUERS = {"KOTAK MAHINDRA BANK": "Kotak Mahindra Bank"}
DATE_RE = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def detect_kotak_issuer(text: str) -> Optional[str]:
    upper = text.upper()
    for key, name in ISSUERS.items():
        if key in upper:
            return name
    if "KOTAK" in upper:
        return "Kotak Mahindra Bank"
    return None

def extract_last4(text: str) -> Optional[str]:
    m = re.search(r"\d{4}\s*X{4,8}\s*X{0,4}\s*(\d{4})", text)
    if m:
        return m.group(1)
    m2 = re.search(r"Primary Card Number\s*\d{4}\s*X+\s*X+\s*(\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    m3 = re.search(r"(?:ending|number|card)\D{0,10}(\d{4})", text, re.I)
    if m3:
        return m3.group(1)
    return None

def extract_card_type(text: str) -> Optional[str]:
    m = re.search(r"\b(Visa|Mastercard|Master\s?Card|Amex|American Express|RuPay)\b", text, re.I)
    if m:
        return m.group(1).title()
    
    variant_pattern = r"(?:Feast Gold|Dream Different|Solitaire|Urbane Gold|PVR|Mojo Platinum|Royale Signature|Zen Signature|White Signature|League Platinum)"
    m2 = re.search(variant_pattern, text, re.I)
    if m2:
        return m2.group(0)
    
    return None

def extract_billing_period(text: str) -> Optional[str]:
    m = re.search(r"from\s+(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})\s+to\s+(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})", text, re.I)
    if m:
        return f"{m.group(1)} to {m.group(2)}"
    
    m2 = re.search(rf"({DATE_RE})\s*(?:to|–|-)\s*({DATE_RE})", text)
    if m2:
        return f"{m2.group(1)} to {m2.group(2)}"
    
    return None

def extract_statement_date(text: str) -> Optional[str]:
    m = re.search(r"Statement Date\s+(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})", text, re.I)
    if m:
        return m.group(1)
    
    m2 = re.search(r"Statement Date\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    
    return None

def extract_due_date_kotak(text: str) -> Optional[str]:
    m = re.search(r"(?:pay by|due date|payment due)\s+(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})", text, re.I)
    if m:
        return m.group(1)
    
    m2 = re.search(r"(?:pay by|due date|payment due)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    
    m3 = re.search(r"due[^\d]{0,10}(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text, re.I)
    return m3.group(1) if m3 else None

def extract_total_amount_due(text: str) -> Optional[float]:
    m = re.search(r"Total Amount Due.*?Rs\.?\s*([\d,]+\.?\d*)", text, re.I)
    if m:
        amount_str = m.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            pass
    return None

def extract_minimum_amount_due(text: str) -> Optional[float]:
    m = re.search(r"Minimum Amount Due.*?Rs\.?\s*([\d,]+\.?\d*)", text, re.I)
    if m:
        amount_str = m.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            pass
    return None

def extract_credit_limit(text: str) -> Optional[float]:
    m = re.search(r"Total Credit Limit[:\s]*Rs\.?\s*([\d,]+\.?\d*)", text, re.I)
    if m:
        amount_str = m.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            pass
    return None

def extract_crn(text: str) -> Optional[str]:
    m = re.search(r"Customer Relationship Number[:\-\s]*([\d]+)", text, re.I)
    if m:
        return m.group(1)
    
    m2 = re.search(r"CRN[:\s]*([\d]+)", text, re.I)
    if m2:
        return m2.group(1)
    
    return None

def parse_kotak_bank(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_from_pdf_bytes(pdf_bytes)

    fields = {
        "issuer": detect_kotak_issuer(text),
        "card_last4": extract_last4(text),
        "card_type": extract_card_type(text),
        "billing_period": extract_billing_period(text),
        "credit_limit": extract_credit_limit(text),
        "crn": extract_crn(text),
    }

    fields["confidence"] = round(sum(v is not None for v in fields.values()) / len(fields), 2)
    fields["raw_text_snippet"] = text[:800]

    return fields