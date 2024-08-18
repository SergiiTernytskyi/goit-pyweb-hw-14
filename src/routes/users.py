import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.config.config import config
from src.schemas.users import UserDbModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDbModel)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function takes in a current user, and returns user object

    :param current_user: User: Validate the request body
    :return: A user object
    """
    return current_user


@router.patch("/avatar", response_model=UserDbModel)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_avatar_user function takes in a file of avatar, and updates user in database.

    :param file: UploadFile: Validate the file
    :param current_user: User: Validate the current user
    :param db: Session: Get the database session
    :return: A user object
    """

    cloudinary.config(
        cloud_name=config.cloudinary_name,
        api_key=config.cloudinary_api_key,
        api_secret=config.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"NotesApp/{current_user.username}", overwrite=True
    )

    src_url = cloudinary.CloudinaryImage(f"NotesApp/{current_user.username}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )

    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
