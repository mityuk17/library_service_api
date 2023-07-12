from passlib.hash import bcrypt
from smtplib import SMTP
import settings
from models import NewUserData


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


