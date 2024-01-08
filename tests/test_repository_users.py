import sys
sys.path.append('../')

import unittest

from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import  User
from src.schemas.user import UserSchema, UserSchemaChangePasword, UserSchemaResetPasword, UserResponse, TokenSchema, RequestEmail 
from src.repository.users import (
    get_user_by_email,
    create_user,
    pass_change,
    pass_reset,
    update_token,
    confirmed_email,
    update_avatar_url,
)




class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)

    async def test_get_user_by_email(self):
        user = User(
            id=1,
            username="test user_1",
            email="tesmail@i.ua",
            password= "12345678",
            avatar="https://test.test.ua",
            refresh_token="test token_1"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email="email@test.ua", db=self.session)
        self.assertEqual(result, user)

    async def test_pass_change(self):
        body = UserSchemaChangePasword(
            username="test user_1",
            email="tesmail@i.ua",
            password= "12345678",
            new_password= "87654321"
        )
        user = User(
            id=1,
            username="test user_1",
            email="tesmail@i.ua",
            password= "87654321",
            avatar="https://test.test.ua",
            refresh_token="test token_1"
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_contact
        result = await pass_change(body, db=self.session)
        self.assertEqual(result, user)
        
    async def test_pass_reset(self):
        body = UserSchemaResetPasword(
            username="test user_1",
            email="tesmail@i.ua",
        )
        user = User(
            id=1,
            username="test user_1",
            email="tesmail@i.ua",
            password= "87654321",
            refresh_token="test token_1"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await pass_reset(body, new_password='87654321', db=self.session)
        self.assertEqual(result, user)


    async def test_create_user(self):
        body = User(
            id=1,
            username="test user_1",
            email="tesmail@i.ua",
            password= "12345678",
            avatar="https://www.gravatar.com/avatar/d3a861d6423f78f33d8bd198ce393ff5",
            refresh_token="test token_1"
            )
        result = await create_user(UserSchema(username="test user_1", email="tesmail@i.ua",password= "12345678"), self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, body.avatar)

    
    async def test_update_avatar_url(self):
        user = User(
            email="tesmail@i.ua",
            avatar="https://www.test.com/avatar/555"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await update_avatar_url(email="tesmail@i.ua", url="https://www.test.com/avatar/555", db=self.session)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.avatar, user.avatar)



if __name__ == '__main__':
    unittest.main()
