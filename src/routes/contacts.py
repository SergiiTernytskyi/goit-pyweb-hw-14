from typing import List
from datetime import date

from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.contacts import ContactSchema, ContactResponse, ContactUpdateSchema
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.database.models import User


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    upcomming_birthday: bool = None,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function gets a contacts list from the database.

    :param skip: int: Skip the first n of contacts
    :param limit: int: Limit the number of contacts returned
    :param first_name: str: First name of contact
    :param last_name: str: Last name of contact
    :param email: str: Email of contact
    :param upcomming_birthday: bool: Filter the upcomming birthday of contact
    :param user: User: Filter the contacts by user
    :param db: Session: Get the database session
    :return: A list of contacts objects
    """
    contacts = await repository_contacts.get_contacts(
        skip, limit, first_name, last_name, email, upcomming_birthday, db, user
    )
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact_by_id(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact_by_id function gets a contact from the database by id.

    :param contact_id: int: Contact id to get
    :param user: User: Filter the contacts by user
    :param db: Session: Get the database session
    :return: A list of contacts objects
    """

    contact = await repository_contacts.get_contact_by_id(contact_id, db, user)
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    status_code=status.HTTP_201_CREATED,
)
async def add_contact(
    body: ContactSchema,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The add_contact function creates a contact in the database.

    :param body: ContactSchema: Validate the request body
    :param user: User: Filter the contacts by user
    :param db: Session: Get the database session
    :return: A contact object
    """

    return await repository_contacts.create_contact(body, db, user)


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def update_contact(
    contact_id: int,
    body: ContactUpdateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
        It takes in a ContactUpdateSchema object, which is validated by pydantic.
        If the contact not in database, it raises an HTTPException with status code 404.
        Otherwise, it returns contact object.

    :param body: ContactUpdateSchema: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param user: User: Filter the contacts by user
    :param db: Session: Get the database session
    :return: A contact object
    """

    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The delete_contact function deletes a contact in the database.
        It takes in a contact id.
        If the contact not in database, it raises an HTTPException with status code 404.
        Otherwise, it returns contact object and deletes a contact in the database.

    :param contact_id: int: Contact id
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param user: User: Filter the contacts by user
    :param db: Session: Get the database session
    :return: A contact object
    """

    contact = await repository_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
