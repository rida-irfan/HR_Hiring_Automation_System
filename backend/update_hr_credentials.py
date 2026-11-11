
from database import SessionLocal
from models import HRUser
from security import hash_password
from getpass import getpass

db = SessionLocal()

try:
    old_email = "hr.test@example.com"

    hr = db.query(HRUser).filter(
        HRUser.email == old_email
    ).first()

    if not hr:
        print("HR account not found.")
    else:
        new_email = input("Enter new HR email: ").strip().lower()
        new_password = getpass("Enter new HR password: ")
        confirm_password = getpass("Confirm new password: ")

        if not new_email or "@" not in new_email:
            print("Invalid email address.")

        elif len(new_password) < 12:
            print("Password must contain at least 12 characters.")

        elif new_password != confirm_password:
            print("Passwords do not match.")

        elif db.query(HRUser).filter(
            HRUser.email == new_email,
            HRUser.hr_id != hr.hr_id
        ).first():
            print("Email is already registered.")

        else:
            hr.email = new_email
            hr.hashed_password = hash_password(new_password)

            db.commit()

            print("HR email and password updated successfully!")

except Exception as e:
    db.rollback()
    print("Update failed:", type(e).__name__)

finally:
    db.close()
