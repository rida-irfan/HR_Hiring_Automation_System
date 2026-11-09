
from sqlalchemy import text
from database import engine

with engine.begin() as connection:

    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "scoring_review_details" not in column_names:

        connection.execute(
            text("""
                ALTER TABLE resume_evaluations
                ADD COLUMN scoring_review_details JSON
            """)
        )

        print("scoring_review_details column added successfully!")

    else:
        print("scoring_review_details column already exists!")
