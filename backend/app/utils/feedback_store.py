from datetime import datetime

feedback_db = {}

def update_feedback(user: str, ip: str, risk_level: str):
    if user not in feedback_db:
        feedback_db[user] = {}
        
    if ip not in feedback_db[user]:
        feedback_db[user][ip] = {
            "total_events": 0,
            "high_risk_count": 0,
            "last_seen": ""
        }
    
    feedback_db[user][ip]["total_events"] += 1
    if risk_level == "high":
        feedback_db[user][ip]["high_risk_count"] += 1
        
    feedback_db[user][ip]["last_seen"] = datetime.utcnow().isoformat()

def get_feedback(user: str, ip: str) -> dict:
    if user not in feedback_db:
        feedback_db[user] = {}
        
    if ip not in feedback_db[user]:
        return {
            "total_events": 0,
            "high_risk_count": 0,
            "last_seen": ""
        }
    return feedback_db[user][ip]
