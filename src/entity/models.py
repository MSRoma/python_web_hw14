import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, func, Table,Enum
from sqlalchemy.orm import relationship ,Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# note_m2m_tag = Table(
#     "note_m2m_tag",
#     Base.metadata,
#     Column("id", Integer, primary_key=True),
#     Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE")),
#     Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
# )

class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    mobilenamber = Column(String(50), nullable=False)
    databirthday = Column('databirthday', DateTime, nullable=False)
    note = Column(String(150), nullable=True)
    createdat = Column('createdat', DateTime, default=func.now())
    
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="todos", lazy="joined")

class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

# class Note(Base):
#     __tablename__ = "notes"
#     id = Column(Integer, primary_key=True)
#     title = Column(String(50), nullable=False)
#     created_at = Column('created_at', DateTime, default=func.now())
#     description = Column(String(150), nullable=False)
#     done = Column(Boolean, default=False)
#     tags = relationship("Tag", secondary=note_m2m_tag, backref="notes")


# class Tag(Base):
#     __tablename__ = "tags"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(25), nullable=False, unique=True)