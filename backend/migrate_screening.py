from sqlalchemy import inspect, text
from database import engine

# New columns required for Agent 2
new_columns = {
    "evaluation_id": "INTEGER",
    "call_status": "VARCHAR(50) NOT NULL DEFAULT 'Not Started'",
    "consent_status": "VARCHAR(50) NOT NULL DEFAULT 'Pending'",
    "question_answer_pairs": "JSON",
    "candidate_stated_availability": "TEXT",
    "role_requirement_responses": "JSON",
    "unresolved_questions": "JSON",
    "concise_summary": "TEXT",
    "recommended_next_step_for_human_review": "TEXT",
    "call_timestamp": "DATETIME",
    "review_status": "VARCHAR(50) NOT NULL DEFAULT 'Pending HR Review'"
}

inspector = inspect(engine)

existing_columns = {
    column["name"]
    for column in inspector.get_columns("screenings")
}

with engine.begin() as connection:
    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            connection.execute(
                text(
                    f"ALTER TABLE screenings "
                    f"ADD COLUMN {column_name} {column_type}"
                )
            )

            print(f"Added: {column_name}")

        else:
            print(f"Already exists: {column_name}")

print("\nScreening database migration completed!")