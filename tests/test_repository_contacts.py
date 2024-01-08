import sys
sys.path.append('../')

import unittest

from datetime import datetime, date
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contacts import ContactModel, ContactResponse
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contact_firstname,
    get_contact_birthday,
    create_contact,
    update_contact,
    remove_contact,
)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            ),
            Contact(
            id=2,
            firstname="test firstname_2",
            lastname="test lastname_2",
            email= "test email_2",
            mobilenamber="test mobilenamber_2",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_2",
            user=self.user
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_firstname(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            ),
            Contact(
            id=2,
            firstname="test firstname_2",
            lastname="test lastname_2",
            email= "test email_2",
            mobilenamber="test mobilenamber_2",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_2",
            user=self.user
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contact_firstname(limit, offset, firstname="test firstname_1",email="test email_1",lastname="test lastname_1",user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_birthday(self):
        limit = 10
        offset = 0
        date_now = date.today()
        contacts = [
            Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=date_now,
            note="test note_1",
            user=self.user
            ),
            Contact(
            id=2,
            firstname="test firstname_2",
            lastname="test lastname_2",
            email= "test email_2",
            mobilenamber="test mobilenamber_2",
            databirthday=date_now,
            note="test note_2",
            user=self.user
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contact_birthday(limit, offset,user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactModel(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobilenamber, body.mobilenamber)
        self.assertEqual(result.databirthday, body.databirthday)
        self.assertEqual(result.note, body.note)

    async def test_remove_contact_found(self):
        mocked_todo = MagicMock()
        mocked_todo.scalar_one_or_none.return_value = Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            )
        self.session.execute.return_value = mocked_todo
        result = await remove_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)


    async def test_update_contact(self):
        body =  ContactModel(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            firstname="test firstname_1",
            lastname="test lastname_1",
            email= "test email_1",
            mobilenamber="test mobilenamber_1",
            databirthday=datetime(year=2024,month=1,day=1),
            note="test note_1",
            user=self.user
            )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobilenamber, body.mobilenamber)
        self.assertEqual(result.databirthday, body.databirthday)
        self.assertEqual(result.note, body.note)


if __name__ == '__main__':
    unittest.main()
