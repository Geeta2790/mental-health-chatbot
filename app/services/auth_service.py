from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    get_user_by_email,
    create_user
)

from app.utils.password import hash_password


from app.utils.password import (
    hash_password,
    verify_password
)

from app.utils.jwt import create_access_token


def signup_user(
    db: Session,
    name: str,
    email: str,
    password: str
):

    existing_user = get_user_by_email(
        db=db,
        email=email
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered."
        )

    hashed_password = hash_password(password)

    user = create_user(
        db=db,
        name=name,
        email=email,
        password_hash=hashed_password
    )

    return user

def login_user(
    db: Session,
    email: str,
    password: str
):

    user = get_user_by_email(
        db=db,
        email=email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        plain_password=password,
        hashed_password=user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your account first."
        )

    access_token = create_access_token(
        user_id=user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
