
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document


# Project's root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def extract_resume_text(resume_path: str):

    file_path = PROJECT_ROOT / resume_path

    # Check whether the file exists
    if not file_path.is_file():
        raise FileNotFoundError("Resume file not found.")

    extension = file_path.suffix.lower()

    text = ""
    parsing_warnings = []

    # Extract text from PDF
    if extension == ".pdf":

        with fitz.open(file_path) as pdf:

            if len(pdf) == 0:
                parsing_warnings.append(
                    "PDF contains no pages."
                )

            for page_number, page in enumerate(pdf, start=1):

                page_text = page.get_text("text")

                if not page_text.strip():
                    parsing_warnings.append(
                        f"Page {page_number} has no extractable text. "
                        "It may contain scanned images."
                    )

                text += page_text + "\n"

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
                row_text = " | ".join(
                    cell.text for cell in row.cells
                )

                if row_text.strip():
                    text += "\n" + row_text

    else:
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    # Check whether any text was extracted
    if not text.strip():

        parsing_warnings.append(
            "No readable text could be extracted from this resume."
        )

    return text.strip(), parsing_warnings
