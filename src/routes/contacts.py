from typing import List

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Query,Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User, Role
from src.schemas.contacts import ContactModel, ContactResponse   #, ContactStatusUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.roles import RoleAccess
#from src.schemas import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])
#router = APIRouter(prefix='/contacts', contacts=["contacts"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def read_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),\
                         db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of cntacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int = Path(ge=1),\
                        db: AsyncSession = Depends(get_db),\
                              user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a contact for a specific user with specified pagination parameters.

    :param pcontact_id: The number of contacts to skip.
    :type pcontact_id: int
    :param user: The user to retrieve notes for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A contact.
    :rtype: Contact
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/contacts/", response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def read_contacts_name_or_surname_or_email(limit: int = Query(10, ge=10, le=50), offset: int = Query(0, ge=0),\
                                                firstname: str | None = None,lastname: str | None = None, email: str | None = None,\
                                                db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of cntacts to return.
    :type limit: int
    :param firstname: Firstname param.
    :type firstname: str
    :param lastname: Lastname param.
    :type lastname: str
    :param email: Lastname param.
    :type email: str
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contscts.
    :rtype: List[Contact]
    """
    contact = await repository_contacts.get_contact_firstname(limit,offset,firstname, lastname, email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/birthday/", response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=1, seconds=20))],tags=["contacts"])
async def read_contacts_birthday(skip: int = 0, limit: int = 10,\
                                  db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of cntacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of Contact.
    :rtype: List[Contact]
    """
    contact = await repository_contacts.get_contact_birthday(skip, limit, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact



@router.post("/", response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def create_contact(body: ContactModel, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Create contact

    :param body: Body class ContactModel.
    :type body: ContactModel
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of notes.
    :rtype: Contact
    """
    return await repository_contacts.create_contact(body, db, user)


@router.put("/{contact_id}", response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def update_contact(body: ContactModel, contact_id: int, db:\
                          AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Update contact

    :param body: Body class ContactModel.
    :type body: ContactModel
    :param contact_id: Body class ContactModel.
    :type contact_id: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A Contact.
    :rtype: Contact
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

# @router.patch("/{contact_id}", response_model=ContactResponse)
# async def update_status_contact(body: ContactStatusUpdate, contact_id: int, db: Session = Depends(get_db)):
#     contact = await repository_contacts.update_status_contact(contact_id, body, db)
#     if contact is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
#     return contact


@router.delete("/{contact_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Remove contact

    :param contact_id: Contact id.
    :type contact_id: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A Contact.
    :rtype: Contact
    """
    contact = await repository_contacts.remove_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact