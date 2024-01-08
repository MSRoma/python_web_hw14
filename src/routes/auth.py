
import random

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse,RequestEmail,UserSchemaChangePasword,UserSchemaResetPasword
from src.services.auth import auth_service
from src.services.email import send_email, send_email_reset_pass
from src.config import messages

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
async def signup(body: UserSchema,bt: BackgroundTasks,request: Request, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a email ,name and password of users.

    :param body: Email ,name and password .
    :type body: UserSchema
    :param bt: Background tasks
    :type bt: BackgroundTasks
    :param request: Request param.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: A list of notes.
    :rtype: User
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login",  response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Retrieves a email and password of users.

    :param body: Email and password .
    :type body: UserSchema
    :param bt: Background tasks
    :type bt: BackgroundTasks
    :param request: Request param.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: A list of notes.
    :rtype:  User
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/change_password", response_model=UserResponse, status_code=status.HTTP_201_CREATED,dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def change_password(body: UserSchemaChangePasword,bt: BackgroundTasks,request: Request, db: AsyncSession = Depends(get_db)):
    """
    Change password.

    :param body: Email and password .
    :type body: UserSchema
    :param bt: Background tasks
    :type bt: BackgroundTasks
    :param request: Request param.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: New user pass.
    :rtype: User
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    body.new_password = auth_service.get_password_hash(body.new_password)
    new_user_pass = await repositories_users.pass_change(body, db)
    return new_user_pass

@router.post("/reset_password", response_model=UserResponse, status_code=status.HTTP_201_CREATED,dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def reset_password(body: UserSchemaResetPasword,bt: BackgroundTasks,request: Request, db: AsyncSession = Depends(get_db)):
    """
    Reset password .

    :param body: Email and password .
    :type body: UserSchema
    :param bt: Background tasks
    :type bt: BackgroundTasks
    :param request: Request param.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: New user pass.
    :rtype: User
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    
    chars = '7'  #'+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 8
    random_password =''
    for i in range(length):
        random_password += random.choice(chars)
    print(random_password)

    new_password = auth_service.get_password_hash(random_password)
    new_user_pass = await repositories_users.pass_reset(body, new_password, db)
    bt.add_task(send_email_reset_pass,random_password,new_user_pass.email, new_user_pass.username, str(request.base_url))
    return new_user_pass


@router.get('/refresh_token',  response_model=TokenSchema,dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Refresh_token .

    :param credentials: HTTP authorization credentials .
    :type credentials: HTTPAuthorizationCredentials
    :return: Refresh token.
    :rtype: User
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}

@router.get('/confirmed_email/{token}',dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirmed email.

    :param token: token .
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: Email confirmed.
    :rtype: User
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email',dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
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
    :return: A list of notes.
    :rtype: User
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


# @router.get('/{username}',dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
# async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
#     print('--------------------------------')
#     print(f'{username} зберігаємо що він відкрив email в БД')
#     print('--------------------------------')
#     return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")