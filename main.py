from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import openai
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env secrets
load_dotenv()
API_KEY = os.getenv("API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Local modules
from detector import detect_scam
from session_store import (
    get_session, update_session, mark_session_engaged, mark_session_complete,
    get_engagement_duration, mark_callback_sent, has_callback_been_sent,
    get_session_summary
)
from intel_store import update_extracted_intelligence, update_agent_notes, get_intelligence_summary
from agent import generate_agent_reply, extract_intelligence, should_continue_engagement
from callback import send_final_result_to_guvi

# Init FastAPI
app = FastAPI(title="Agentic Honeypot", version="1.0")

# ---- Pydantic models for request validation ----

class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class InboundRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Metadata] = None

# ---- Main Endpoint ----
@app.post("/inbound")
async def receive_message(
    payload: InboundRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """
    Main honeypot endpoint that processes incoming scam messages.
    
    Flow:
    1. Authenticate with x-api-key
    2. Detect scam intent
    3. If scam detected, engage agent
    4. Extract intelligence
    5. When engagement ends, send GUVI callback (only once)
    """
    
    # ✅ Authentication
    if x_api_key != API_KEY:
        logger.warning(f"Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    session_id = payload.sessionId
    message_text = payload.message.text
    channel = payload.metadata.channel if payload.metadata else "SMS"
    locale = payload.metadata.locale if payload.metadata else "IN"
    language = payload.metadata.language if payload.metadata else "English"
    
    logger.info(f"[{session_id}] Received message from {payload.message.sender}: {message_text[:50]}...")
    
    # 1️⃣ Detect Scam
    scam_detected = detect_scam(message_text)
    logger.info(f"[{session_id}] Scam detected: {scam_detected}")
    
    # 2️⃣ Load or create session
    session = get_session(session_id)
    
    # 3️⃣ Update session with incoming message
    incoming_message = {
        "sender": payload.message.sender,
        "text": message_text,
        "timestamp": payload.message.timestamp or datetime.utcnow().isoformat()
    }
    session = update_session(session_id, incoming_message)
    logger.info(f"[{session_id}] Total messages in session: {session['totalMessages']}")
    
    # 4️⃣ Agent engagement logic
    agent_reply = None
    extracted_intel = {
        "upi": [],
        "accounts": [],
        "urls": [],
        "phones": []
    }
    
    if scam_detected and not session["agentEngaged"]:
        # First detection - activate agent
        logger.info(f"[{session_id}] Activating agent for scam engagement")
        mark_session_engaged(session_id)
    
    if session["agentEngaged"]:
        # Agent is engaged - process with LLM
        logger.info(f"[{session_id}] Agent processing message")
        
        try:
            # Generate natural reply
            agent_reply = generate_agent_reply(session, channel=channel, locale=locale)
            logger.info(f"[{session_id}] Agent reply: {agent_reply[:60]}...")
            
            # Extract intelligence from latest message
            extracted_intel = extract_intelligence(session, message_text)
            logger.info(f"[{session_id}] Extracted intelligence: {extracted_intel}")
            
            # Update session with extracted data
            update_extracted_intelligence(session, extracted_intel, message_text)
            
            # Update agent notes with summary
            intelligence_note = get_intelligence_summary(session["extractedIntelligence"])
            update_agent_notes(session, intelligence_note)
            
            # Add agent reply to conversation history
            session["conversationHistory"].append({
                "sender": "user",  # This is our agent's reply (from scammer's perspective)
                "text": agent_reply,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[{session_id}] Agent processing error: {e}")
            agent_reply = "Can you please explain that again? I'm a bit confused."
    
    # 5️⃣ Determine if engagement should continue or end
    should_continue = should_continue_engagement(session)
    
    engagement_complete = not should_continue
    if engagement_complete:
        logger.info(f"[{session_id}] Engagement complete - terminating conversation")
        mark_session_complete(session_id)
    
    # 6️⃣ Send GUVI callback if engagement is complete and not already sent
    callback_sent = False
    if engagement_complete and scam_detected and not has_callback_been_sent(session_id):
        logger.info(f"[{session_id}] Preparing to send GUVI callback")
        session_summary = get_session_summary(session_id)
        if send_final_result_to_guvi(session_summary):
            mark_callback_sent(session_id)
            callback_sent = True
            logger.info(f"[{session_id}] ✅ GUVI callback sent successfully")
        else:
            logger.error(f"[{session_id}] ❌ GUVI callback failed")
    
    # 7️⃣ Build response according to spec
    engagement_duration = get_engagement_duration(session_id)
    
    response = {
        "status": "success",
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_duration,
            "totalMessagesExchanged": session["totalMessages"]
        },
        "extractedIntelligence": session["extractedIntelligence"],
        "agentNotes": session["agentNotes"],
        "agentReply": agent_reply,  # Include agent reply for Mock Scammer API
        "engagementComplete": engagement_complete,
        "callbackSent": callback_sent
    }
    
    logger.info(f"[{session_id}] Sending response: scamDetected={scam_detected}, "
                f"totalMessages={session['totalMessages']}, "
                f"agentEngaged={session['agentEngaged']}")
    
    return response

# ---- Health check endpoint ----
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ---- Dashboard endpoints ----
@app.get("/")
async def root():
    """Serve React dashboard."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r') as f:
            return HTMLResponse(content=f.read())
    return {"message": "Dashboard frontend not found"}


@app.get("/dashboard")
async def dashboard():
    """Serve React dashboard (legacy route)."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Dashboard frontend not found"}


# ---- Startup event ----
@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup."""
    if not API_KEY:
        logger.warning("⚠️ API_KEY not set in environment")
    if not openai.api_key:
        logger.warning("⚠️ OPENAI_API_KEY not set in environment")
    logger.info("✅ Agentic Honeypot started")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)