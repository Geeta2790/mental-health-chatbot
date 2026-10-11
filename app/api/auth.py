from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    SendOTPRequest,
    VerifyOTPRequest,
    MessageResponse,
    LoginRequest,
    TokenResponse
)
from app.services.auth_service import signup_user

    


from app.services.otp_service import (
    send_otp,
    verify_otp
)

from app.services.auth_service import (
    signup_user,
    login_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=201
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    user = signup_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password
    )

    return user

@router.post(
    "/send-otp",
    response_model=MessageResponse
)
def send_signup_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):

    return send_otp(
        db=db,
        email=request.email
    )


@router.post(
    "/verify-otp",
    response_model=MessageResponse
)
def verify_signup_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    return verify_otp(
        db=db,
        email=request.email,
        otp_code=request.otp
    )

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    return login_user(
        db=db,
        email=request.email,
        password=request.password
    )

