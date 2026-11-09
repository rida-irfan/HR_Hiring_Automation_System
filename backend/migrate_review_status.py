from sqlalchemy import text
from database import engine

with engine.begin() as connection:
    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "review_status" not in column_names:
        connection.execute(
            text("""
                ALTER TABLE resume_evaluations
                ADD COLUMN review_status VARCHAR(30)
                NOT NULL DEFAULT 'Pending HR Review'
            """)
        )
        print("review_status column added successfully!")
    else:
        print("review_status column already exists!")