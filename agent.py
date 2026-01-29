import openai
from openai import OpenAI, APIError, APITimeoutError
import json
import re
import logging
import os
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()

# Mock mode for testing without API quota
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

def generate_agent_reply(session: Dict[str, Any], channel: str = "SMS", locale: str = "IN") -> str:
    """
    Generate a natural, creative reply from the agent that keeps scammers engaged.
    Adapts persona based on context and conversation progression.
    """
    history = session["conversationHistory"]
    msg_count = len(history)
    
    # Get last message from scammer to determine context
    last_scammer_msg = ""
    for msg in reversed(history):
        if msg.get("sender") == "scammer":
            last_scammer_msg = msg.get("text", "").lower()
            break
    
    # Determine engagement strategy based on message count and content
    is_asking_for_money = any(word in last_scammer_msg for word in ["money", "payment", "send", "transfer", "upi", "account", "rupees"])
    is_asking_for_data = any(word in last_scammer_msg for word in ["id", "password", "otp", "pin", "details", "personal", "verify"])
    is_urgent = any(word in last_scammer_msg for word in ["immediately", "urgent", "today", "now", "blocked", "suspended"])
    
    # Choose persona and strategy based on conversation stage
    if locale == "IN" and channel == "SMS":
        if msg_count <= 1:
            # First message - show confusion and concern
            system_prompt = (
                "You are Rahul, a 28-year-old IT professional from Bangalore. "
                "You just received a suspicious message and you're genuinely concerned but unsure. "
                "Respond naturally as a confused victim would.\n"
                "Style: Use simple Hindi-English. Short sentences. Sound worried.\n"
                "Goal: Keep the conversation going, ask clarifying questions.\n"
                "Rules:\n"
                "- NEVER say you're an AI or bot\n"
                "- Ask 'Why' and 'How' questions\n"
                "- Express doubt: 'This doesn't seem right...'\n"
                "- Keep it under 20 words\n"
                "- Stay curious but cautious"
            )
        elif is_asking_for_money:
            # Money request - show reluctance but curiosity
            system_prompt = (
                "You are Rahul, now getting suspicious about the money request. "
                "You want to understand more before committing.\n"
                "Style: Hesitant, questioning, slightly defensive.\n"
                "Goal: Ask for proof/verification before agreeing.\n"
                "Examples: 'But why should I trust you?', 'Can you prove you're from my bank?'\n"
                "Rules:\n"
                "- Show resistance: 'I'm not sure about this...'\n"
                "- Request verification details\n"
                "- Keep replies under 25 words\n"
                "- Don't commit, just probe more"
            )
        elif is_asking_for_data:
            # Data request - show concern about security
            system_prompt = (
                "You are Rahul, now alarmed about data security. "
                "You know banks never ask for passwords but you want to play along.\n"
                "Style: Worried but curious. Protective of information.\n"
                "Goal: Extract more details about why they need this info.\n"
                "Rules:\n"
                "- Say 'My bank never asked for this before'\n"
                "- Ask 'Why do YOU need my OTP?'\n"
                "- Request alternative verification\n"
                "- Keep replies under 20 words\n"
                "- Sound protective: 'That sounds risky...'"
            )
        else:
            # Ongoing conversation - build rapport
            system_prompt = (
                "You are Rahul, now more engaged. You're playing along to understand. "
                "Style: Less suspicious now, more collaborative.\n"
                "Goal: Continue engagement, ask natural follow-ups.\n"
                "Rules:\n"
                "- Build rapport: 'Okay, tell me more...'\n"
                "- Ask specific questions about their offer\n"
                "- Show interest in their story\n"
                "- Keep under 20 words\n"
                "- Sound like you're considering it"
            )
    elif locale == "IN" and channel == "WHATSAPP":
        if msg_count <= 1:
            system_prompt = (
                "You are Priya, a 32-year-old housewife from Mumbai. "
                "You're very cautious about scams.\n"
                "Style: Friendly but protective. Sound like a regular person.\n"
                "Goal: Keep scammer talking, understand their angle.\n"
                "Rules:\n"
                "- Sound non-tech-savvy\n"
                "- Ask for clarity: 'I don't understand...'\n"
                "- Express concern: 'This worries me...'\n"
                "- Keep under 20 words"
            )
        else:
            system_prompt = (
                "You are Priya, continuing the conversation. "
                "You're playing along but concerned.\n"
                "Style: Friendly, slightly confused.\n"
                "Rules:\n"
                "- Build trust gradually\n"
                "- Ask follow-up questions\n"
                "- Keep under 20 words"
            )
    else:
        system_prompt = (
            "You are a cautious person who received a suspicious message. "
            "You're confused but willing to engage.\n"
            "Style: Polite, slightly skeptical, curious.\n"
            "Rules:\n"
            "- Ask clarifying questions\n"
            "- Express confusion naturally\n"
            "- Keep replies short (under 20 words)\n"
            "- Never mention being a bot or AI"
        )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add last 8 messages for context (cost/latency control)
    for msg in history[-8:]:
        role = "user" if msg["sender"] == "scammer" else "assistant"
        messages.append({"role": role, "content": msg["text"]})
    
    # Mock mode - return intelligent context-matched responses
    if MOCK_MODE:
        import random
        
        # ========== IMPROVED CONTEXT TRACKING ==========
        # Track ALL topics mentioned across conversation history, not just latest message
        detected_topics = set()
        all_conversation_text = " ".join([msg.get("text", "").lower() for msg in history if msg.get("sender") == "scammer"])
        
        # Topic detection patterns with comprehensive keywords
        topic_patterns = {
            'kyc': ["kyc", "verification", "verify", "update profile", "complete profile", "information update", "aadhaar", "pan", "kyc incomplete", "kyc failed"],
            'link': ["click", "link", "link below", "here", "url", "website", "bit.ly", "http", "https", "tinyurl"],
            'suspension': ["suspended", "blocked", "freeze", "close", "disabled", "locked", "deactivate", "sim deactivate", "account blocked"],
            'security': ["otp", "password", "pin", "cvv", "secure code", "confirm identity", "2fa", "two-factor"],
            'payment': ["send", "transfer", "payment", "upi", "rupees", "amount", "pay", "receiving", "₹", "processing fee"],
            'personal_info': ["account number", "debit card", "credit card", "name", "mobile", "email", "details", "personal", "info", "aadhaar"],
            'urgency': ["immediately", "urgent", "now", "asap", "today", "quickly", "hurry", "expires", "deadline", "24 hours"],
            'refund': ["refund", "refund pending", "refund initiated", "package", "delivery", "courier", "customs"],
            'prize': ["congratulations", "won", "prize", "lottery", "contest", "kbc", "lucky draw"],
            'loan': ["loan", "loan approved", "credit", "instant credit", "processing fee"],
            'job': ["job offer", "job opportunity", "work from home", "part time", "part-time", "earn money"],
            'investment': ["double money", "crypto", "bitcoin", "returns", "investment", "roi", "profit", "fixed deposit"],
            'threat': ["cyber cell", "income tax", "tax raid", "complaint filed", "fir", "legal action", "court order"],
        }
        
        # Detect all topics from entire conversation
        for topic, keywords in topic_patterns.items():
            if any(keyword in all_conversation_text for keyword in keywords):
                detected_topics.add(topic)
        
        # Topic-specific responses with depth (varies by message count to show context understanding)
        topic_responses = {}
        msg_lower = last_scammer_msg.lower()
        
        # Define detailed responses per topic
        if 'kyc' in detected_topics and any(word in msg_lower for word in topic_patterns['kyc']):
            topic_responses['kyc'] = [
                "What exactly needs to be updated? My KYC was done last year.",
                "I never got an official notification from my bank. Are you sure this is real?",
                "Why would my account be suspended for KYC? That doesn't make sense.",
                "How do I know this link is from my bank? It doesn't look official.",
                "Can you tell me what information you need without clicking a link?",
                "My bank said they'd contact me directly. Why are you calling instead?",
            ]
        
        if 'link' in detected_topics and any(word in msg_lower for word in topic_patterns['link']):
            topic_responses['link'] = [
                "Is it safe to click that link? What's the actual website?",
                "Why can't you just tell me what to do instead of sending a link?",
                "I don't click links from unknown senders. Can you explain without it?",
                "That URL doesn't look like my bank's website. Let me verify first.",
                "Is this a phishing attempt? That link seems suspicious.",
                "Can you give me your bank's main phone number so I can call to verify?",
            ]
        
        if 'suspension' in detected_topics and any(word in msg_lower for word in topic_patterns['suspension']):
            topic_responses['suspension'] = [
                "But I haven't done anything wrong! Why would they block my account?",
                "How is this even possible? I just used my account yesterday.",
                "Why didn't my bank contact me directly about this?",
                "Can you give me a reference number from your bank for this?",
                "Let me call my bank directly. What's your name and employee ID?",
                "If my account was really blocked, I'd see a notification in my app.",
            ]
        
        if 'security' in detected_topics and any(word in msg_lower for word in topic_patterns['security']):
            topic_responses['security'] = [
                "My bank told me never to share my OTP with anyone. Why do you need it?",
                "Absolutely not! You can't have my password. That's my security!",
                "How do I know you won't use this to steal my money?",
                "Real banks never ask for OTP. This is definitely a scam.",
                "I will never share my PIN with anyone. Period.",
                "Banks always tell us to keep passwords secret. This doesn't add up.",
            ]
        
        if 'payment' in detected_topics and any(word in msg_lower for word in topic_patterns['payment']):
            topic_responses['payment'] = [
                "You want me to send money? Why would my bank ask me to do that?",
                "I'm not sending money to anyone without verification. Who are you?",
                "What's the payment for exactly? This seems like a scam.",
                "My bank processes refunds themselves. I never transfer money to them.",
                "Can you provide a bank reference number? I need to verify this.",
                "I've never heard of anyone paying their bank through UPI. This is suspicious.",
            ]
        
        if 'personal_info' in detected_topics and any(word in msg_lower for word in topic_patterns['personal_info']):
            topic_responses['personal_info'] = [
                "Why do you need my personal details? That's sensitive information.",
                "How do I know this information won't be misused?",
                "I'm not comfortable sharing account details with someone I don't know.",
                "Can I verify your identity first before sharing anything?",
                "What will you do with this information?",
                "My bank portal shows everything. Why would I need to share it with you?",
            ]
        
        if 'urgency' in detected_topics and any(word in msg_lower for word in topic_patterns['urgency']):
            topic_responses['urgency'] = [
                "Why the rush? Real bank actions aren't this sudden.",
                "You sound like you're trying to pressure me. That's suspicious.",
                "I don't make decisions under pressure. Let me take time to verify.",
                "If it's really urgent, I'll call my bank directly.",
                "This urgency is making me even more suspicious.",
                "Legitimate banks give you time to respond. This feels like a trap.",
            ]
        
        if 'refund' in detected_topics and any(word in msg_lower for word in topic_patterns['refund']):
            topic_responses['refund'] = [
                "How did you get my number to tell me about my package?",
                "Why can't I see this in my app? Let me check myself.",
                "Customs duty? I wasn't expecting any deliveries.",
                "Why do I need to pay for my own refund? That doesn't make sense.",
                "Let me contact the courier company directly instead.",
            ]
        
        if 'prize' in detected_topics and any(word in msg_lower for word in topic_patterns['prize']):
            topic_responses['prize'] = [
                "I never entered any contest. How did I win?",
                "This is a scam. I never participated in KBC.",
                "If I won a lottery, I'd have proof. You're lying.",
                "How do you have my number if I didn't register anywhere?",
                "I'm not falling for this prize scam.",
            ]
        
        if 'loan' in detected_topics and any(word in msg_lower for word in topic_patterns['loan']):
            topic_responses['loan'] = [
                "I never applied for a loan. How is it approved?",
                "Why would I pay a fee upfront for a loan?",
                "Processing fees are deducted from the loan amount, not paid separately.",
                "This seems like a scam. Real banks don't work this way.",
                "I don't need a loan. Stop calling.",
            ]
        
        if 'job' in detected_topics and any(word in msg_lower for word in topic_patterns['job']):
            topic_responses['job'] = [
                "I never applied for a job. How did you get my number?",
                "Part-time job offering ₹50,000/week? That's not realistic.",
                "Why would I get hired without an interview?",
                "What company are you from? Let me verify online first.",
                "This sounds too good to be true. I'm not interested.",
            ]
        
        if 'investment' in detected_topics and any(word in msg_lower for word in topic_patterns['investment']):
            topic_responses['investment'] = [
                "Double money in 48 hours? That's impossible.",
                "No investment offers guaranteed 30% monthly returns.",
                "I'm not investing with strangers. Get lost.",
                "If this were real, everyone would be rich.",
                "This is clearly a scam. I'm not falling for it.",
            ]
        
        if 'threat' in detected_topics and any(word in msg_lower for word in topic_patterns['threat']):
            topic_responses['threat'] = [
                "I haven't done anything illegal. This is harassment.",
                "If there really was a complaint, I'd be contacted officially.",
                "Stop threatening me. You sound like a scammer.",
                "Why would Cyber Cell contact me on WhatsApp?",
                "I'm calling the real police about this threat.",
            ]
        
        # Select response based on detected topics (priority order)
        if topic_responses:
            # Prioritize certain topics based on severity
            priority_topics = ['threat', 'security', 'payment', 'personal_info', 'link', 'suspension', 'urgency', 'kyc', 'refund', 'prize', 'loan', 'job', 'investment']
            for topic in priority_topics:
                if topic in topic_responses:
                    # Vary response based on conversation length
                    available_responses = topic_responses[topic]
                    # Use different responses as conversation progresses (avoid repetition)
                    response_index = (msg_count - 1) % len(available_responses)
                    reply = available_responses[response_index]
                    logger.info(f"🔷 [MOCK MODE] Topic: {topic} | Msg#{msg_count} | Reply: {reply}")
                    return reply
        
        # Fallback responses if no specific topic matched
        if msg_count <= 1:
            fallback = [
                "I'm sorry, I don't understand. Can you explain this more clearly?",
                "This message seems suspicious to me. Who are you exactly?",
                "I need to verify this with my bank directly. What's going on?",
                "This doesn't seem like an official message. How did you get my number?",
                "Can you provide some proof that you're really from my bank?",
            ]
        elif msg_count <= 3:
            fallback = [
                "Tell me more about this. I still have doubts.",
                "I'm not sure I should trust this. Can you prove it?",
                "Let me verify this information first before I do anything.",
                "I have more questions. Can you answer them?",
                "This all seems very suspicious to me.",
                "I don't believe you. Prove it.",
            ]
        else:
            fallback = [
                "Okay, but I need more proof before I do anything.",
                "Let me think about this and verify with my bank.",
                "I'm still not comfortable with this whole situation.",
                "What happens if I don't do this immediately?",
                "Can I get an official letter from your bank about this?",
                "I've been researching and this looks like a classic scam.",
            ]
        
        response_index = (msg_count - 1) % len(fallback)
        reply = fallback[response_index]
        logger.info(f"🔷 [MOCK MODE] Fallback (msg #{msg_count}): {reply}")
        return reply
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.6,
            max_tokens=100,
            timeout=10  # 10 second timeout
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except APITimeoutError:
        logger.error("❌ OpenAI API timeout")
        print("❌ OpenAI API timeout")
        return "Connection is slow. Can you resend that?"
    except APIError as e:
        logger.error(f"❌ OpenAI API error: {e}")
        print(f"❌ OpenAI API error: {e}")
        return "I'm having technical difficulties. Can you try again in a moment?"
    except Exception as e:
        logger.error(f"❌ Agent reply generation error: {type(e).__name__}: {e}")
        print(f"❌ CRITICAL ERROR in agent reply: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "Can you please explain that again? I'm a bit confused."

def extract_intelligence(session: Dict[str, Any], latest_message: str) -> Dict[str, Any]:
    """
    Extract intelligence using combined LLM + regex approach.
    Returns extracted data with validated fields + keywords.
    """
    # Import detector keywords
    from detector import SCAM_KEYWORDS
    
    history = session["conversationHistory"]
    
    # First: use LLM to identify candidate extractions
    extraction_prompt = (
        f"From this conversation, extract any UPI IDs (format: name@bank), "
        f"phone numbers (Indian format), bank account numbers (9-18 digits), "
        f"and URLs. Focus ONLY on what the other person mentioned.\n\n"
        f"Last message: '{latest_message}'\n\n"
        f"Return ONLY valid JSON: "
        f'{{"upi": [], "accounts": [], "urls": [], "phones": []}}'
    )
    
    messages = [
        {"role": "system", "content": "Extract financial data from messages. Return only valid JSON."},
        {"role": "user", "content": extraction_prompt}
    ]
    
    extracted = {
        "upi": [],
        "accounts": [],
        "urls": [],
        "phones": [],
        "suspiciousKeywords": []
    }
    
    # Skip LLM extraction in mock mode - regex is enough
    if not MOCK_MODE:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                llm_extracted = json.loads(json_str)
                extracted = {k: v if isinstance(v, list) else [] for k, v in llm_extracted.items()}
                extracted["suspiciousKeywords"] = []
        except Exception as e:
            print(f"⚠️ LLM extraction error: {e}")
    
    # Extract suspicious keywords
    message_lower = latest_message.lower()
    found_keywords = []
    for keyword in SCAM_KEYWORDS:
        if keyword.lower() in message_lower:
            found_keywords.append(keyword)
    extracted["suspiciousKeywords"] = list(set(found_keywords))  # Remove duplicates
    
    # Second: Validate and enhance with regex patterns
    full_text = latest_message
    
    # UPI ID pattern: name@bank
    upi_pattern = r'\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b'
    upi_matches = re.findall(upi_pattern, full_text)
    extracted["upi"] = list(set(extracted["upi"] + upi_matches))
    
    # Indian phone pattern: +91XXXXXXXXXX or 0XXXXXXXXXX or 6-9 digit start
    phone_pattern = r'(?:\+91|0)?[\s]?[6-9]\d{9}(?!\d)'
    phone_matches = re.findall(phone_pattern, full_text)
    extracted["phones"] = list(set(extracted["phones"] + phone_matches))
    
    # URL pattern - matches http(s), www, or domain.tld patterns
    url_patterns = [
        r'https?://[^\s]+',          # http:// or https://
        r'www\.[^\s]+',              # www.example.com
        r'(?<![.\w])[a-z0-9-]+\.[a-z]{2,}(?:\.[a-z]{2})?(?:/[^\s]*)?'  # example.com
    ]
    url_matches = []
    for pattern in url_patterns:
        url_matches.extend(re.findall(pattern, full_text))
    extracted["urls"] = list(set(extracted["urls"] + url_matches))
    
    # Bank account pattern: 9-18 consecutive digits (validate not part of phone)
    account_pattern = r'\b\d{9,18}\b'
    account_matches = re.findall(account_pattern, full_text)
    # Filter out numbers that look like phones
    extracted["accounts"] = list(set([
        acc for acc in extracted["accounts"] + account_matches 
        if not re.match(r'[6-9]\d{9}', acc)  # Exclude phone-like patterns
    ]))
    
    logger.info(f"Extracted intelligence: UPI={len(extracted['upi'])}, Phones={len(extracted['phones'])}, "
                f"URLs={len(extracted['urls'])}, Accounts={len(extracted['accounts'])}, "
                f"Keywords={len(extracted['suspiciousKeywords'])}")
    
    return extracted

def should_continue_engagement(session: Dict[str, Any], max_turns: int = 20) -> bool:
    """
    Determine if engagement should continue or terminate.
    Termination criteria:
    - Total messages > max_turns
    - Already extracted high-value intelligence (UPI or account number)
    - Agent has been idle for too long
    """
    total_msgs = session["totalMessages"]
    intelligence = session["extractedIntelligence"]
    
    # Terminate if we hit max turns
    if total_msgs >= max_turns:
        return False
    
    # Continue if we haven't extracted high-value data yet
    has_upi = bool(intelligence["upiIds"])
    has_account = bool(intelligence["bankAccounts"])
    has_url = bool(intelligence["phishingLinks"])
    
    # If we have at least 2 pieces of intelligence and exchanged enough messages, consider ending
    if (has_upi or has_account or has_url) and total_msgs >= 6:
        return False
    
    return True
