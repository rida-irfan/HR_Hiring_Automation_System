from sqlalchemy import text
from database import engine

# New columns required by Agent 1
new_columns = {
    "missing_or_unclear_items": "JSON",
    "parsing_warnings": "JSON",
    "recommendation_for_human_review": "TEXT"
}

with engine.begin() as connection:

    # Check existing columns
    columns = connection.execute(
        text("PRAGMA table_info(resume_evaluations)")
    ).fetchall()

    existing_columns = [column[1] for column in columns]

    # Add only missing columns
    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            connection.execute(
                text(
                    f"ALTER TABLE resume_evaluations "
                    f"ADD COLUMN {column_name} {column_type}"
                )
            )

            print(f"Added column: {column_name}")

        else:
            print(f"Column already exists: {column_name}")

print("\nDatabase migration completed successfully!")