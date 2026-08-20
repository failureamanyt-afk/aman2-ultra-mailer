import time
import threading
from typing import List, Dict, Callable, Optional
from core.tag_engine import TagEngine
from core.content_generator import ContentGenerator
from core.mailer import GmailMailer
from core.account_manager import AccountManager

class TaskWorker:
    def __init__(self, task_id: int, account_mgr: AccountManager, user_info: dict = None):
        self.task_id = task_id
        self.account_mgr = account_mgr
        self.user_info = user_info or {}
        self.thread: Optional[threading.Thread] = None
        
        self.is_active = False
        self.is_paused = False
        self.stop_requested = False
        
        self.recipients: List[str] = []
        self.config: Dict = {}
        self.sent_count = 0
        self.failed_count = 0
        self.total_count = 0
        self.errors: List[Dict] = []
        
        # Callbacks
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_status: Optional[Callable[[str, str], None]] = None
        self.on_account_switch: Optional[Callable[[str], None]] = None
        self.on_finished: Optional[Callable[[], None]] = None

    def start(self, recipients: List[str], config: Dict):
        if self.is_active:
            return
        
        self.recipients = [r.strip() for r in recipients if r.strip() and '@' in r]
        self.config = config
        self.total_count = len(self.recipients)
        self.sent_count = 0
        self.failed_count = 0
        self.errors = []
        self.is_active = True
        self.is_paused = False
        self.stop_requested = False
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.stop_requested = True
        self.is_paused = False
        self.is_active = False

    def _run(self):
        rotate_after = self.config.get('rotate_after', 5)
        delay_ms = self.config.get('delay_ms', 0)
        delay_mode = self.config.get('delay_mode', 'Each')
        tfn1 = self.config.get('tfn1', '')
        tfn2 = self.config.get('tfn2', '')
        tfn1_b64 = self.config.get('tfn1_base64', False)
        tfn2_b64 = self.config.get('tfn2_base64', False)
        universal_url = self.config.get('universal_url', '')
        anti_detect = self.config.get('enable_anti_detect', True)
        
        subject_tpl = self.config.get('subject', '')
        body_tpl = self.config.get('body', '')
        html_tpl = self.config.get('html_content', '')
        output_mode = self.config.get('output_mode', 'Raw pdf')
        page_format = self.config.get('page_format', 'A4')
        unsub_link = self.config.get('unsubscriber_link', False)
        country = self.config.get('country', 'USA')
        
        for idx, recipient in enumerate(self.recipients):
            if self.stop_requested:
                break
                
            while self.is_paused and not self.stop_requested:
                if self.on_status:
                    self.on_status('Paused', '#FFA500')
                time.sleep(0.5)
                
            if self.stop_requested:
                break

            account = self.account_mgr.get_account_for_send(rotate_after, self.sent_count)
            if not account:
                if self.on_status:
                    self.on_status('Error: No active sender account available!', '#FF3333')
                break
                
            if self.on_account_switch:
                self.on_account_switch(account.get('email', ''))

            if self.on_status:
                self.on_status(f'Sending to {recipient}...', '#33CC66')

            # Dynamic Tag + Spintax + Universal Link + Anti-Detect Processing
            sender_name = TagEngine.process_tags(
                self.config.get('sender_name', '') or account.get('sender_name', ''),
                recipient_email=recipient, tfn1=tfn1, tfn2=tfn2, tfn1_base64=tfn1_b64, tfn2_base64=tfn2_b64,
                universal_url=universal_url, enable_anti_detect=False
            )
            subj = TagEngine.process_tags(
                subject_tpl, recipient_email=recipient, tfn1=tfn1, tfn2=tfn2, tfn1_base64=tfn1_b64, tfn2_base64=tfn2_b64,
                universal_url=universal_url, enable_anti_detect=False
            )
            body = TagEngine.process_tags(
                body_tpl, recipient_email=recipient, tfn1=tfn1, tfn2=tfn2, tfn1_base64=tfn1_b64, tfn2_base64=tfn2_b64,
                universal_url=universal_url, enable_anti_detect=anti_detect
            )
            html = TagEngine.process_tags(
                html_tpl, recipient_email=recipient, tfn1=tfn1, tfn2=tfn2, tfn1_base64=tfn1_b64, tfn2_base64=tfn2_b64,
                universal_url=universal_url, enable_anti_detect=anti_detect
            )

            msg = ContentGenerator.build_email_message(
                sender_email=account.get('email', ''),
                sender_name=sender_name,
                recipient_email=recipient,
                subject=subj,
                body_text=body,
                html_content=html,
                output_mode=output_mode,
                page_format=page_format,
                unsubscribe_link=unsub_link,
                country=country,
                enable_anti_detect=anti_detect
            )

            success, err_msg = GmailMailer.send_email(account, recipient, msg)
            
            if success:
                self.sent_count += 1
                self.account_mgr.increment_sent(account.get('email', ''))
            else:
                self.failed_count += 1
                self.errors.append({
                    'recipient': recipient,
                    'account': account.get('email', ''),
                    'error': err_msg,
                    'time': time.strftime('%H:%M:%S')
                })

            if self.on_progress:
                self.on_progress(self.sent_count, self.total_count, recipient)

            if delay_ms > 0:
                if delay_mode == 'Each':
                    time.sleep(delay_ms / 1000.0)
                elif delay_mode == 'Every 50' and (idx + 1) % 50 == 0:
                    time.sleep(delay_ms / 1000.0)

        self.is_active = False
        if self.on_status:
            if self.stop_requested:
                self.on_status('Stopped by user', '#FF9900')
            else:
                self.on_status('Completed!', '#00FF00')
                
        if self.on_finished:
            self.on_finished()
