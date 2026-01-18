from langchain_openai import ChatOpenAI
from app.llm.state import AgentState
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Increased for more natural responses
)

# Security & Guardrails
SECURITY_PROMPT = """
You are a security filter for ProdOps AI. Analyze if this user input is safe and appropriate for a production operations system.

User input: "{input}"

Check for:
1. SQL injection attempts
2. System commands
3. Attempts to access unauthorized data
4. Malicious code
5. Inappropriate content
6. Attempts to bypass role restrictions

Respond with ONLY:
- SAFE: if the input is legitimate
- UNSAFE: if the input is potentially malicious

Response:"""

def security_check(state: AgentState) -> bool:
    """Check if user input is safe"""
    user_input = state.get("input", "")
    
    # Basic checks
    suspicious_patterns = [
        "DROP TABLE", "DELETE FROM", "UPDATE users SET",
        "'; --", "UNION SELECT", "<script>", "javascript:",
        "eval(", "exec(", "__import__", "os.system"
    ]
    
    input_upper = user_input.upper()
    for pattern in suspicious_patterns:
        if pattern.upper() in input_upper:
            return False
    
    # LLM-based check for subtle attacks
    try:
        check_prompt = SECURITY_PROMPT.format(input=user_input)
        result = llm.invoke(check_prompt).content.strip()
        return "SAFE" in result.upper()
    except:
        # If LLM check fails, be cautious
        return len(user_input) < 500  # Basic length check

# -------------------------
# Intent Classification
# -------------------------
INTENT_PROMPT = """
You are ProdOps AI, a production operations assistant. Classify the user's intent into ONE category:

- PRODUCTION_QUERY: Questions about production output, quantities, good/reject counts
- DOWNTIME_QUERY: Questions about machine downtime, stoppages, reasons for delays
- CREATE_TICKET: Requests to create maintenance tickets, report issues, log problems
- TICKET_STATUS: Questions about existing tickets, ticket status
- GENERAL_QUERY: General questions, greetings, or unclear requests

User message: {input}

Previous context: {context}

Return ONLY the intent label (e.g., PRODUCTION_QUERY).
"""

def classify_intent(state: AgentState) -> AgentState:
    # Security check first
    if not security_check(state):
        state["intent"] = "BLOCKED"
        state["response"] = "I detected potentially unsafe content in your request. Please rephrase your question appropriately."
        return state
    
    context = state.get("memory", {})
    context_str = json.dumps(context) if context else "None"
    
    prompt = INTENT_PROMPT.format(
        input=state["input"],
        context=context_str
    )
    
    intent = llm.invoke(prompt).content.strip()
    state["intent"] = intent
    return state

# -------------------------
# Import Services
# -------------------------
from app.services.production_service import get_daily_production_summary
from app.services.downtime_service import get_downtime_summary
from app.services.ticket_service import create_ticket, get_open_tickets_count
from app.services.memory_service import load_user_memory, save_user_memory
from app.rag.retriever import retrieve_docs


# -------------------------
# Production Query Handler
# -------------------------
PRODUCTION_RESPONSE_PROMPT = """
You are ProdOps AI, a friendly and professional production operations assistant.

The user asked: "{user_query}"

Production data retrieved:
{data}

Generate a natural, conversational response that:
1. Directly answers their question in plain English
2. Highlights key metrics (good quantity, reject quantity, efficiency)
3. Points out any concerns (high rejects, low output)
4. Offers to help with next steps if relevant

Be concise but friendly. Use natural language, not technical jargon.
"""

def handle_production(state: AgentState) -> AgentState:
    # Extract parameters from query using LLM
    extract_prompt = f"""
Extract the line_code and date from this query: "{state['input']}"

Rules:
- If no line mentioned, use "LINE-1"
- If no date mentioned, use today's date: {datetime.now().strftime('%Y-%m-%d')}
- Return ONLY in this format: LINE-X|YYYY-MM-DD
"""
    
    params = llm.invoke(extract_prompt).content.strip()
    
    try:
        line_code, date = params.split("|")
    except:
        line_code, date = "LINE-1", datetime.now().strftime('%Y-%m-%d')
    
    # Get data
    result = get_daily_production_summary(line_code.strip(), date.strip())
    
    if not result:
        state["response"] = f"I couldn't find any production data for {line_code} on {date}. Would you like to check a different line or date?"
        return state
    
    # Format response naturally
    data_str = f"""
Line: {result.get('line_code', 'N/A')}
Date: {result.get('production_date', 'N/A')}
Good Quantity: {result.get('total_good', 0)} units
Rejected: {result.get('total_reject', 0)} units
"""
    
    response_prompt = PRODUCTION_RESPONSE_PROMPT.format(
        user_query=state["input"],
        data=data_str
    )
    
    natural_response = llm.invoke(response_prompt).content
    state["response"] = natural_response
    state["tool_result"] = result
    return state


