import os
import sys
import socket
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from core.auth_manager import AuthManager
from core.account_manager import AccountManager
from core.tag_engine import TagEngine
from core.content_generator import ContentGenerator
from core.mailer import GmailMailer
from core.anti_detect import AntiDetectEngine

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__)
app.secret_key = 'aman2_super_secret_anti_detect_key_2026'

auth_mgr = AuthManager()
account_mgr = AccountManager()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# ----------------- ENFORCED AUTHENTICATION ROUTES -----------------

@app.route('/')
def index():
    # Enforce login: If not authenticated, redirect to login page immediately!
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    # Render dashboard with user session
    return render_template('bm2_ultra.html', user=session)

@app.route('/download')
def download_page():
    return render_template('download.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        ok, user_data, msg = auth_mgr.authenticate(username, password)
        if ok:
            session['username'] = user_data['username']
            session['fullname'] = user_data.get('fullname', username)
            session['role'] = user_data.get('role', 'user')
            session['daily_limit'] = user_data.get('daily_limit', 1000)
            session['expiry_date'] = user_data.get('expiry_date', '')
            return redirect(url_for('index'))
        return render_template('login.html', error=msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ----------------- REST API ROUTES -----------------

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    if session.get('role') != 'admin':
        return jsonify([])
    return jsonify(auth_mgr.get_all_users())

@app.route('/api/admin/create_user', methods=['POST'])
def create_user():
    # Only admin can create users!
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Permission Denied! Only Super Admin can create client users.'}), 403
        
    data = request.json or {}
    ok, msg = auth_mgr.create_user(
        username=data.get('username', ''),
        password=data.get('password', ''),
        fullname=data.get('fullname', ''),
        daily_limit=int(data.get('daily_limit', 5000)),
        days_valid=int(data.get('days_valid', 30))
    )
    return jsonify({'success': ok, 'message': msg})

@app.route('/api/admin/delete_user', methods=['POST'])
def delete_user():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.json or {}
    ok, msg = auth_mgr.delete_user(data.get('username', ''))
    return jsonify({'success': ok, 'message': msg})

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify(account_mgr.get_all_accounts())

@app.route('/api/accounts/add', methods=['POST'])
def add_account():
    data = request.json or {}
    em = data.get('email', '').strip()
    pw = data.get('app_password', '').strip()
    sn = data.get('sender_name', 'Customer Support')
    
    test_acc = {'email': em, 'app_password': pw, 'smtp_host': 'smtp.gmail.com', 'smtp_port': 465, 'ssl': True}
    ok, msg = GmailMailer.test_connection(test_acc)
    if not ok:
        return jsonify({'success': False, 'message': f'SMTP Connection Failed: {msg}'})
        
    account_mgr.add_account(em, pw, sender_name=sn)
    return jsonify({'success': True, 'message': 'Gmail Account & App Password Verified & Saved Successfully!'})

@app.route('/api/accounts/delete', methods=['POST'])
def delete_account():
    data = request.json or {}
    account_mgr.remove_account(data.get('email', ''))
    return jsonify({'success': True, 'message': 'Account removed'})

@app.route('/api/test_smtp', methods=['POST'])
def test_smtp():
    data = request.json or {}
    em = data.get('email', '').strip()
    pw = data.get('app_password', '').strip()
    test_acc = {'email': em, 'app_password': pw, 'smtp_host': 'smtp.gmail.com', 'smtp_port': 465, 'ssl': True}
    ok, msg = GmailMailer.test_connection(test_acc)
    return jsonify({'success': ok, 'message': 'Connection & App Password Validated!' if ok else f'Error: {msg}'})

@app.route('/api/send', methods=['POST'])
def send_bulk_admin():
    data = request.json or {}
    recipients = data.get('recipients', [])
    subj_tpl = data.get('subject', 'Important Update')
    sender_name = data.get('sender_name', 'Support Team')
    body_tpl = data.get('body', '')

    accounts = account_mgr.get_all_accounts()
    if not accounts:
        return jsonify({'success': False, 'message': 'No Gmail accounts configured! Please add your Gmail & App Password in the "🔑 Gmail Accounts" menu.'})

    sent = 0
    failed = 0
    for idx, r in enumerate(recipients):
        acc = accounts[idx % len(accounts)]
        s_subj = TagEngine.process_tags(subj_tpl, recipient_email=r, enable_anti_detect=False)
        s_name = TagEngine.process_tags(sender_name, recipient_email=r, enable_anti_detect=False)
        s_body = TagEngine.process_tags(body_tpl, recipient_email=r, enable_anti_detect=True)

        msg = ContentGenerator.build_email_message(
            sender_email=acc['email'],
            sender_name=s_name,
            recipient_email=r,
            subject=s_subj,
            body_text=s_body,
            enable_anti_detect=True
        )

        ok, err = GmailMailer.send_email(acc, r, msg)
        if ok:
            sent += 1
            account_mgr.increment_sent(acc['email'])
        else:
            failed += 1

    return jsonify({'success': True, 'message': f'Completed! Delivered: {sent} emails, Failed: {failed}'})

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("=" * 60)
    print("AMAN2 ULTRA SECURE WEB SERVER RUNNING")
    print(f"Direct Link:           http://localhost:5000/login")
    print(f"Universal Link(Share): http://{local_ip}:5000/login")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
