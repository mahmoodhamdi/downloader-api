from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

db = SQLAlchemy()

class RequestLog(db.Model):
    """Model for storing request logs"""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    format = db.Column(db.String, nullable=False)
    result = db.Column(db.Text, nullable=False)  # Store as JSON string
    duration = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def get_stored_result(url: str, format: str) -> dict:
    """Retrieve stored result for a given URL and format
    
    Args:
        url: The URL of the request
        format: The requested format
        
    Returns:
        dict: Stored result if found, else None
    """
    log = RequestLog.query.filter_by(url=url, format=format).first()
    if log:
        return json.loads(log.result)
    return None

def add_request_log(url: str, format: str, result: dict, duration: float):
    """Add a new request log to the database
    
    Args:
        url: The URL of the request
        format: The requested format
        result: The result data or error
        duration: The processing duration in seconds
    """
    try:
        result_json = json.dumps(result)
    except TypeError:
        result_json = json.dumps({"error": "Result is not serializable"})
    log = RequestLog(url=url, format=format, result=result_json, duration=duration)
    db.session.add(log)
    db.session.commit()