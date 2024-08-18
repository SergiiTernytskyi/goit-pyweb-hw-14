import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.users import UserModel, UserDbModel, UserResponse

from src.repository.users import (get_user_by_email, create_user, update_token, update_avatar, confirme_email)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(username='serhio', email="test@example.com", password="12345678")
        mock_avatar_url = "http://example.com/avatar.jpg"

        new_user = User(**body.dict(), avatar=mock_avatar_url)
        result = await create_user(body, db=self.session)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(email="test@example.com", refresh_token=None)
        token = "new_refresh_token"

        await update_token(user, token, db=self.session)
        self.assertEqual(user.refresh_token, token)

    async def test_update_token_with_none(self):
        user = User(email="test@example.com", refresh_token=None)
        token = None

        await update_token(user, token, db=self.session)
        self.assertIsNone(user.refresh_token)

    async def test_update_avatar(self):
        email = "test@example.com"
        new_avatar_url = "http://example.com/new_avatar.jpg"
        user = User(email=email, avatar="http://example.com/old_avatar.jpg")

        result = await update_avatar(email, new_avatar_url, db=self.session)
        self.assertEqual(result.avatar, new_avatar_url)


if __name__ == '__main__':
    unittest.main()

