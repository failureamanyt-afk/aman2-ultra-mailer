import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from typing import Tuple

class GmailMailer:
    @staticmethod
    def send_email(account: dict, recipient: str, msg: MIMEMultipart, timeout: int = 20) -> Tuple[bool, str]:
        username = account.get('email', '').strip()
        password = account.get('app_password', '').replace(' ', '').strip()

        if not username or not password:
            return False, 'Sender email or App Password is missing'

        # Attempt 1: Port 587 (STARTTLS) - standard for modern cloud networks
        try:
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=timeout) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.sendmail(username, [recipient], msg.as_string())
            return True, 'Sent successfully'
        except smtplib.SMTPAuthenticationError as e:
            return False, f'Authentication failed: {e}'
        except Exception:
            pass

        # Attempt 2: Port 465 (SSL fallback)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=timeout) as server:
                server.login(username, password)
                server.sendmail(username, [recipient], msg.as_string())
            return True, 'Sent successfully'
        except smtplib.SMTPAuthenticationError as e:
            return False, f'Authentication failed: {e}'
        except Exception as e:
            return False, f'Error: {str(e)}'

    @staticmethod
    def test_connection(account: dict) -> Tuple[bool, str]:
        username = account.get('email', '').strip()
        password = account.get('app_password', '').replace(' ', '').strip()

        if not username or not password:
            return False, 'Email and App Password are required'

        # Try Port 587 first
        try:
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=8) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
            return True, 'Connected & Verified via Port 587 (TLS)!'
        except smtplib.SMTPAuthenticationError as e:
            return False, f'Gmail Authentication Failed: Please check App Password. ({e})'
        except Exception:
            pass

        # Try Port 465 fallback
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=8) as server:
                server.login(username, password)
            return True, 'Connected & Verified via Port 465 (SSL)!'
        except smtplib.SMTPAuthenticationError as e:
            return False, f'Gmail Authentication Failed: Please check App Password. ({e})'
        except Exception as e:
            return False, str(e)
