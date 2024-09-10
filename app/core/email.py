# # app\core\email.py

# import os
# from aiosmtplib import send
# from email.message import EmailMessage
# from dotenv import load_dotenv

# load_dotenv("env/.env")

# MAIL_HOST = os.getenv("MAIL_HOST")
# MAIL_PORT = int(os.getenv("MAIL_PORT"))
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# EMAIL_FROM = os.getenv("EMAIL_FROM")

# async def send_email(to_email: str, subject: str, body: str):
#     message = EmailMessage()
#     message["From"] = EMAIL_FROM
#     message["To"] = to_email
#     message["Subject"] = subject
#     message.set_content(body)

#     await send(message, hostname=MAIL_HOST, port=MAIL_PORT, start_tls=True,
#                username=MAIL_USERNAME, password=MAIL_PASSWORD)

# app\core\email.py

import os
from aiosmtplib import send
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv("env/.env")

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await send(message, hostname=MAIL_HOST, port=MAIL_PORT, start_tls=True,
               username=MAIL_USERNAME, password=MAIL_PASSWORD)
