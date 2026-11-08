from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime

from database import Base

class Requisition(Base):
    __tablename__ = "requisitions"

    requisition_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    job_description = Column(Text, nullable=False)
    rubric = Column(JSON, nullable=True)
    status = Column(String(50), default="Open")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    resume_path = Column(String(255), nullable=True)
    consent_preferences = Column(JSON, nullable=True)
    current_status = Column(String(100), default="Resume Received")

    
