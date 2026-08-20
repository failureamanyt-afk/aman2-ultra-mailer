import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AuthManager:
    def __init__(self, data_file: str = None):
        if data_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_file = os.path.join(base_dir, 'data', 'users.json')
        else:
            self.data_file = data_file
            
        self.users: List[Dict] = []
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except Exception:
                self.users = []
        else:
            # Create default Super Admin account
            self.users = [{
                'username': 'admin',
                'password_hash': self._hash_pwd('admin123'),
                'role': 'admin',
                'fullname': 'Super Admin (AMAN2)',
                'daily_limit': 100000,
                'sent_today': 0,
                'total_sent': 0,
                'expiry_date': '2099-12-31',
                'status': 'active',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }]
            self.save_users()

    def _hash_pwd(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def save_users(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2)

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        username = username.strip().lower()
        pwd_hash = self._hash_pwd(password.strip())
        
        user = next((u for u in self.users if u['username'].lower() == username), None)
        if not user:
            return False, None, 'User does not exist'
            
        if user['password_hash'] != pwd_hash:
            return False, None, 'Incorrect password'
            
        if user.get('status') != 'active':
            return False, None, 'This user account is disabled by Admin'
            
        # Check expiry
        expiry_str = user.get('expiry_date', '2099-12-31')
        try:
            exp_date = datetime.strptime(expiry_str, '%Y-%m-%d')
            if datetime.now() > exp_date + timedelta(days=1):
                return False, None, f'Account expired on {expiry_str}. Contact Admin.'
        except Exception:
            pass

        return True, user, 'Login successful'

    def create_user(self, username: str, password: str, fullname: str = '', 
                    role: str = 'user', daily_limit: int = 2000, days_valid: int = 30) -> Tuple[bool, str]:
        username = username.strip().lower()
        if not username or not password:
            return False, 'Username and password are required'
            
        if any(u['username'].lower() == username for u in self.users):
            return False, 'Username already exists'

        expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d')
        new_user = {
            'username': username,
            'password_hash': self._hash_pwd(password.strip()),
            'role': role,
            'fullname': fullname.strip() or username.capitalize(),
            'daily_limit': int(daily_limit),
            'sent_today': 0,
            'total_sent': 0,
            'expiry_date': expiry_date,
            'status': 'active',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.users.append(new_user)
        self.save_users()
        return True, f'User {username} created successfully (Valid till {expiry_date})'

    def update_user(self, username: str, new_password: str = None, daily_limit: int = None, 
                    days_add: int = None, status: str = None) -> Tuple[bool, str]:
        user = next((u for u in self.users if u['username'].lower() == username.lower()), None)
        if not user:
            return False, 'User not found'
            
        if new_password:
            user['password_hash'] = self._hash_pwd(new_password.strip())
        if daily_limit is not None:
            user['daily_limit'] = int(daily_limit)
        if days_add is not None:
            try:
                curr_exp = datetime.strptime(user.get('expiry_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                if curr_exp < datetime.now():
                    curr_exp = datetime.now()
                user['expiry_date'] = (curr_exp + timedelta(days=days_add)).strftime('%Y-%m-%d')
            except Exception:
                user['expiry_date'] = (datetime.now() + timedelta(days=days_add)).strftime('%Y-%m-%d')
        if status is not None:
            user['status'] = status

        self.save_users()
        return True, f'User {username} updated successfully'

    def delete_user(self, username: str) -> Tuple[bool, str]:
        if username.lower() == 'admin':
            return False, 'Cannot delete Super Admin account'
            
        self.users = [u for u in self.users if u['username'].lower() != username.lower()]
        self.save_users()
        return True, f'User {username} removed'

    def get_all_users(self) -> List[Dict]:
        return list(self.users)
