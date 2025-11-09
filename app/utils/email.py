import smtplib
from email.mime.text import MIMEText
from email.mime.text.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to: str, subject: str, body: str):
    msg = MIMEMultipart()

    msg["From"] = settings.SMTP_MAIL_FROM
    msg["to"] = to
    msg["subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
             server.starttls()
             server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
             server.send_message(msg)
      
        
