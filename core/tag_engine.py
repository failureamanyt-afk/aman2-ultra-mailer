import re
import random
import string
import base64
from datetime import datetime
from core.anti_detect import AntiDetectEngine

class TagEngine:
    @staticmethod
    def generate_random_string(length=8, digits_only=False, letters_only=False):
        if digits_only:
            return ''.join(random.choices(string.digits, k=length))
        if letters_only:
            return ''.join(random.choices(string.ascii_uppercase, k=length))
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def process_tags(text: str, recipient_email: str = "", recipient_name: str = "", 
                     tfn1: str = "", tfn2: str = "", tfn1_base64: bool = False, tfn2_base64: bool = False,
                     universal_url: str = "", enable_anti_detect: bool = True) -> str:
        if not text:
            return ""

        # 1. Process Spintax first: {Hello|Hi|Greetings}
        text = AntiDetectEngine.process_spintax(text)

        now = datetime.now()
        
        # Prepare TFN values
        tfn1_val = base64.b64encode(tfn1.encode()).decode() if tfn1_base64 else tfn1
        tfn2_val = base64.b64encode(tfn2.encode()).decode() if tfn2_base64 else tfn2

        # Extract name from email if empty
        if not recipient_name and recipient_email and "@" in recipient_email:
            recipient_name = recipient_email.split("@")[0].capitalize()

        # Build dynamic universal link if requested
        univ_link = AntiDetectEngine.build_universal_link(universal_url, recipient_email)

        # Direct replacements
        replacements = {
            "#DATE#": now.strftime("%d/%m/%Y"),
            "#TIME#": now.strftime("%H:%M:%S"),
            "#DATETIME#": now.strftime("%d/%m/%Y %H:%M:%S"),
            "#TFN#": tfn1_val,
            "#TFN1#": tfn1_val,
            "#TFNA#": tfn2_val,
            "#TFN2#": tfn2_val,
            "#EMAIL#": recipient_email,
            "{{email}}": recipient_email,
            "[email]": recipient_email,
            "#NAME#": recipient_name,
            "{{name}}": recipient_name,
            "[name]": recipient_name,
            "#ORDER_ID#": "ORD-" + TagEngine.generate_random_string(8),
            "#INVOICE_ID#": "INV-" + TagEngine.generate_random_string(6, digits_only=True),
            "#UNIVERSAL_LINK#": univ_link,
            "#SAFE_LINK#": univ_link,
            "#LINK#": univ_link
        }

        for tag, val in replacements.items():
            text = text.replace(tag, str(val))

        # Dynamic regex replacements for #RANDOM# and #RANDOM_N#
        text = re.sub(r'#RANDOM#', lambda m: TagEngine.generate_random_string(8), text)
        text = re.sub(r'#RANDOM_DIGITS(?:_(\d+))?#', lambda m: TagEngine.generate_random_string(int(m.group(1)) if m.group(1) else 6, digits_only=True), text)
        text = re.sub(r'#RANDOM_LETTERS(?:_(\d+))?#', lambda m: TagEngine.generate_random_string(int(m.group(1)) if m.group(1) else 6, letters_only=True), text)
        text = re.sub(r'#RANDOM_HEX#', lambda m: f"{random.randint(0x100000, 0xFFFFFF):06X}", text)

        # 3. Inject invisible anti-spam noise if enabled
        if enable_anti_detect:
            # Inject subtle noise in text without breaking HTML tags
            parts = re.split(r'(<[^>]+>)', text)
            noisy_parts = []
            for part in parts:
                if part.startswith('<') and part.endswith('>'):
                    noisy_parts.append(part)
                else:
                    noisy_parts.append(AntiDetectEngine.inject_invisible_noise(part, frequency=4))
            text = ''.join(noisy_parts)

        return text
