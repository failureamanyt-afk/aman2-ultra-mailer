import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from typing import Tuple

class GmailMailer:
    @staticmethod
    def send_email(account: dict, recipient: str, msg: MIMEMultipart, timeout: int = 20) -> Tuple[bool, str]:
        smtp_host = account.get('smtp_host', 'smtp.gmail.com')
        smtp_port = int(account.get('smtp_port', 465))
        use_ssl = account.get('ssl', True)
        username = account.get('email', '')
        password = account.get('app_password', '')

        if not username or not password:
            return False, 'Sender email or App Password is missing'

        try:
            if use_ssl or smtp_port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=timeout) as server:
                    server.login(username, password)
                    server.sendmail(username, [recipient], msg.as_string())
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(username, password)
                    server.sendmail(username, [recipient], msg.as_string())
            return True, 'Sent successfully'
        except smtplib.SMTPAuthenticationError as e:
            return False, f'Authentication failed: {e}'
        except smtplib.SMTPConnectError as e:
            return False, f'Connection error: {e}'
        except Exception as e:
            return False, f'Error: {str(e)}'

    @staticmethod
    def test_connection(account: dict) -> Tuple[bool, str]:
        smtp_host = account.get('smtp_host', 'smtp.gmail.com')
        smtp_port = int(account.get('smtp_port', 465))
        use_ssl = account.get('ssl', True)
        username = account.get('email', '')
        password = account.get('app_password', '')

        try:
            if use_ssl or smtp_port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=10) as server:
                    server.login(username, password)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(username, password)
            return True, 'Connected and Authenticated successfully!'
        except Exception as e:
            return False, str(e)
