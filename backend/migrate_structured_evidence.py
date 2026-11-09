from sqlalchemy import text
from database import engine

with engine.begin() as connection:

    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "structured_evidence" not in column_names:

        connection.execute(
            text("""
                ALTER TABLE resume_evaluations
                ADD COLUMN structured_evidence JSON
            """)
        )

        print("structured_evidence column added successfully!")

    else:
        print("structured_evidence column already exists!")