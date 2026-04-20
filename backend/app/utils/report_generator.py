import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(messages: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # 1. TITLE
    story.append(Paragraph("DcoY Cyber Defense Report", styles['Title']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated At: {datetime.utcnow().isoformat()}", styles['Normal']))
    story.append(Spacer(1, 10))

    # Calculate summaries
    total_events = len(messages)
    high_risk = sum(1 for m in messages if m.get("risk_level") == "high")
    medium_risk = sum(1 for m in messages if m.get("risk_level") == "medium")
    low_risk = sum(1 for m in messages if m.get("risk_level") == "low")

    beginner_count = sum(1 for m in messages if m.get("attacker_profile") == "beginner")
    tool_count = sum(1 for m in messages if m.get("attacker_profile") == "automated_tool")
    advanced_count = sum(1 for m in messages if m.get("attacker_profile") == "advanced")

    # 2. SUMMARY SECTION
    story.append(Paragraph("<b>Summary Section:</b>", styles['Heading2']))
    story.append(Paragraph(f"Total Events: {total_events}", styles['Normal']))
    story.append(Paragraph(f"High Risk Count: {high_risk}", styles['Normal']))
    story.append(Paragraph(f"Medium Risk Count: {medium_risk}", styles['Normal']))
    story.append(Paragraph(f"Low Risk Count: {low_risk}", styles['Normal']))
    story.append(Spacer(1, 10))

    # 3. ATTACKER PROFILE SUMMARY
    story.append(Paragraph("<b>Attacker Profile Summary:</b>", styles['Heading2']))
    story.append(Paragraph(f"Beginner: {beginner_count}", styles['Normal']))
    story.append(Paragraph(f"Automated Tool: {tool_count}", styles['Normal']))
    story.append(Paragraph(f"Advanced: {advanced_count}", styles['Normal']))
    story.append(Spacer(1, 10))

    # 4 & 5. DETAILED EVENTS & EXPLANATION SECTION
    story.append(Paragraph("<b>Detailed Events:</b>", styles['Heading2']))
    story.append(Spacer(1, 10))

    for msg in messages:
        story.append(Paragraph("<b>-----------------------------</b>", styles['Normal']))
        story.append(Paragraph(f"<b>IP:</b> {msg.get('ip', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Event Type:</b> {msg.get('event_type', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Level:</b> {msg.get('risk_level', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Score:</b> {msg.get('risk_score', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Severity:</b> {msg.get('severity', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Attacker Profile:</b> {msg.get('attacker_profile', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>History Events:</b> {msg.get('history_events', 0)}", styles['Normal']))
        story.append(Paragraph(f"<b>Repeat Offender Score:</b> {msg.get('repeat_offender_score', 0)}", styles['Normal']))
        
        # Include Response and Deception action (handling possible missing keys gracefully)
        response_action = msg.get('response_action_final', 'N/A')
        deception_action = msg.get('deception_action', 'N/A')
        
        story.append(Paragraph(f"<b>Response Action:</b> {response_action}", styles['Normal']))
        story.append(Paragraph(f"<b>Deception Action:</b> {deception_action}", styles['Normal']))
        
        explanation = msg.get("explanation")
        if explanation:
             story.append(Paragraph(f"<b>Explanation:</b> {explanation}", styles['Normal']))
        
        story.append(Spacer(1, 10))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