# -------------------------
# Downtime Query Handler
# -------------------------
DOWNTIME_RESPONSE_PROMPT = """
You are ProdOps AI, a production operations assistant.

The user asked: "{user_query}"

Downtime data retrieved:
{data}

Generate a clear, conversational response that:
1. Summarizes the total downtime and main reasons
2. Highlights the biggest issues (longest downtimes)
3. Suggests checking related tickets or taking action if needed

Be helpful and professional.
"""

def handle_downtime(state: AgentState) -> AgentState:
    # Extract parameters
    extract_prompt = f"""
Extract line_code and date from: "{state['input']}"

Rules:
- Default line: "LINE-1"
- Default date: {datetime.now().strftime('%Y-%m-%d')}
- Format: LINE-X|YYYY-MM-DD
"""
    
    params = llm.invoke(extract_prompt).content.strip()
    
    try:
        line_code, date = params.split("|")
    except:
        line_code, date = "LINE-1", datetime.now().strftime('%Y-%m-%d')
    
    result = get_downtime_summary(line_code.strip(), date.strip())
    
    if not result:
        state["response"] = f"Great news! No downtime recorded for {line_code} on {date}. 🎉"
        return state
    
    # Format downtime data
    total_downtime = sum(float(r.get('downtime_minutes', 0)) for r in result)
    data_str = f"Total Downtime: {total_downtime:.1f} minutes\n\nBreakdown:\n"
    
    for idx, r in enumerate(result[:5], 1):  # Top 5 reasons
        data_str += f"{idx}. {r.get('reason_text', 'Unknown')}: {r.get('downtime_minutes', 0):.1f} min\n"
    
    response_prompt = DOWNTIME_RESPONSE_PROMPT.format(
        user_query=state["input"],
        data=data_str
    )
    
    natural_response = llm.invoke(response_prompt).content
    state["response"] = natural_response
    state["tool_result"] = result
    return state


# -------------------------
# Ticket Creation Handler
# -------------------------
TICKET_CREATION_PROMPT = """
You are ProdOps AI. Extract ticket details from the user's request.

User request: "{user_query}"

Extract:
1. Line code (default: LINE-1)
2. Issue summary (brief description)
3. Severity (Low/Medium/High/Critical - assess based on urgency)

Return in this exact format:
LINE-X|Issue description here|Severity
"""

TICKET_RESPONSE_TEMPLATE = """
✅ **Ticket Created Successfully!**

**Ticket Number:** {ticket_no}
**Severity:** {severity}
**Status:** {status}
**Created:** {created_at}

Your maintenance team has been notified via email and WhatsApp. They'll address this issue promptly.

Is there anything else I can help you with?
"""

def handle_ticket(state: AgentState) -> AgentState:
    # Check authorization
    if "SUPERVISOR" not in state["roles"]:
        state["response"] = "I'm sorry, but only supervisors can create maintenance tickets. Please contact your supervisor if you need to report an issue."
        return state
    
    # Extract ticket details
    extraction = llm.invoke(
        TICKET_CREATION_PROMPT.format(user_query=state["input"])
    ).content.strip()
    
    try:
        parts = extraction.split("|")
        line_code = parts[0].strip()
        issue_summary = parts[1].strip() if len(parts) > 1 else state["input"]
        severity = parts[2].strip() if len(parts) > 2 else "Medium"
    except:
        line_code = "LINE-1"
        issue_summary = state["input"]
        severity = "Medium"
    
    # Create ticket
    ticket = create_ticket(
        line_code=line_code,
        issue_summary=issue_summary,
        severity=severity,
        created_by_user_id=state["user_id"],
    )
    
    # Format response
    state["response"] = TICKET_RESPONSE_TEMPLATE.format(
        ticket_no=ticket.get('ticket_no', 'N/A'),
        severity=ticket.get('severity', 'N/A'),
        status=ticket.get('status', 'N/A'),
        created_at=ticket.get('created_at', 'Just now')
    )
    state["tool_result"] = ticket
    return state

