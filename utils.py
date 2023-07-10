from passlib.hash import bcrypt
from smtplib import SMTP
import settings
from models import NewUserData


def get_password_hash(password: str) -> str:
    password_hash = bcrypt.hash(password)
    return password_hash


def notify_about_account_creation(email_contoller: SMTP, user: NewUserData):
    msg = f'''Your account has been created
Data for authorization
Login: {user.login},
Password: {user.password}'''
    send_email_to_user(email_contoller, user.email, msg)


def send_email_to_user(email_controller: SMTP, user_email: str, message: str):
    email_controller.sendmail(settings.EMAIL_LOGIN, user_email, message)


