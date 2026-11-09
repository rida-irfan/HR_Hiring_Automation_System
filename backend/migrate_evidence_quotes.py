
from sqlalchemy import text
from database import engine

# Add the new column without deleting existing data
with engine.begin() as connection:

    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "evidence_quotes" not in column_names:

        connection.execute(
            text("""
                ALTER TABLE resume_evaluations
                ADD COLUMN evidence_quotes JSON
            """)
        )

        print("evidence_quotes column added successfully!")

    else:
        print("evidence_quotes column already exists!")
