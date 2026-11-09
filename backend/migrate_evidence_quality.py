
from sqlalchemy import text
from database import engine

# Add evidence_quality column safely
with engine.begin() as connection:

    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "evidence_quality" not in column_names:

        connection.execute(
            text("""
                ALTER TABLE resume_evaluations
                ADD COLUMN evidence_quality JSON
            """)
        )

        print("evidence_quality column added successfully!")

    else:
        print("evidence_quality column already exists!")
