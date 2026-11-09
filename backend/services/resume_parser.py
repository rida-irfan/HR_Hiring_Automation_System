
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document


# Project's root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def extract_resume_text(resume_path: str) -> str:

    file_path = PROJECT_ROOT / resume_path

    # Check whether the file exists
    if not file_path.exists():
        raise FileNotFoundError("Resume file not found.")

    extension = file_path.suffix.lower()

    # Extract text from PDF
    if extension == ".pdf":
        text = ""

        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text() + "\n"

    # Extract text from DOCX
    elif extension == ".docx":
        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        text = "\n".join(paragraphs)

        # Also extract text from tables
        for table in document.tables:
            for row in table.rows:
                text += "\n" + " | ".join(
                    cell.text for cell in row.cells
                )

    else:
        raise ValueError("Only PDF and DOCX files are supported.")

    if not text.strip():
        raise ValueError(
            "No readable text found in this resume."
        )

    return text.strip()
