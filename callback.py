import requests
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

GUVI_CALLBACK_ENDPOINT = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_result_to_guvi(session_summary: Dict[str, Any]) -> bool:
    """
    Send final engagement result to GUVI evaluation endpoint.
    
    Returns:
        True if successful, False otherwise
    """
    payload = {
        "sessionId": session_summary["sessionId"],
        "scamDetected": session_summary["scamDetected"],
        "totalMessagesExchanged": session_summary["totalMessagesExchanged"],
        "extractedIntelligence": session_summary["extractedIntelligence"],
        "agentNotes": session_summary["agentNotes"]
    }
    
    try:
        logger.info(f"Sending GUVI callback for session {session_summary['sessionId']}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            GUVI_CALLBACK_ENDPOINT,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ GUVI callback sent successfully for session {session_summary['sessionId']}")
            logger.debug(f"Response: {response.text}")
            return True
        else:
            logger.error(f"❌ GUVI callback failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ GUVI callback request error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during GUVI callback: {e}")
        return False
