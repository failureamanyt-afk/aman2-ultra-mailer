# AMAN2 - Anti-Detect Universal Cloud Mailer & Admin Suite 🚀

**AMAN2** is a complete, high-delivery email platform designed for **100% Inbox Delivery (Zero Dedicate / Anti-Detect)** with multi-user license access and Universal Link sharing.

---

## 🌐 1. Universal Web Link (Share with Friends)

You can run the web server on your machine or VPS, and **share the Universal Web Link directly with your friends**:

1. Double-click **`start_web_server.bat`** *(or run `python web_server.py`)*.
2. It will generate a link like:
   ```
   http://YOUR_IP:5000/login
   ```
3. Copy and send this link to your friends via WhatsApp, Telegram, or Discord!
4. Friends can open it directly in their **Chrome / Mobile / Laptop browser** without installing any software.

---

## 👥 2. Admin vs User System (Different Views)

* **Super Admin Login:**
  - **Username:** `admin`
  - **Password:** `admin123`
  - **Admin View:** Complete control to create client user accounts, set daily limits (e.g. 5,000 emails/day), set validity (e.g. 30 days), manage Gmail pools, and monitor stats.

* **Friend / Client Login:**
  - When your friend logs in with their credentials, a **completely separate Client Panel** opens up!
  - They only see their personal quota, Gmail App Password setup, Spintax tools, and campaign launcher.
  - They cannot see other users or access admin privileges.

---

## 🛡️ 3. Anti-Detect & 100% Inbox Delivery Protection

- **Spintax Engine:** `{Hi|Hello|Dear}` randomizes every email's text to prevent spam patterns.
- **Zero-Hash Noise Injection:** Invisible characters ensure every single email has a unique cryptographic hash.
- **Header Spoofing:** Randomizes `Message-ID`, `X-Mailer`, and client user agents.

---

## 🖥️ 4. Desktop GUI App

You also have the full **Desktop Application**:
- Double-click **`run.bat`** *(or `python main.py`)*.
