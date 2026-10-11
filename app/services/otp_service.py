import random
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_email
from app.repositories.otp_repository import (
    create_otp,
    get_latest_valid_otp
)


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def send_otp(
    db: Session,
    email: str
):

    user = get_user_by_email(
        db=db,
        email=email
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    otp_code = generate_otp()

    expires_at = datetime.utcnow() + timedelta(
        minutes=5
    )

    create_otp(
        db=db,
        user_id=user.id,
        otp_code=otp_code,
        expires_at=expires_at
    )

    # Local development only
    print(f"OTP for {email}: {otp_code}")

    return {
        "message": "OTP generated successfully."
    }


def verify_otp(
    db: Session,
    email: str,
    otp_code: str
):

    user = get_user_by_email(
        db=db,
        email=email
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    otp_record = get_latest_valid_otp(
        db=db,
        user_id=user.id
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="No valid OTP found."
        )

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP has expired."
        )

    if otp_record.otp_code != otp_code:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP."
        )

    otp_record.is_used = True
    user.is_verified = True

    db.commit()

    return {
        "message": "OTP verified successfully."
    }   