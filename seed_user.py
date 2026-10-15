import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parent / "app" / ".env")

from app.db.database import SessionLocal
from app.repositories.user_repository import get_user_by_email, create_user
from app.utils.password import hash_password


def seed():

    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    name = os.getenv("ADMIN_NAME", "Admin")

    if not email or not password:
        print(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD env vars before running this script.",
            file=sys.stderr
        )
        sys.exit(1)

    db = SessionLocal()
    try:
        user = get_user_by_email(db=db, email=email)

        if user is None:
            user = create_user(
                db=db,
                name=name,
                email=email,
                password_hash=hash_password(password)
            )
            user.is_verified = True
            user.role = "admin"
            db.commit()
            db.refresh(user)
            print(f"Created admin user id={user.id} email={user.email}")
        else:
            user.password_hash = hash_password(password)
            user.is_verified = True
            user.role = "admin"
            db.commit()
            print(f"Updated admin user id={user.id} email={user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
