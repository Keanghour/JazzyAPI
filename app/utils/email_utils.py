import smtplib
from email.message import EmailMessage
from pydantic import BaseSettings

class EmailSettings(BaseSettings):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str

    class Config:
        env_file = ".env"

settings = EmailSettings()

def send_email(to_email: str, subject: str, content: str) -> None:
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
