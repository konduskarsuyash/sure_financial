from typing import Dict, Any, Optional
import io
import pdfplumber

from axis_bank_parser import parse_axis_bank
from icici_bank_parser import parse_icici_bank
from kotak_bank_parser import parse_kotak_bank
from hdfc_bank_parser import parse_hdfc_bank
from utils import detect_issuer

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Simple reusable extractor for detection only."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])


def route_parser(pdf_bytes: bytes, issuer_hint: Optional[str] = None) -> Dict[str, Any]:
    """Select the correct parser based on detected or provided issuer."""
    text = extract_text_from_pdf_bytes(pdf_bytes)

    issuer = issuer_hint or detect_issuer(text)

    if not issuer:
        return {"error": "Unable to detect issuer. Please specify manually.", "confidence": 0}

    issuer_lower = issuer.lower()

    if "axis" in issuer_lower:
        print('axis parser called')
        return parse_axis_bank(pdf_bytes)
    elif "icici" in issuer_lower:
        print('icici parser called')
        return parse_icici_bank(pdf_bytes)
    elif "kotak" in issuer_lower:
        print('kotak parser called')
        return parse_kotak_bank(pdf_bytes)
    elif "hdfc" in issuer_lower:
        print('hdfc parser called')
        return parse_hdfc_bank(pdf_bytes)
    else:
        return {"error": f"Issuer '{issuer}' not supported yet.", "confidence": 0}

