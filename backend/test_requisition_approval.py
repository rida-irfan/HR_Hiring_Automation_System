
from database import SessionLocal
from models import Requisition


def check_requisition_approval(requisition_id):
    db = SessionLocal()

    try:
        requisition = db.query(Requisition).filter(
            Requisition.requisition_id == requisition_id
        ).first()

        if not requisition:
            return "Requisition not found."

        if requisition.status != "Approved":
            return "BLOCKED: Requisition must be approved by HR."

        return "ALLOWED: Requisition is approved."

    finally:
        db.close()


# Test an approved requisition
print("Requisition 5:")
print(check_requisition_approval(5))

# Test an unapproved requisition
print("\nRequisition 1:")
print(check_requisition_approval(1))
