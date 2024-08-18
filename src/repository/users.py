from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email, and get the object user with that email

    :param email: Specify the email of the user
    :type email: str
    :param db: Pass a database connection to the function
    :type db: Session
    :return: A user object
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function takes in an user dict, and creates the user with that params

    :param body: Specify the params of the user
    :type body: UserModel
    :param db: Pass a database connection to the function
    :type db: Session
    :return: A user object
    """

    avatar = None

    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function takes in an user, and updates the token

    :param user: Specify the user
    :type user: UserModel
    :param token: Specify the token
    :type token: str | None
    :param db: Pass a database connection to the function
    :type db: Session
    """

    user.refresh_token = token
    db.commit()


async def confirme_email(email: str, db: Session) -> None:
    """
    The confirme_email function takes in an email, and sets status confirmed

    :param email: Specify the user email
    :type email: str
    :param db: Pass a database connection to the function
    :type db: Session
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function takes in an email, avatar url and sets user avatar

    :param email: Specify the user email
    :type email: str
    :param url: Specify the user avatar url
    :type url: str
    :param db: Pass a database connection to the function
    :type db: Session
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
