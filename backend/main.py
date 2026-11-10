from datetime import datetime
from security import verify_password, create_access_token
from fastapi import FastAPI, Depends, Header,UploadFile, File, HTTPException, status
from pathlib import Path
from sqlalchemy.orm import Session
import uuid
from database import get_db
import models
import schemas
from auth import get_current_hr
from database import engine, Base
from services.rubric_validator import validate_rubric
import os
import secrets
from dotenv import load_dotenv
from security import hash_password
from invitation_security import create_candidate_session_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from invitation_security import verify_candidate_session_token
import jwt
from invitation_security import (
    generate_invitation_token,
    hash_invitation_token,
    get_invitation_expiry,
    is_invitation_expired
)

load_dotenv()
HR_SETUP_KEY = os.getenv("HR_SETUP_KEY")

# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="HR Hiring Automation System")

# Resume upload directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "HR Hiring Automation API is running!"
    }

# --------------------------------------------------
# JOB REQUISITION ENDPOINTS
# --------------------------------------------------

# Create a job requisition
@app.post(
    "/requisitions",
    response_model=schemas.RequisitionResponse,
    dependencies=[Depends(get_current_hr)]
)
def create_requisition(
    requisition: schemas.RequisitionCreate,
    db: Session = Depends(get_db)
):
    new_requisition = models.Requisition(
        **requisition.model_dump()
    )

    db.add(new_requisition)
    db.commit()
    db.refresh(new_requisition)

    return new_requisition

# Get all job requisitions
@app.get(
    "/requisitions",
    response_model=list[schemas.RequisitionResponse],
    dependencies=[Depends(get_current_hr)]
)
def get_requisitions(db: Session = Depends(get_db)):

    requisitions = db.query(
        models.Requisition
    ).all()

    return requisitions


# Approve a job requisition
@app.patch("/requisitions/{requisition_id}/approve", dependencies=[Depends(get_current_hr)])
def approve_requisition(
    requisition_id: int,
    db: Session = Depends(get_db)
):
    # Step 1: Find the requisition
    requisition = db.query(
        models.Requisition
    ).filter(
        models.Requisition.requisition_id == requisition_id
    ).first()

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    # Step 2: Prevent repeated approval
    if requisition.status == "Approved":
        raise HTTPException(
            status_code=400,
            detail="Requisition is already approved"
        )

    # Step 3: Check whether rubric exists
    if not requisition.rubric:
        raise HTTPException(
            status_code=400,
            detail="Cannot approve a requisition without a scoring rubric"
        )

    # Step 4: Validate rubric
    try:
        validate_rubric(requisition.rubric)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # Step 5: Approve requisition
    requisition.status = "Approved"

    # Step 6: Save changes in SQLite
    db.commit()
    db.refresh(requisition)

    return {
        "message": "Requisition approved successfully",
        "requisition_id": requisition.requisition_id,
        "status": requisition.status
    }

# --------------------------------------------------
# CANDIDATE ENDPOINTS
# --------------------------------------------------

