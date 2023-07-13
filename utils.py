from datetime import timedelta, datetime
import jwt
from databases.core import Connection
from passlib.context import CryptContext
from passlib.hash import bcrypt
from smtplib import SMTP
import models
import settings
import db
from models import NewUserData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    password_hash = bcrypt.hash(password)
    return password_hash


def notify_about_account_creation(user: NewUserData):
    msg = f'''Your account has been created
Data for authorization
Login: {user.login},
Password: {user.password}'''
    send_email_to_user(user.email, msg)


def send_email_to_user(user_email: str, message: str):
    email_controller = SMTP()
    email_controller.connect(settings.EMAIL_DOMEN_NAME, settings.EMAIL_PORT)
    email_controller.starttls()
    email_controller.login(settings.EMAIL_LOGIN, settings.EMAIL_PASSWORD)
    email_controller.sendmail(settings.EMAIL_LOGIN, user_email, message)
    email_controller.quit()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(login: str, password: str, session: Connection) -> models.User:
    user = await db.get_user_by_login(login, session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def unite_dicts(main_dict: dict, new_dict: dict) -> dict:
    new_dict = {item: new_dict.get(item) for item in new_dict if new_dict.get(item) is not None}
    return main_dict | new_dict
