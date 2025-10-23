import re
from typing import Optional

ISSUERS = {
    "CHASE": "Chase",
    "AMERICAN EXPRESS": "American Express",
    "AMEX": "American Express",
    "CITI": "Citi",
    "CITIBANK": "Citi",
    "BANK OF AMERICA": "Bank of America",
    "CAPITAL ONE": "Capital One",
    "AXIS BANK": "Axis Bank",
    "HDFC BANK": "HDFC Bank",
    "ICICI BANK": "ICICI Bank",
    "SBI": "State Bank of India",
    "KOTAK": "Kotak Mahindra Bank",
}

def preprocess_text(text: str) -> str:
    """Clean up common PDF artifacts and normalize spacing."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def detect_issuer(text: str) -> Optional[str]:
    """
    Detect the credit card issuer/bank based on text content.
    Improved to avoid false positives with card networks vs banks.
    """
    if not text:
        return None

    upper = text.upper()
    lines = upper.splitlines()

    if "ICICI" in upper or "ICICI BANK" in upper:
        return "ICICI Bank"
    
    card_networks = ["VISA", "MASTERCARD", "AMERICAN EXPRESS", "AMEX", "RUPAY", "DISCOVER"]
    

    for line in lines[:15]:
        if any(network in line for network in card_networks) and not any(bank in line for bank in ["BANK", "CITI", "CHASE", "ICICI", "HDFC", "AXIS", "KOTAK", "SBI"]):
            continue

        statement_indicators = ["CREDIT CARD", "STATEMENT", "ACCOUNT", "SUMMARY", "BILL"]
        if any(indicator in line for indicator in statement_indicators):
            for key, name in sorted(ISSUERS.items(), key=lambda kv: -len(kv[0])):
                if key in line:
                    return name


    bank_keys = [k for k in ISSUERS.keys() if "BANK" in k or k in ["CITI", "CHASE", "ICICI", "HDFC", "AXIS", "KOTAK", "SBI"]]
    for key in sorted(bank_keys, key=len, reverse=True):
        if re.search(r"\b" + re.escape(key) + r"\b", upper):
            return ISSUERS[key]
    
    for key, name in sorted(ISSUERS.items(), key=lambda kv: -len(kv[0])):

        if key in ["AMERICAN EXPRESS", "AMEX", "VISA", "MASTERCARD", "DISCOVER", "RUPAY"]:
            if not re.search(r"\b" + re.escape(key) + r".{0,20}CARD|CARD.{0,20}" + re.escape(key), upper):
                continue
        
        if re.search(r"\b" + re.escape(key) + r"\b", upper):
            return name

    icici_indicators = ["INFINITY", "CORAL", "SAPPHIRO", "RUBYX", "MMT", "MAKEMYTRIP", "EMERALDE"]
    for indicator in icici_indicators:
        if re.search(r"\b" + re.escape(indicator) + r"\b", upper):
            return "ICICI Bank"

    return None

def find_first_date(text: str) -> Optional[str]:
    """Extract the first date pattern (useful for fallback date detection)."""
    m = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
    return m.group(0) if m else None

def find_all_dates(text: str) -> list[str]:
    """Extract all date-like patterns from text."""
    return re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", text)