# Register a new candidate
@app.post(
    "/candidates",
    response_model=schemas.CandidateResponse,
    dependencies=[Depends(get_current_hr)]
)
def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db)
):
    new_candidate = models.Candidate(
        **candidate.model_dump()
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate

# Get all candidates
@app.get(
    "/candidates",
    response_model=list[schemas.CandidateResponse],
    dependencies=[Depends(get_current_hr)]
)
def get_candidates(db: Session = Depends(get_db)):

    candidates = db.query(
        models.Candidate
    ).all()

    return candidates

# --------------------------------------------------
# RESUME UPLOAD ENDPOINT
# --------------------------------------------------

@app.post("/candidates/{candidate_id}/resume", dependencies=[Depends(get_current_hr)])
async def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Step 1: Find candidate
    candidate = db.query(
        models.Candidate
    ).filter(
        models.Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # Step 2: Validate file format
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    # Step 3: Read and validate file size
    content = await file.read()

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 5 MB"
        )

    # Step 4: Generate unique filename
    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename

    file_path.write_bytes(content)

    # Step 5: Save resume path in SQLite
    candidate.resume_path = f"uploads/{filename}"

    db.commit()
    db.refresh(candidate)

    return {
        "message": "Resume uploaded successfully",
        "candidate_id": candidate.candidate_id,
        "resume_path": candidate.resume_path
    }

# --------------------------------------------------
# RESUME EVALUATION ENDPOINTS
# --------------------------------------------------

# Retrieve all saved resume evaluations
@app.get(
    "/evaluations",
    response_model=list[schemas.ResumeEvaluationResponse],
    dependencies=[Depends(get_current_hr)]
)
def get_evaluations(
    db: Session = Depends(get_db)
):
    evaluations = db.query(
        models.ResumeEvaluation
    ).all()

    return evaluations


# --------------------------------------------------
# HR REVIEW ENDPOINT
# --------------------------------------------------

@app.patch("/evaluations/{evaluation_id}/review", dependencies=[Depends(get_current_hr)])
def review_evaluation(
    evaluation_id: int,
    review: schemas.EvaluationReviewRequest,
    db: Session = Depends(get_db)
):
    # Step 1: Find evaluation
    evaluation = db.query(
        models.ResumeEvaluation
    ).filter(
        models.ResumeEvaluation.evaluation_id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    # Step 2: Update HR review status
    evaluation.review_status = review.review_status

    # Step 3: Save changes
    db.commit()
    db.refresh(evaluation)

    return {
        "message": "HR review updated successfully",
        "evaluation_id": evaluation.evaluation_id,
        "review_status": evaluation.review_status
    }

    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == question.requisition_id
    ).first()

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    # Create a new unapproved screening question
    new_question = models.ScreeningQuestion(
        requisition_id=question.requisition_id,
        question_text=question.question_text,
        category=question.category,
        is_approved=False
    )

    # Save question in the database
    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question

# ==========================================
# AGENT 2 - GET SCREENING QUESTIONS
# ==========================================

@app.get(
    "/screening-questions",
    response_model=list[schemas.ScreeningQuestionResponse],
    dependencies=[Depends(get_current_hr)]
)
def get_screening_questions(
    requisition_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.ScreeningQuestion)

    # Filter questions by requisition if provided
    if requisition_id is not None:
        query = query.filter(
            models.ScreeningQuestion.requisition_id == requisition_id
        )

    return query.all()

# ==========================================
# AGENT 2 - APPROVE SCREENING QUESTION
# ==========================================

@app.patch(
    "/screening-questions/{question_id}/approve",
    response_model=schemas.ScreeningQuestionResponse,
    dependencies=[Depends(get_current_hr)]
)
def approve_screening_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = db.query(models.ScreeningQuestion).filter(
        models.ScreeningQuestion.question_id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Screening question not found"
        )

    # Only questions for approved requisitions
    # can be approved
    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == question.requisition_id
    ).first()

    if not requisition or requisition.status != "Approved":
        raise HTTPException(
            status_code=400,
            detail="Requisition must be approved first"
        )

    question.is_approved = True
    question.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(question)

    return question

# ==========================================
# AGENT 2 - CHECK SCREENING ELIGIBILITY
# ==========================================

@app.get("/screening-eligibility/{evaluation_id}", dependencies=[Depends(get_current_hr)])
def check_screening_eligibility(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    evaluation = db.query(models.ResumeEvaluation).filter(
        models.ResumeEvaluation.evaluation_id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Resume evaluation not found"
        )

    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == evaluation.requisition_id
    ).first()

    approved_questions = db.query(models.ScreeningQuestion).filter(
        models.ScreeningQuestion.requisition_id == evaluation.requisition_id,
        models.ScreeningQuestion.is_approved.is_(True)
    ).count()

    eligible = (
        evaluation.review_status == "Approved for Screening"
        and requisition is not None
        and requisition.status == "Approved"
        and approved_questions > 0
    )

    return {
        "evaluation_id": evaluation.evaluation_id,
        "candidate_id": evaluation.candidate_id,
        "requisition_id": evaluation.requisition_id,
        "eligible_for_screening": eligible,
        "hr_review_status": evaluation.review_status,
        "approved_questions_count": approved_questions
    }

# ==========================================
# AGENT 2 - CREATE SCREENING SESSION
# ==========================================

@app.post("/screenings", status_code=201, dependencies=[Depends(get_current_hr)])
def create_screening_session(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    # 1. Find resume evaluation
    evaluation = db.query(models.ResumeEvaluation).filter(
        models.ResumeEvaluation.evaluation_id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Resume evaluation not found"
        )

    # 2. Verify HR approval
    if evaluation.review_status != "Approved for Screening":
        raise HTTPException(
            status_code=403,
            detail="Candidate is not approved for screening"
        )
    # 3. Verify approved requisition
    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == evaluation.requisition_id,
        models.Requisition.status == "Approved"
    ).first()

    if not requisition:
        raise HTTPException(
            status_code=403,
            detail="Job requisition is not approved"
        )

    # 4. Get approved questions only
    approved_questions = db.query(models.ScreeningQuestion).filter(
        models.ScreeningQuestion.requisition_id == evaluation.requisition_id,
        models.ScreeningQuestion.is_approved.is_(True)
    ).order_by(
        models.ScreeningQuestion.question_id
    ).all()

    if not approved_questions:
        raise HTTPException(
            status_code=400,
            detail="No HR-approved screening questions available"
        )
     # 5. Prevent duplicate sessions for same evaluation
    existing = db.query(models.Screening).filter(
        models.Screening.evaluation_id == evaluation_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Screening session already exists for this evaluation"
        )

    # 6. Create session
    screening = models.Screening(
        candidate_id=evaluation.candidate_id,
        requisition_id=evaluation.requisition_id,
        evaluation_id=evaluation_id,
        questions=[
            {
                "question_id": q.question_id,
                "question_text": q.question_text,
                "category": q.category
            }
            for q in approved_questions
        ],
        call_status="Not Started",
        consent_status="Pending",
        review_status="Pending HR Review"
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)

    return {
        "screening_id": screening.screening_id,
        "candidate_id": screening.candidate_id,
        "requisition_id": screening.requisition_id,
        "evaluation_id": screening.evaluation_id,
        "call_status": screening.call_status,
        "consent_status": screening.consent_status,
        "questions": screening.questions,
        "review_status": screening.review_status
    }

# ==========================================
# AGENT 2 - GET SCREENING SESSION
# ==========================================

@app.get("/screenings/{screening_id}", dependencies=[Depends(get_current_hr)])
def get_screening_session(
    screening_id: int,
    db: Session = Depends(get_db)
):
    screening = db.query(models.Screening).filter(
        models.Screening.screening_id == screening_id
    ).first()

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening session not found"
        )

    return {
        "screening_id": screening.screening_id,
        "candidate_id": screening.candidate_id,
        "requisition_id": screening.requisition_id,
        "evaluation_id": screening.evaluation_id,
        "call_status": screening.call_status,
        "consent_status": screening.consent_status,
        "questions": screening.questions,
        "question_answer_pairs": screening.question_answer_pairs,
        "candidate_stated_availability": screening.candidate_stated_availability,
        "role_requirement_responses": screening.role_requirement_responses,
        "unresolved_questions": screening.unresolved_questions,
        "concise_summary": screening.concise_summary,
        "recommended_next_step_for_human_review": screening.recommended_next_step_for_human_review,
        "call_timestamp": screening.call_timestamp,
        "review_status": screening.review_status
    }

# ==========================================
# HR SIGNUP API
# ==========================================

@app.post(
    "/auth/signup",
    response_model=schemas.HRResponse,
    status_code=status.HTTP_201_CREATED
)
def signup_hr(
    hr_data: schemas.HRSignup,
    x_hr_setup_key: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    # Restrict unauthorized HR account creation
    if not HR_SETUP_KEY:
        raise HTTPException(
            status_code=503,
            detail="HR account setup is not configured"
        )

    if not x_hr_setup_key or not secrets.compare_digest(
        x_hr_setup_key,
        HR_SETUP_KEY
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create HR accounts"
        )

    # Normalize email
    email = hr_data.email.strip().lower()

    # Check duplicate email
    existing_hr = (
        db.query(models.HRUser)
        .filter(models.HRUser.email == email)
        .first()
    )

    if existing_hr:
        raise HTTPException(
            status_code=409,
            detail="HR account with this email already exists"
        )

    new_hr = models.HRUser(
        full_name=hr_data.full_name.strip(),
        email=email,
        hashed_password=hash_password(hr_data.password),
        is_active=True
    )

    db.add(new_hr)

    try:
        db.commit()
        db.refresh(new_hr)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create HR account"
        )

    return new_hr

# ==========================================
# HR LOGIN API
# ==========================================

@app.post(
    "/auth/login",
    response_model=schemas.TokenResponse,
)
def login_hr(
    login_data: schemas.HRLogin,
    db: Session = Depends(get_db)
):
    email = login_data.email.strip().lower()

    # Find HR account
    hr = (
        db.query(models.HRUser)
        .filter(models.HRUser.email == email)
        .first()
    )

    # Check password
    if not hr or not verify_password(
        login_data.password,
        hr.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check account status
    if not hr.is_active:
        raise HTTPException(
            status_code=403,
            detail="HR account is disabled"
        )

    # Generate JWT
    access_token = create_access_token(hr.hr_id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/auth/me", response_model=schemas.HRResponse)
def get_my_profile(
    current_hr: models.HRUser = Depends(get_current_hr)
):
    return current_hr


# ==========================================
# AGENT 2 - CREATE INTERVIEW INVITATION
# ==========================================

@app.post(
    "/invitations",
    response_model=schemas.InvitationResponse,
    status_code=201,
    dependencies=[Depends(get_current_hr)]
)
def create_interview_invitation(
    invitation: schemas.InvitationCreate,
    db: Session = Depends(get_db)
):
    # Find screening session
    screening = db.query(models.Screening).filter(
        models.Screening.screening_id == invitation.screening_id
    ).first()

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening session not found"
        )

    # Verify HR approval
    evaluation = db.query(models.ResumeEvaluation).filter(
        models.ResumeEvaluation.evaluation_id == screening.evaluation_id,
        models.ResumeEvaluation.candidate_id == screening.candidate_id,
        models.ResumeEvaluation.requisition_id == screening.requisition_id,
        models.ResumeEvaluation.review_status == "Approved for Screening"
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=403,
            detail="Candidate is not approved for screening"
        )

    # Verify job approval
    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == screening.requisition_id,
        models.Requisition.status == "Approved"
    ).first()

    if not requisition:
        raise HTTPException(
            status_code=403,
            detail="Job requisition is not approved"
        )

    # Check for an existing active invitation
    now = datetime.utcnow()

    existing = db.query(models.InterviewInvitation).filter(
        models.InterviewInvitation.screening_id == screening.screening_id,
        models.InterviewInvitation.used_at.is_(None),
        models.InterviewInvitation.expires_at > now,
        models.InterviewInvitation.status.in_(["Pending", "Sent"])
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An active invitation already exists"
        )

    # Generate secure token
    raw_token = generate_invitation_token()
    token_hash = hash_invitation_token(raw_token)

    # Store only the hash
    new_invitation = models.InterviewInvitation(
        candidate_id=screening.candidate_id,
        screening_id=screening.screening_id,
        token_hash=token_hash,
        expires_at=get_invitation_expiry(),
        status="Pending"
    )

   
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    # Development-only invitation link
    interview_link = (
        f"http://localhost:8501/interview?token={raw_token}"
    )

    return {
        "invitation_id": new_invitation.invitation_id,
        "candidate_id": new_invitation.candidate_id,
        "screening_id": new_invitation.screening_id,
        "status": new_invitation.status,
        "expires_at": new_invitation.expires_at,
        "interview_link": interview_link
    }


