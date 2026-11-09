from fastapi import UploadFile, File, HTTPException
from pathlib import Path
import uuid
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine, Base

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="HR Hiring Automation System")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test endpoint
@app.get("/")
def home():
    return {"message": "HR Hiring Automation API is running!"}


# Create a job requisition
@app.post("/requisitions", response_model=schemas.RequisitionResponse)
def create_requisition(
    requisition: schemas.RequisitionCreate,
    db: Session = Depends(get_db)
):
    new_requisition = models.Requisition(**requisition.model_dump())

    db.add(new_requisition)
    db.commit()
    db.refresh(new_requisition)

    return new_requisition


# Get all job requisitions
@app.get("/requisitions", response_model=list[schemas.RequisitionResponse])
def get_requisitions(db: Session = Depends(get_db)):
    requisitions = db.query(models.Requisition).all()
    return requisitions

# Register a new candidate
@app.post("/candidates", response_model=schemas.CandidateResponse)
def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db)
):
    new_candidate = models.Candidate(**candidate.model_dump())

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate


# Get all candidates
@app.get("/candidates", response_model=list[schemas.CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).all()
    return candidates

@app.post("/candidates/{candidate_id}/resume")
async def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Find candidate
    candidate = db.query(models.Candidate).filter(
        models.Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # Validate file format
    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    # Read and validate file size
    content = await file.read()

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 5 MB"
        )

    # Generate a unique filename
    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)

    # Save file location in database
    candidate.resume_path = f"uploads/{filename}"

    db.commit()
    db.refresh(candidate)

    return {
        "message": "Resume uploaded successfully",
        "candidate_id": candidate.candidate_id,
        "resume_path": candidate.resume_path
    }

# Retrieve all saved resume evaluations
@app.get(
    "/evaluations",
    response_model=list[schemas.ResumeEvaluationResponse]
)
def get_evaluations(db: Session = Depends(get_db)):

    evaluations = db.query(
        models.ResumeEvaluation
    ).all()

    return evaluations

@app.patch("/evaluations/{evaluation_id}/review")
def review_evaluation(
    evaluation_id: int,
    review: schemas.EvaluationReviewRequest,
    db: Session = Depends(get_db)
):
    # Find the evaluation
    evaluation = db.query(models.ResumeEvaluation).filter(
        models.ResumeEvaluation.evaluation_id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    # Update HR review status
    evaluation.review_status = review.review_status

    db.commit()
    db.refresh(evaluation)

    return {
        "message": "HR review updated successfully",
        "evaluation_id": evaluation.evaluation_id,
        "review_status": evaluation.review_status
    }


@app.patch("/requisitions/{requisition_id}/approve")
def approve_requisition(
    requisition_id: int,
    db: Session = Depends(get_db)
):
    # Find the requisition
    requisition = db.query(models.Requisition).filter(
        models.Requisition.requisition_id == requisition_id
    ).first()

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    # Prevent repeated approval
    if requisition.status == "Approved":
        raise HTTPException(
            status_code=400,
            detail="Requisition is already approved"
        )

    # Make sure the rubric exists
    if not requisition.rubric:
        raise HTTPException(
            status_code=400,
            detail="Cannot approve a requisition without a scoring rubric"
        )

    # Mark requisition as approved
    requisition.status = "Approved"

    db.commit()
    db.refresh(requisition)

    return {
        "message": "Requisition approved successfully",
        "requisition_id": requisition.requisition_id,
        "status": requisition.status
    }