# Add this function after handle_ticket function

def handle_ticket_status(state: AgentState) -> AgentState:
    """Handle queries about ticket status"""
    from app.services.ticket_service import get_all_tickets, get_ticket_stats, get_ticket_by_number
    
    user_query = state["input"].lower()
    
    # Check if asking for specific ticket
    if "ticket" in user_query and any(word in user_query for word in ["status", "tkt-", "ticket-"]):
        # Try to extract ticket number
        import re
        ticket_match = re.search(r'TKT-[A-Z0-9]{6}', state["input"].upper())
        
        if ticket_match:
            ticket_no = ticket_match.group(0)
            ticket = get_ticket_by_number(ticket_no)
            
            if ticket:
                state["response"] = f"""
📋 **Ticket Details: {ticket['ticket_no']}**

**Issue:** {ticket['issue_summary']}
**Line:** {ticket['line_code']}
**Severity:** {ticket['severity']}
**Status:** {ticket['status']}
**Created By:** {ticket['created_by']}
**Created:** {ticket['created_at']}

Need anything else?
"""
            else:
                state["response"] = f"I couldn't find ticket {ticket_no}. Please check the ticket number and try again."
            return state
    
    # If asking for open tickets or summary
    if any(word in user_query for word in ["open", "pending", "how many"]):
        stats = get_ticket_stats()
        tickets = get_all_tickets(limit=5, status="OPEN")
        
        response = f"""
📊 **Ticket Summary**

- Open: {stats['open_count']} tickets
- In Progress: {stats['in_progress_count']} tickets  
- Closed: {stats['closed_count']} tickets
- Total: {stats['total_count']} tickets

"""
        
        if stats['open_count'] > 0:
            response += "\n**Recent Open Tickets:**\n"
            for t in tickets[:3]:
                response += f"• {t['ticket_no']} - {t['issue_summary'][:50]}... ({t['severity']})\n"
        
        state["response"] = response
        return state
    
    # Default: show general stats
    stats = get_ticket_stats()
    state["response"] = f"""
📊 **Current Ticket Status**

- {stats['open_count']} Open
- {stats['in_progress_count']} In Progress
- {stats['closed_count']} Closed

Would you like to see details for any specific tickets?
"""
    return state

# -------------------------
# General Response Formatter
# -------------------------
GENERAL_RESPONSE_PROMPT = """
You are ProdOps AI, a helpful production operations assistant.

The user said: "{user_query}"

Context from knowledge base:
{knowledge}

Generate a helpful, conversational response. Be friendly and professional.
"""

def format_response(state: AgentState) -> AgentState:
    # If response already set, return
    if state.get("response"):
        return state
    
    # If knowledge retrieved
    if state.get("retrieved_docs"):
        content = "\n\n".join([d.page_content for d in state["retrieved_docs"][:3]])
        
        response_prompt = GENERAL_RESPONSE_PROMPT.format(
            user_query=state["input"],
            knowledge=content
        )
        
        state["response"] = llm.invoke(response_prompt).content
        return state
    
    # If tool result but no response formatted
    if state.get("tool_result"):
        state["response"] = "I found the information you requested. Let me know if you need anything else!"
        return state
    
    # Default fallback
    state["response"] = "I'm here to help with production queries, downtime analysis, and ticket management. What would you like to know?"
    return state


# -------------------------
# Memory Management
# -------------------------
def load_memory(state: AgentState) -> AgentState:
    memory = load_user_memory(state["user_id"])
    state["memory"] = memory
    return state


def persist_memory(state: AgentState) -> AgentState:
    memory = state.get("memory", {})
    
    # Update memory
    memory.update({
        "last_intent": state.get("intent"),
        "last_query": state.get("input"),
        "last_response": state.get("response", "")[:200],  # Store first 200 chars
        "timestamp": datetime.now().isoformat()
    })
    
    save_user_memory(state["user_id"], memory)
    return state


def retrieve_knowledge(state: AgentState) -> AgentState:
    docs = retrieve_docs(state["input"])
    state["retrieved_docs"] = docs
    return state