# ==========================================
# AGENT 2 - VALIDATE INTERVIEW INVITATION
# ==========================================

@app.get("/invitations/validate")
def validate_interview_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    # Hash the received token
    token_hash = hash_invitation_token(token)

    # Find invitation
    invitation = db.query(
        models.InterviewInvitation
    ).filter(
        models.InterviewInvitation.token_hash == token_hash
    ).first()

    # Invalid token
    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invalid invitation link"
        )

    # Already used
    if invitation.used_at is not None:
        raise HTTPException(
            status_code=403,
            detail="Invitation link has already been used"
        )

    # Expired token
    if is_invitation_expired(invitation.expires_at):
        raise HTTPException(
            status_code=403,
            detail="Invitation link has expired"
        )

    # Validate invitation status
    if invitation.status not in ["Pending", "Sent"]:
        raise HTTPException(
            status_code=403,
            detail="Invitation is not active"
        )

    return {
        "valid": True,
        "screening_id": invitation.screening_id,
        "message": "Invitation is valid"
    }


# ==========================================
# AGENT 2 - REDEEM INTERVIEW INVITATION
# ==========================================

from sqlalchemy import update

@app.post("/invitations/redeem")
def redeem_interview_invitation(
    request: schemas.InvitationRedeem,
    db: Session = Depends(get_db)
):
    token_hash = hash_invitation_token(request.token)
    now = datetime.utcnow()

    # Atomically redeem an active invitation
    result = db.execute(
        update(models.InterviewInvitation)
        .where(
            models.InterviewInvitation.token_hash == token_hash,
            models.InterviewInvitation.used_at.is_(None),
            models.InterviewInvitation.expires_at > now,
            models.InterviewInvitation.status.in_(["Pending", "Sent"])
        )
        .values(
            used_at=now,
            status="Redeemed"
        )
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Invitation is invalid, expired, or already used"
        )

    invitation = db.query(models.InterviewInvitation).filter(
        models.InterviewInvitation.token_hash == token_hash
    ).first()

    db.commit()

    session_token = create_candidate_session_token(
        screening_id=invitation.screening_id,
        candidate_id=invitation.candidate_id
    )

    return {
        "message": "Invitation redeemed successfully",
        "screening_id": invitation.screening_id,
        "session_token": session_token,
        "token_type": "bearer",
        "expires_in_minutes": 30
    }


# ==========================================
# AGENT 2 - VERIFY CANDIDATE SESSION
# ==========================================

candidate_bearer = HTTPBearer(auto_error=False)


def get_current_candidate_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(candidate_bearer),
    db: Session = Depends(get_db)
):
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired candidate session",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = verify_candidate_session_token(
            credentials.credentials
        )

        candidate_id = int(payload["sub"])
        screening_id = int(payload["screening_id"])

    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise unauthorized

    screening = db.query(models.Screening).filter(
        models.Screening.screening_id == screening_id,
        models.Screening.candidate_id == candidate_id
    ).first()

    if not screening:
        raise unauthorized

    return screening


@app.get("/candidate-session/me")
def get_candidate_session(
    screening: models.Screening = Depends(
        get_current_candidate_session
    )
):
    return {
        "authenticated": True,
        "screening_id": screening.screening_id,
        "call_status": screening.call_status,
        "consent_status": screening.consent_status
    }



   