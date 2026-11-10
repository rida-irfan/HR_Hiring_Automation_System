
from sqlalchemy import (Column,Integer,String,Text,DateTime,JSON,Float,ForeignKey,Boolean)
from datetime import datetime
from database import Base


# ==========================================
# 1. REQUISITION MODEL
# ==========================================

class Requisition(Base):
    __tablename__ = "requisitions"

    requisition_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String(200), nullable=False)

    job_description = Column(Text, nullable=False)

    # Stores weights, must-have/preferred types,
    # and justifications for each criterion
    rubric = Column(JSON, nullable=True)

    status = Column(String(50), default="Open")

    created_by = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# 2. CANDIDATE MODEL
# ==========================================

class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String(150), nullable=False)

    email = Column(String(150), nullable=True)

    phone = Column(String(30), nullable=True)

    resume_path = Column(String(255), nullable=True)

    consent_preferences = Column(JSON, nullable=True)

    current_status = Column(
        String(100),
        default="Resume Received"
    )


# ==========================================
# 3. RESUME EVALUATION MODEL (AGENT 1)
# ==========================================

class ResumeEvaluation(Base):
    __tablename__ = "resume_evaluations"

    evaluation_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.candidate_id"),
        nullable=False
    )

    requisition_id = Column(
        Integer,
        ForeignKey("requisitions.requisition_id"),
        nullable=False
    )

    # AI-generated weighted score
    total_score = Column(Float, nullable=False)

    # Individual criterion scores
    criterion_scores = Column(JSON, nullable=True)

    # Supporting evidence for each criterion
    evidence = Column(JSON, nullable=True)

    # Structured resume information
    structured_evidence = Column(JSON, nullable=True)
    evidence_quotes = Column(JSON, nullable=True)
    evidence_quality = Column(JSON, nullable=True)
    scoring_review_details = Column(JSON, nullable=True)

    # AI warnings
    warnings = Column(JSON, nullable=True)

    # Missing or unclear qualifications
    missing_or_unclear_items = Column(
        JSON,
        nullable=True
    )

    # Resume extraction warnings
    parsing_warnings = Column(
        JSON,
        nullable=True
    )

    # Recommendation for human verification
    recommendation_for_human_review = Column(
        Text,
        nullable=True
    )

    # Azure model deployment identifier
    model_version = Column(
        String(100),
        nullable=True
    )

    # Human approval status
    review_status = Column(
        String(30),
        default="Pending HR Review",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# 4. SCREENING MODEL (AGENT 2)
# ==========================================

class Screening(Base):
    __tablename__ = "screenings"

    screening_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.candidate_id"),
        nullable=False
    )

    requisition_id = Column(
        Integer,
        ForeignKey("requisitions.requisition_id"),
        nullable=False
    )

    evaluation_id = Column(
        Integer,
        ForeignKey("resume_evaluations.evaluation_id"),
        nullable=True
    )

    # HR-approved screening questions
    questions = Column(JSON, nullable=True)

    # Existing fields retained
    answers = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="Pending Consent")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Required Agent 2 outputs
    call_status = Column(
        String(50),
        default="Not Started",
        nullable=False
    )

    consent_status = Column(
        String(50),
        default="Pending",
        nullable=False
    )

    question_answer_pairs = Column(JSON, nullable=True)

    candidate_stated_availability = Column(
        Text,
        nullable=True
    )

    role_requirement_responses = Column(
        JSON,
        nullable=True
    )

    unresolved_questions = Column(
        JSON,
        nullable=True
    )

    concise_summary = Column(Text, nullable=True)

    recommended_next_step_for_human_review = Column(
        Text,
        nullable=True
    )

    call_timestamp = Column(DateTime, nullable=True)

    # HR makes the final progression decision
    review_status = Column(
        String(50),
        default="Pending HR Review",
        nullable=False
    )

# ==========================================
# 5. SCREENING QUESTION MODEL (AGENT 2)
# ==========================================

class ScreeningQuestion(Base):
    __tablename__ = "screening_questions"

    question_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    requisition_id = Column(
        Integer,
        ForeignKey("requisitions.requisition_id"),
        nullable=False
    )

    question_text = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(50),
        nullable=False
    )

    is_approved = Column(
        Boolean,
        default=False,
        nullable=False
    )

    approved_by = Column(
        String(100),
        nullable=True
    )

    approved_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )    


# ==========================================
# 6. HR USER MODEL (AUTHENTICATION)
# ==========================================

class HRUser(Base):
    __tablename__ = "hr_users"

    hr_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# 7. INTERVIEW INVITATION MODEL (AGENT 2)
# ==========================================

class InterviewInvitation(Base):
    __tablename__ = "interview_invitations"

    invitation_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.candidate_id"),
        nullable=False
    )

    screening_id = Column(
        Integer,
        ForeignKey("screenings.screening_id"),
        nullable=False
    )

    # Store token hash, never the actual token
    token_hash = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )

    # Invitation expiry time (UTC)
    expires_at = Column(
        DateTime,
        nullable=False
    )

    # Track whether the link has been redeemed
    used_at = Column(
        DateTime,
        nullable=True
    )

    # Invitation delivery and lifecycle
    status = Column(
        String(50),
        default="Pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )
