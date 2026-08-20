import json
import os
import threading
from typing import List, Dict, Optional

class AccountManager:
    def __init__(self, data_file: str = None):
        if data_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_file = os.path.join(base_dir, 'data', 'accounts.json')
        else:
            self.data_file = data_file
            
        self.lock = threading.Lock()
        self.accounts: List[Dict] = []
        self.current_index = 0
        self.load_accounts()

    def load_accounts(self):
        with self.lock:
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        self.accounts = json.load(f)
                except Exception:
                    self.accounts = []
            else:
                self.accounts = []

    def save_accounts(self):
        with self.lock:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2)

    def add_account(self, email: str, app_password: str, sender_name: str = '', smtp_host: str = 'smtp.gmail.com', smtp_port: int = 465, ssl: bool = True) -> Dict:
        # Clean app password (remove spaces)
        clean_pwd = app_password.replace(' ', '').strip()
        account = {
            'email': email.strip(),
            'app_password': clean_pwd,
            'sender_name': sender_name.strip(),
            'smtp_host': smtp_host.strip(),
            'smtp_port': int(smtp_port),
            'ssl': bool(ssl),
            'sent_count': 0,
            'status': 'active'
        }
        with self.lock:
            # Check if email already exists, update if so
            for idx, acc in enumerate(self.accounts):
                if acc['email'].lower() == email.lower():
                    self.accounts[idx] = account
                    self.save_accounts_unlocked()
                    return account
            self.accounts.append(account)
            self.save_accounts_unlocked()
            return account

    def save_accounts_unlocked(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2)

    def remove_account(self, email: str):
        with self.lock:
            self.accounts = [a for a in self.accounts if a['email'].lower() != email.lower()]
            self.save_accounts_unlocked()

    def get_all_accounts(self) -> List[Dict]:
        with self.lock:
            return list(self.accounts)

    def get_account_for_send(self, rotate_threshold: int = 5, total_sent_in_batch: int = 0) -> Optional[Dict]:
        with self.lock:
            if not self.accounts:
                return None
            
            if rotate_threshold > 0 and len(self.accounts) > 1:
                # Rotate index based on count
                idx = (total_sent_in_batch // rotate_threshold) % len(self.accounts)
                return self.accounts[idx]
            else:
                return self.accounts[0]

    def increment_sent(self, email: str):
        with self.lock:
            for acc in self.accounts:
                if acc['email'].lower() == email.lower():
                    acc['sent_count'] = acc.get('sent_count', 0) + 1
                    break
            self.save_accounts_unlocked()

    def clear_cache_and_counts(self):
        with self.lock:
            for acc in self.accounts:
                acc['sent_count'] = 0
            self.save_accounts_unlocked()
