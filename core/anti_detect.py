import re
import random
import string
import base64
import time
from datetime import datetime

class AntiDetectEngine:
    CLIENT_USER_AGENTS = [
        'Apple Mail (2.3654.120.0.1)',
        'Mozilla Thunderbird (115.8.0 / Windows NT 10.0)',
        'Microsoft Outlook 16.0.16327.20214',
        'iPhone Mail (20G75)',
        'Google Mail Client v2024.03',
        'Samsung Email / Android 14',
        'Roundcube Webmail/1.6.5'
    ]

    ZERO_WIDTH_CHARS = ['\u200B', '\u200C', '\u200D', '\uFEFF']

    @staticmethod
    def process_spintax(text: str) -> str:
        """
        Recursively processes nested Spintax format: {option1|option2|option3}
        Example: '{Hello|Hi|Greetings} {friend|customer|valued client}'
        """
        if not text:
            return ""
        
        pattern = r'\{([^{}]+)\}'
        while re.search(pattern, text):
            text = re.sub(pattern, lambda m: random.choice(m.group(1).split('|')), text)
        return text

    @staticmethod
    def inject_invisible_noise(text: str, frequency: int = 3) -> str:
        """
        Injects invisible zero-width characters into text to ensure 
        every single sent email has a unique SHA256/MD5 checksum hash.
        This prevents Gmail anti-spam spam filters from matching duplicate payloads!
        """
        if not text:
            return ""
        
        words = text.split(' ')
        noisy_words = []
        for idx, word in enumerate(words):
            if idx % frequency == 0 and len(word) > 2:
                # Inject zero-width char inside word
                split_pos = random.randint(1, len(word) - 1)
                noise = random.choice(AntiDetectEngine.ZERO_WIDTH_CHARS)
                word = word[:split_pos] + noise + word[split_pos:]
            noisy_words.append(word)
        return ' '.join(noisy_words)

    @staticmethod
    def generate_message_id(domain: str = 'gmail.com') -> str:
        """Generates standard compliant random RFC Message-ID header"""
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        timestamp = int(time.time() * 1000)
        return f"<{rand_str}.{timestamp}@{domain}>"

    @staticmethod
    def get_random_client_header() -> str:
        return random.choice(AntiDetectEngine.CLIENT_USER_AGENTS)

    @staticmethod
    def build_universal_link(base_url: str, recipient_email: str, custom_token: str = "") -> str:
        """
        Generates dynamic tracked / universal safe link for inbox delivery.
        """
        if not base_url:
            return "#"
        
        rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        email_b64 = base64.urlsafe_b64encode(recipient_email.encode()).decode().rstrip('=')
        
        separator = '&' if '?' in base_url else '?'
        token_param = f"token={custom_token}&" if custom_token else ""
        return f"{base_url}{separator}{token_param}uid={rand_id}&usr={email_b64}&ts={int(time.time())}"
