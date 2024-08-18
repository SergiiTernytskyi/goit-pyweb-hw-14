import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema

from src.repository.contacts import (get_contacts, get_contact_by_id, create_contact, update_contact, delete_contact)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, first_name=None, last_name=None, email=None, upcomming_birthday=None, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactSchema(first_name='Bob', last_name='Bobster', email='sample@mail.com', phone_number='+380999999999', birth_date='2024-08-04', additional_info="hello")
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertTrue(hasattr(result, "id"))

    async def test_delete_contact_found(self):
        note = Contact()
        self.session.query().filter().first.return_value = note
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdateSchema(first_name='Bob', last_name='Bobster', email='sample@mail.com', phone_number='+380999999999', birth_date='2024-08-04', additional_info="hello")
        contact = Contact(email='sample111@mail.com')
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdateSchema(first_name='Bob', last_name='Bobster', email='sample@mail.com', phone_number='+380999999999', birth_date='2024-08-04', additional_info="hello")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

