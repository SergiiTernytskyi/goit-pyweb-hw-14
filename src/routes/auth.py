from typing import List
from datetime import date

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Path,
    Query,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponse, TokenModel
from src.schemas.email import RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db=Depends(get_db),
):
    """
    The signup function creates a new user in the database.
        It takes in a UserModel object, which is validated by pydantic.
        If the email already exists, it raises an HTTPException with status code 409 (Conflict).
        Otherwise, it hashes the password and creates a new user using create_user from repositories/users.py.

    :param body: UserModel: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A user object
    """

    existing_user = await repository_users.get_user_by_email(body.email, db)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )

    body.password = auth_service.create_hashed_password(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/signin", response_model=TokenModel)
async def signin(body: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """
    The signin function allows user to application.
        It takes in a UserModel object, which is validated by pydantic.
        If the user is not in database, it raises an HTTPException with status code 401.
        If the user is not confirmed, it raises an HTTPException with status code 401.
        If the user password is not verified, it raises an HTTPException with status code 401.
        Otherwise, it creates acces and refresh tokens.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Get the database session
    :return: A acces and refresh tokens with type bearer
    """

    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security), db=Depends(get_db)
):
    """
    The refresh_token function creates new refresh token.
        If the refresh token is not in database, it raises an HTTPException with status code 401.
        Otherwise, it creates acces and refresh tokens.

    :param credentials: HTTPAuthorizationCredentials: Validate the credentials
    :param db: Session: Get the database session
    :return: A acces and refresh tokens with type bearer
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})

    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db=Depends(get_db)):
    """
    The confirmed_email function changes the state of user in databese to confirmed.
        If the user is not in database, it raises an HTTPException with status code 401.
        Otherwise, it creates acces and refresh tokens.

    :param token: str: Token string
    :param db: Session: Get the database session
    :return: A acces and refresh tokens with type bearer
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    await repository_users.confirme_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db=Depends(get_db),
):
    """
    The request_email function sends the email to change the status cinfirmed.
        If the user is not confirmed in database, it raises an HTTPException with status code 401.
        Otherwise, it creates acces and refresh tokens.

    :param body: RequestEmail: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A successfull message
    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )

    return {"message": "Check your email for confirmation."}
