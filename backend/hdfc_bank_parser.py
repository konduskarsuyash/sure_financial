from typing import Optional, Dict, Any, List
import io
import re
import pdfplumber

ISSUERS = {"HDFC BANK": "HDFC Bank"}
DATE_RE = r"\d{1,2}[-/]\s*[A-Za-z]{3}[-/,]\s*\d{4}"


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])


def detect_hdfc_issuer(text: str) -> Optional[str]:
    upper = text.upper()
    for key, name in ISSUERS.items():
        if key in upper:
            return name
    if "HDFC" in upper:
        return "HDFC Bank"
    return None


def extract_last4(text: str) -> Optional[str]:
    m = re.search(r"\d{6}X{6}(\d{4})", text)
    if m:
        return m.group(1)
    
    m2 = re.search(r"Credit Card No\.\s*\d{6}X+(\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    
    m3 = re.search(r"(?:ending|number|card)\D{0,10}(\d{4})", text, re.I)
    if m3:
        return m3.group(1)
    
    return None


def extract_card_type(text: str) -> Optional[str]:
    m = re.search(r"(UPI RuPay Biz Credit Card|RuPay|Visa|Mastercard|Master\s?Card|Amex|American Express)", text, re.I)
    if m:
        return m.group(1).strip()
    
    m2 = re.search(r"(\w+\s+\w+)\s+Credit Card Statement", text, re.I)
    if m2:
        return m2.group(1).strip()
    
    return None


def extract_billing_period(text: str) -> Optional[str]:
    m = re.search(r"Billing Period\s+(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})\s*-\s*(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text, re.I)
    if m:
        return f"{m.group(1)} - {m.group(2)}"
    
    m2 = re.search(r"(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})\s*-\s*(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text)
    if m2:
        return f"{m2.group(1)} - {m2.group(2)}"
    
    return None


def extract_statement_date(text: str) -> Optional[str]:
    m = re.search(r"Statement Date\s+(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text, re.I)
    if m:
        return m.group(1)
    
    return None


def extract_due_date_hdfc(text: str) -> Optional[str]:
    m = re.search(r"DUE DATE\s+(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text, re.I)
    if m:
        return m.group(1)
    
    m2 = re.search(r"(?:Payment Due Date|Due Date)\s+(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text, re.I)
    if m2:
        return m2.group(1)
    
    m3 = re.search(r"due[^\d]{0,10}(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})", text, re.I)
    return m3.group(1) if m3 else None


def extract_gstin(text: str) -> Optional[str]:
    m = re.search(r"GSTIN[:\s]*([\dA-Z]+)", text, re.I)
    if m:
        return m.group(1)
    return None


def extract_alternate_account_number(text: str) -> Optional[str]:
    m = re.search(r"Alternate Account Number\s+([\d]+)", text, re.I)
    if m:
        return m.group(1)
    return None



def parse_hdfc_bank(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_from_pdf_bytes(pdf_bytes)

    fields = {
        "issuer": detect_hdfc_issuer(text),
        "card_last4": extract_last4(text),
        "card_type": extract_card_type(text),
        "billing_period": extract_billing_period(text),
        "statement_date": extract_statement_date(text),
        "gstin": extract_gstin(text),
        "alternate_account_number": extract_alternate_account_number(text),
    }

    fields["confidence"] = round(sum(v is not None for v in fields.values()) / len(fields), 2)
    fields["raw_text_snippet"] = text[:800]

    return fields

