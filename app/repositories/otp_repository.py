from sqlalchemy.orm import Session
from datetime import datetime

from app.models.otp import OTPVerification


def create_otp(
    db: Session,
    user_id: int,
    otp_code: str,
    expires_at: datetime
):

    otp = OTPVerification(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return otp


def get_latest_valid_otp(
    db: Session,
    user_id: int
):

    return (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.is_used == False
        )
        .order_by(
            OTPVerification.created_at.desc()
        )
        .first()
    )