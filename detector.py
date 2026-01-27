import re

SCAM_KEYWORDS = [
    # ========== BANKING/KYC FRAUD ==========
    "verify", "verify now", "verify identity", "verify account", "verify immediately",
    "account", "account suspension", "account blocked", "account disabled",
    "suspend", "suspended", "blocking", "blocked", "disable",
    "urgent", "urgently", "immediately", "asap", "now",
    "otp", "share otp", "send otp", "otp needed",
    "kyc", "kyc verification", "kyc incomplete", "kyc update", "kyc failed",
    "pan", "aadhaar", "pan number", "aadhaar number",
    "rbi", "rbi notice", "rbi alert", "rbi warning",
    "sbi alert", "sbi notice", "bank alert", "bank notice",
    "reserve bank", "bank account", "debit card", "credit card",
    "card disabled", "card blocked", "card cancelled",
    "unusual activity", "suspicious activity", "unauthorized transaction",
    "click here", "click link", "download form", "download app",
    "linked", "attachment", "attached form", "attached document",
    "update now", "update immediately", "confirm details",
    
    # ========== DELIVERY/REFUND SCAMS ==========
    "package", "parcel", "shipment", "delivery",
    "customs", "customs duty", "import tax",
    "courier", "tracking", "reschedule",
    "refund", "refund pending", "refund initiated",
    "payment required", "pay now", "payment needed",
    "incorrect address", "delivery failed", "delivery failed",
    "confirm address", "update address",
    "amazon", "flipkart", "swiggy", "zomato",
    
    # ========== JOB/PRIZE/LOAN SCAMS ==========
    "congratulations", "won", "prize", "prize money",
    "contest", "kaun banega crorepati", "kbc",
    "lottery", "lottery winner", "lucky draw",
    "job offer", "job opening", "job opportunity",
    "work from home", "part time", "part-time",
    "earn money", "earning", "income", "salary",
    "₹", "rupees", "lakh", "crore", "rs", "inr",
    "loan", "loan approved", "credit", "instant credit",
    "processing fee", "application fee", "fee required",
    "no skills needed", "no experience needed", "no qualification",
    
    # ========== INVESTMENT/CRYPTO SCAMS ==========
    "double money", "double your money", "multiply money",
    "crypto", "bitcoin", "ethereum", "nft",
    "blockchain", "trading", "trader",
    "investment", "invest now", "investment opportunity",
    "returns", "monthly return", "daily return", "guaranteed return",
    "fixed deposit", "fd", "fd scheme",
    "interest rate", "interest", "high interest",
    "roi", "profit", "guaranteed profit",
    "govt scheme", "government scheme", "scheme",
    "limited slots", "limited time", "limited offers",
    
    # ========== ROMANCE/SOCIAL ENGINEERING ==========
    "friend", "friends", "friendship",
    "whatsapp", "telegram", "signal",
    "stuck abroad", "stuck", "emergency",
    "send money", "send funds", "need money",
    "paytm", "google pay", "phonepe", "bank transfer",
    "emi", "payment method", "payment option",
    "resend money", "transfer back", "send back",
    "personal help", "urgent help", "immediate help",
    
    # ========== THREATENING/URGENT SCAMS ==========
    "sim deactivate", "deactivated", "deactivation",
    "income tax", "tax raid", "raid", "tax dues",
    "cyber cell", "cyber crime", "police complaint",
    "complaint filed", "case registered", "fir",
    "resolve", "resolve immediately", "resolve now",
    "clear dues", "pay fine", "pay penalty",
    "action will be taken", "legal action", "court order",
    
    # ========== GENERAL SCAM INDICATORS ==========
    "send upi", "upi details", "upi id", "upi handle",
    "click link", "malicious link", "phishing",
    "link", "url", "bit.ly",
    "transfer", "transfer money", "transfer funds",
    "share details", "provide details", "give details",
    "confirm", "confirm account", "confirm details",
    "update", "update now", "update details",
    "validate", "validate account", "validate identity",
    "authenticate", "authentication", "two-factor",
    "dmme", "dm me", "call me", "contact me",
    "password", "pin", "cvv", "cvv2",
    "mobile number", "phone number", "contact number"
]

def detect_scam(message_text: str) -> bool:
    text = message_text.lower()
    score = 0

    # Keyword scoring
    for keyword in SCAM_KEYWORDS:
        if keyword in text:
            score += 1

    # Pattern scoring (e.g., UPI IDs, links)
    if re.search(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text):
        score += 2  # UPI ID pattern

    if re.search(r"https?://[^\s]+", text):
        score += 2  # Phishing link

    if re.search(r"\b\d{9,18}\b", text):
        score += 2  # Possible account number

    # Set threshold
    return score >= 2
