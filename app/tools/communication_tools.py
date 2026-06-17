import os

# Simulated mailbox store for draft tracking
DRAFTS_FILE = "drafts.json"

def get_drafts():
    import json
    if not os.path.exists(DRAFTS_FILE):
        return []
    try:
        with open(DRAFTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_draft(draft):
    import json
    drafts = get_drafts()
    drafts.append(draft)
    with open(DRAFTS_FILE, "w") as f:
        json.dump(drafts, f, indent=4)

def draft_email_message(to_address: str, subject: str, body: str) -> str:
    """Drafts an email or message on behalf of the user and saves it to the local drafts list.
    
    Args:
        to_address: Recipient email address (e.g. 'client@example.com').
        subject: Email subject.
        body: Message body content.
    """
    try:
        import datetime
        draft = {
            "to": to_address,
            "subject": subject,
            "body": body,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "draft"
        }
        save_draft(draft)
        return f"Email draft successfully created and stored to '{to_address}'. Subject: '{subject}'."
    except Exception as e:
        return f"Error drafting email: {str(e)}"

def format_meeting_notes(raw_notes: str) -> str:
    """Formats raw transcripts or messy details from a meeting into a structured meeting note template.
    
    Args:
        raw_notes: Raw transcribed text or notes from the meeting.
    """
    # Simple formatting logic
    lines = raw_notes.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    output = []
    output.append("=== MEETING SUMMARY ===")
    output.append("Date: Stamped via Digital Twin Operating System")
    output.append("\nSummary of discussion points:")
    
    actions = []
    for line in cleaned_lines:
        if any(keyword in line.lower() for keyword in ("action", "todo", "needs to", "must do", "assign")):
            actions.append(f"- {line}")
        else:
            output.append(f"- {line}")
            
    if actions:
        output.append("\nAction Items:")
        output.extend(actions)
        
    return "\n".join(output)

def list_drafts_summary() -> str:
    """Returns a list of all drafted emails/messages stored locally."""
    try:
        drafts = get_drafts()
        if not drafts:
            return "No drafts currently saved."
        
        output = ["### Draft Messages List:"]
        for idx, d in enumerate(drafts):
            output.append(f"Draft [{idx+1}] To: {d['to']} | Subject: {d['subject']} | Time: {d['timestamp']}\nBody: {d['body'][:150]}...")
            output.append("-" * 30)
        return "\n".join(output)
    except Exception as e:
        return f"Error listing drafts: {str(e)}"
