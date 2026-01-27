import re
from typing import Dict, List, Any

def merge_unique(existing: List[str], new: List[str]) -> List[str]:
    """Merge two lists and remove duplicates."""
    return list(set(existing + new))

def validate_upi(upi: str) -> bool:
    """Validate UPI ID format: name@bank"""
    return bool(re.match(r'^[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}$', upi))

def validate_phone(phone: str) -> bool:
    """Validate Indian phone format."""
    # Remove spaces and common formatting
    cleaned = phone.replace(" ", "").replace("-", "")
    return bool(re.match(r'^(\+91|0)?[6-9]\d{9}$', cleaned))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    return bool(re.match(r'^https?://[^\s]+$', url))

def validate_account(account: str) -> bool:
    """Validate account number (9-18 digits, not a phone number)."""
    if not re.match(r'^\d{9,18}$', account):
        return False
    # Exclude if it looks like a phone
    if re.match(r'^[6-9]\d{9}$', account):
        return False
    return True

def update_extracted_intelligence(session: Dict[str, Any], agent_extract: Dict[str, List[str]], message_text: str):
    """
    Update session with extracted intelligence.
    Validates extracted data before adding.
    """
    ei = session["extractedIntelligence"]
    
    # Validate and add UPI IDs
    valid_upis = [u for u in agent_extract.get("upi", []) if validate_upi(u)]
    ei["upiIds"] = merge_unique(ei["upiIds"], valid_upis)
    
    # Validate and add bank accounts
    valid_accounts = [a for a in agent_extract.get("accounts", []) if validate_account(a)]
    ei["bankAccounts"] = merge_unique(ei["bankAccounts"], valid_accounts)
    
    # Validate and add URLs
    valid_urls = [u for u in agent_extract.get("urls", []) if validate_url(u)]
    ei["phishingLinks"] = merge_unique(ei["phishingLinks"], valid_urls)
    
    # Validate and add phone numbers
    valid_phones = [p for p in agent_extract.get("phones", []) if validate_phone(p)]
    ei["phoneNumbers"] = merge_unique(ei["phoneNumbers"], valid_phones)
    
    # Extract suspicious keywords from message
    keywords = ["urgent", "verify", "account", "send now", "kyc", "block", "suspended", 
                "immediately", "otp", "upi", "transfer", "confirm", "click here", "link"]
    found = [kw for kw in keywords if kw in message_text.lower()]
    ei["suspiciousKeywords"] = merge_unique(ei["suspiciousKeywords"], found)

def update_agent_notes(session: Dict[str, Any], note: str):
    """Update agent notes with latest observation."""
    if note:
        if session["agentNotes"]:
            session["agentNotes"] += " | " + note
        else:
            session["agentNotes"] = note

def get_intelligence_summary(intelligence: Dict[str, Any]) -> str:
    """Generate a summary of extracted intelligence for agent notes."""
    summaries = []
    
    if intelligence["upiIds"]:
        summaries.append(f"UPI IDs: {', '.join(intelligence['upiIds'])}")
    if intelligence["bankAccounts"]:
        summaries.append(f"Bank accounts: {', '.join(intelligence['bankAccounts'])}")
    if intelligence["phishingLinks"]:
        summaries.append(f"Suspicious links: {', '.join(intelligence['phishingLinks'])}")
    if intelligence["phoneNumbers"]:
        summaries.append(f"Phone numbers: {', '.join(intelligence['phoneNumbers'])}")
    if intelligence["suspiciousKeywords"]:
        summaries.append(f"Keywords: {', '.join(set(intelligence['suspiciousKeywords']))}")
    
    return " | ".join(summaries) if summaries else "Gathering intelligence..."