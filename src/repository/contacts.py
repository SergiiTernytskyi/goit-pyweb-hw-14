from datetime import date, datetime, timedelta
from typing import List, Optional, Type

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema


async def get_contacts(
    skip: int,
    limit: int,
    first_name: Optional[str],
    last_name: Optional[str],
    email: Optional[str],
    upcomming_birthday: Optional[bool],
    db: Session,
    user: User,
) -> List[Contact]:
    """
    The get_contacts function returns the contacts list.

    :param skip: Skip the first n of contacts
    :type skip: int
    :param limit: Limit the number of contacts returned
    :type limit: int
    :param first_name: First name of contact
    :type first_name: str
    :param last_name: Last name of contact
    :type last_name: str
    :param email: Email of contact
    :type email: str
    :param upcomming_birthday: Upcomming birthday of contact
    :type upcomming_birthday: bool
    :param db: Pass a database connection to the function
    :type db: Session
    :param user: Filter the contacts by user
    :type user: User
    :return: A list of contacts objects
    """

    print(user)

    query = db.query(Contact).filter(Contact.user_id == user.id)

    today_date = datetime.today()
    upcoming_week = today_date + timedelta(days=7)

    if first_name:
        query = query.filter(Contact.first_name == first_name)
    if last_name:
        query = query.filter(Contact.last_name == last_name)
    if email:
        query = query.filter(Contact.email == email)
    if upcomming_birthday:
        query = query.filter(Contact.birth_date.between(today_date, upcoming_week))

    return query.offset(skip).limit(limit).all()


async def get_contact_by_id(
    contact_id: int,
    db: Session,
    user: User,
) -> Type[Contact] | None:
    """
    The get_contact_by_id function returns the contact, function takes in an id, and returns the object with that id.

    :param contact_id: Specify the id of the contact to get
    :type contact_id: int
    :param db: Pass a database connection to the function
    :type db: Session
    :param user: Filter the contacts by user
    :type user: User
    :return: A contact object
    """

    return (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )


async def create_contact(
    body: ContactSchema,
    db: Session,
    user: User,
) -> Contact:
    """
    The create_contact function creates the contact.

    :param body: Contact parameters
    :type body: ContactSchema
    :param db: Pass a database connection to the function
    :type db: Session
    :param user: Filter the contacts by user
    :type user: User
    :return: A contact object
    """

    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int,
    body: ContactUpdateSchema,
    db: Session,
    user: User,
):
    """
    The update_contact function updates the contact.

    :param contact_id: Specify the id of the contact
    :type contact_id: int
    :param body: Contact parameters
    :type body: ContactSchema
    :param db: Pass a database connection to the function
    :type db: Session
    :param user: Filter the contacts by user
    :type user: User
    :return: A contact object
    """

    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        update_data = body.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


async def delete_contact(
    contact_id: int,
    db: Session,
    user: User,
):
    """
    The delete_contact function deletes the contact, function takes in an id, and deletes the object with that id

    :param contact_id: Specify the id of the contact
    :type contact_id: int
    :param db: Pass a database connection to the function
    :type db: Session
    :param user: Filter the contacts by user
    :type user: User
    :return: A contact object
    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact
