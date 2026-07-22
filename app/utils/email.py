import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to: str, subject: str, body: str):
    msg = MIMEMultipart()

    msg["From"] = settings.SMTP_MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT), timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"email envoyer a {to}")

    except Exception as e:
        print(f"Erreur d'envoi : {e}")


def send_html_mail(to: str, subject: str, title: str, message: str, button_text: str = None, button_link: str = None):
    msg = MIMEMultipart("alternative")

    msg["From"] = settings.SMTP_MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject

    button_html = ""
    if button_text and button_link:
        button_html = f'<p><a href="{button_link}" style="background-color:#2d6cdf;color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;">{button_text}</a></p>'

    html = f"""
    <html>
        <body style="font-family:sans-serif;">
            <h2>{title}</h2>
            <p>{message}</p>
            {button_html}
        </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT), timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"email envoyer a {to}")

    except Exception as e:
        print(f"Erreur d'envoi : {e}")
