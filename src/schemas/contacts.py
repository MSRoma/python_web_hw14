from datetime import datetime,date
from typing import List, Optional
from pydantic import BaseModel, Field


class ContactModel(BaseModel):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: str = Field(max_length=50)
    mobilenamber: str = Field(max_length=50)
    databirthday: date = Field()
    note: str = Field(max_length=50)



class ContactResponse(BaseModel):
    id: int
    firstname: str 
    lastname: str 
    email: str 
    mobilenamber: str 
    databirthday: date
    note: str 

    class Config:
        orm_mode = True



# class ContactResponse(ContactModel):
#     firstname: str 
#     lastname: str 
#     email: str 
#     mobilenamber: str 
#     databirthday: datetime 
#     note: str 

#     class Config:
#         orm_mode = True

# class ContactStatusUpdate():
#     pass


# class NoteBase(BaseModel):
#     title: str = Field(max_length=50)
#     description: str = Field(max_length=150)


# class NoteModel(NoteBase):
#     tags: List[int]


# class NoteUpdate(NoteModel):
#     done: bool


# class NoteStatusUpdate(BaseModel):
#     done: bool


# class NoteResponse(NoteBase):
#     id: int
#     created_at: datetime
#     tags: List[TagResponse]

#     class Config:
#         orm_mode = True