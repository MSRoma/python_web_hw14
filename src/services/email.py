from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.config.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="TODO Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send email.

    :param email: Send email .
    :type email: EmailStr
    :param username: The maximum number of cntacts to return.
    :type username: str
    :param host: Host.
    :type host: str
    :return: FastMail.
    :rtype: FastMail
    """    
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)

async def send_email_reset_pass(password, email: EmailStr, username: str, host: str):
    """
    Send email reset pass.

    :param email: Send email reset pass .
    :type email: EmailStr
    :param username: Username.
    :type username: str
    :param password: Host.
    :type password: str
    :return: FastMail.
    :rtype: FastMail
    """   
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset password ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification,"password": password},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_reset_pass.html")
    except ConnectionErrors as err:
        print(err)