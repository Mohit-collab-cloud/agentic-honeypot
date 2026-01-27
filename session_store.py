from datetime import datetime
from typing import Dict, Optional

# In-memory session store: sessionId → session data
SESSIONS: Dict[str, Dict] = {}

def get_session(session_id: str) -> Dict:
    """Get or create a session."""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "sessionId": session_id,
            "conversationHistory": [],
            "agentEngaged": False,
            "startTime": datetime.utcnow(),
            "endTime": None,
            "totalMessages": 0,
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "agentNotes": "",
            "callbackSent": False  # Track if final callback was sent
        }
    return SESSIONS[session_id]

def update_session(session_id: str, new_message: dict) -> Dict:
    """Add a message to session and increment counter."""
    session = get_session(session_id)
    session["conversationHistory"].append(new_message)
    session["totalMessages"] += 1
    return session

def mark_session_engaged(session_id: str):
    """Mark session as agent-engaged."""
    session = get_session(session_id)
    session["agentEngaged"] = True

def mark_session_complete(session_id: str):
    """Mark session as complete and set end time."""
    session = get_session(session_id)
    session["endTime"] = datetime.utcnow()

def get_engagement_duration(session_id: str) -> int:
    """Get engagement duration in seconds."""
    session = get_session(session_id)
    if session["endTime"]:
        delta = session["endTime"] - session["startTime"]
    else:
        delta = datetime.utcnow() - session["startTime"]
    return int(delta.total_seconds())

def mark_callback_sent(session_id: str):
    """Mark that the GUVI callback has been sent for this session."""
    session = get_session(session_id)
    session["callbackSent"] = True

def has_callback_been_sent(session_id: str) -> bool:
    """Check if callback was already sent (prevent duplicate callbacks)."""
    session = get_session(session_id)
    return session["callbackSent"]

def get_session_summary(session_id: str) -> Dict:
    """Get a summary of the session for final reporting."""
    session = get_session(session_id)
    return {
        "sessionId": session_id,
        "scamDetected": session["agentEngaged"],  # If agent was engaged, scam was detected
        "totalMessagesExchanged": session["totalMessages"],
        "engagementDurationSeconds": get_engagement_duration(session_id),
        "extractedIntelligence": session["extractedIntelligence"],
        "agentNotes": session["agentNotes"]
    }
