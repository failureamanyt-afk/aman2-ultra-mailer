import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import webbrowser

from core.tag_engine import TagEngine
from core.content_generator import ContentGenerator
from core.mailer import GmailMailer
from core.account_manager import AccountManager
from core.auth_manager import AuthManager
from core.task_worker import TaskWorker

# Exact Color Palette
COLOR_HEADER_BG = '#1e293b'
COLOR_MAIN_BG = '#c8d0d8'
COLOR_DARK_PANEL = '#0d131a'
COLOR_LIME_GREEN = '#28d150'
COLOR_DARK_GREEN = '#006622'
COLOR_TASK_BG = '#e8ecf0'
COLOR_RED_BTN = '#c02222'
COLOR_ORANGE_BORDER = '#f59e0b'
COLOR_TEXT_DARK = '#000000'
COLOR_TEXT_WHITE = '#ffffff'
COLOR_TEXT_BLUE = '#1d4ed8'

class AMAN2ExactApp:
    def __init__(self, root):
        self.root = root
        self.root.title('AMAN2 Ultra - 3273')
        self.root.geometry('1180x820')
        self.root.minsize(1100, 780)
        self.root.configure(bg=COLOR_MAIN_BG)

        self.account_mgr = AccountManager()
        self.auth_mgr = AuthManager()
        self.current_task = 1
        self.active_worker = None

        # Variables
        self.var_country = tk.StringVar(value='USA')
        self.var_with_name = tk.BooleanVar(value=True)
        self.var_mode = tk.StringVar(value='Mode 1')
        self.var_grayscale = tk.BooleanVar(value=False)
        self.var_crop = tk.BooleanVar(value=True)
        self.var_quality = tk.BooleanVar(value=False)
        self.var_highsize = tk.BooleanVar(value=True)
        self.var_limit_chk = tk.BooleanVar(value=True)
        
        self.var_change_after = tk.BooleanVar(value=True)
        self.var_change_count = tk.IntVar(value=5)
        self.var_name = tk.StringVar(value='Teamonline Team')
        self.var_sender_email = tk.StringVar(value='claudiyaikahelsyaharani83@gmail.com')
        self.var_subject = tk.StringVar(value='Thanks For Your Order #RANDOM#')
        
        self.var_tfn1 = tk.StringVar(value='+1 859 704-1290')
        self.var_tfn2 = tk.StringVar(value='+1 859 704-1290')
        self.var_tfn1_b64 = tk.BooleanVar(value=False)
        self.var_tfn2_b64 = tk.BooleanVar(value=False)
        self.var_sw_format = tk.BooleanVar(value=False)
        
        self.var_html_body = tk.BooleanVar(value=True)
        self.var_auto_style = tk.BooleanVar(value=False)
        self.var_import_body = tk.BooleanVar(value=False)
        self.var_auto_body = tk.BooleanVar(value=False)
        self.var_modify_html = tk.BooleanVar(value=True)
        
        self.var_delay_ms = tk.IntVar(value=0)
        self.var_delay_mode = tk.StringVar(value='Each')
        self.var_content_type = tk.StringVar(value='Auto')
        self.var_img_format = tk.StringVar(value='heic')
        self.var_page_format = tk.StringVar(value='A4')
        self.var_out_mode = tk.StringVar(value='Raw pdf')
        
        self.var_html_w = tk.IntVar(value=0)
        self.var_html_h = tk.IntVar(value=0)
        self.var_rand_w = tk.BooleanVar(value=False)
        self.var_test_mail = tk.BooleanVar(value=False)

        self.var_specif_type = tk.StringVar(value='ALL')
        self.var_specif_num = tk.IntVar(value=350)
        
        self.var_live_status = tk.StringVar(value='Ready To Send')
        self.var_total_sent_str = tk.StringVar(value='Total Sent 431 of 454')
        self.var_last_api = tk.StringVar(value='rayyaoktavianikaylazia96@gmail.com')

        self.tasks_data = {
            1: {'sent': 431, 'total': 454},
            2: {'sent': 414, 'total': 450},
            3: {'sent': 188, 'total': 400},
            4: {'sent': 203, 'total': 350},
            5: {'sent': 420, 'total': 500}
        }

        self._build_exact_ui()
        self._load_accounts_init()

    def _build_exact_ui(self):
        # 1. TOP HEADER BAR
        header_bar = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=34)
        header_bar.pack(fill=tk.X, side=tk.TOP)

        lbl_icon = tk.Label(header_bar, text=' ✉ ', bg='#00E5FF', fg='#000000', font=('Arial', 10, 'bold'))
        lbl_icon.pack(side=tk.LEFT, padx=(6, 4), pady=4)

        lbl_title = tk.Label(header_bar, text='AMAN2 Ultra', bg=COLOR_HEADER_BG, fg='#00E5FF', font=('Segoe UI', 11, 'bold'))
        lbl_title.pack(side=tk.LEFT, padx=4)

        lbl_num = tk.Label(header_bar, text='3273', bg=COLOR_HEADER_BG, fg='#cbd5e1', font=('Segoe UI', 9))
        lbl_num.pack(side=tk.LEFT, padx=30)

        lbl_welcome = tk.Label(header_bar, text='Welcome To BMD161', bg=COLOR_HEADER_BG, fg='#ffffff', font=('Segoe UI', 10, 'bold'))
        lbl_welcome.pack(side=tk.RIGHT, padx=40)

        lbl_menu = tk.Label(header_bar, text='Menu', bg=COLOR_HEADER_BG, fg=COLOR_LIME_GREEN, font=('Segoe UI', 10, 'bold'), cursor='hand2')
        lbl_menu.pack(side=tk.RIGHT, padx=10)
        lbl_menu.bind('<Button-1>', lambda e: self.show_admin_or_accounts())

        # 2. TASK TABS BAR
        task_row = tk.Frame(self.root, bg=COLOR_MAIN_BG, height=44)
        task_row.pack(fill=tk.X, side=tk.TOP, padx=4, pady=3)

        btn_add_task = tk.Button(task_row, text='+ Add User / Task', bg='#f1f5f9', fg='#000000', font=('Segoe UI', 9, 'bold'),
                                 relief=tk.RAISED, bd=2, padx=12, pady=4, command=self.show_admin_or_accounts)
        btn_add_task.pack(side=tk.LEFT, padx=3)

        self.task_btns = {}
        for t_id in [5, 4, 3, 2, 1]:
            tf = tk.Frame(task_row, bg='#e2e8f0', bd=1, relief=tk.SOLID, padx=1, pady=1)
            tf.pack(side=tk.LEFT, padx=2)
            
            lbl_tname = tk.Label(tf, text=f'➜ Task {t_id}', bg='#ffffff', fg='#000000', font=('Segoe UI', 8, 'bold'), width=11)
            lbl_tname.pack(fill=tk.X)
            
            sent_bg = COLOR_LIME_GREEN if t_id == 1 else '#22c55e'
            lbl_tsent = tk.Label(tf, text=f'Sent-{self.tasks_data[t_id]["sent"]}', bg=sent_bg, fg='#000000', font=('Segoe UI', 8, 'bold'), width=11)
            lbl_tsent.pack(fill=tk.X)
            
            tf.bind('<Button-1>', lambda e, tid=t_id: self._select_task(tid))
            lbl_tname.bind('<Button-1>', lambda e, tid=t_id: self._select_task(tid))
            lbl_tsent.bind('<Button-1>', lambda e, tid=t_id: self._select_task(tid))
            self.task_btns[t_id] = (lbl_tname, lbl_tsent, tf)

        # Date & All Tag
        btn_all_tag = tk.Button(task_row, text='ALL TAG', bg='#16a34a', fg='#ffffff', font=('Segoe UI', 9, 'bold'),
                                relief=tk.RAISED, bd=2, padx=14, pady=4, cursor='hand2', command=self.show_tags_modal)
        btn_all_tag.pack(side=tk.RIGHT, padx=4)

        date_box = tk.Frame(task_row, bg=COLOR_MAIN_BG)
        date_box.pack(side=tk.RIGHT, padx=10)
        tk.Label(date_box, text='Date Setting', bg=COLOR_MAIN_BG, fg='#000000', font=('Segoe UI', 8, 'bold')).pack(anchor='e')
        
        date_field = tk.Frame(date_box, bg='#ffffff', bd=1, relief=tk.SOLID)
        date_field.pack()
        self.lbl_cur_date = tk.Label(date_field, text=datetime.now().strftime('%d/%m/%Y'), bg='#ffffff', fg='#000000', font=('Segoe UI', 8), width=10)
        self.lbl_cur_date.pack(side=tk.LEFT, padx=2)
        tk.Label(date_field, text='📅', bg='#e2e8f0', fg='#000000', font=('Segoe UI', 8)).pack(side=tk.RIGHT)

        # 3. MAIN WORKSPACE CONTAINER
        workspace = tk.Frame(self.root, bg=COLOR_MAIN_BG)
        workspace.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # LEFT COLUMN (Recipients)
        self._build_left_recipient_panel(workspace)

        # CENTER COLUMN (Configs, Sender, HTML, Buttons)
        self._build_center_panel(workspace)

        # RIGHT WATERMARK
        lbl_watermark = tk.Label(workspace, text='A\nM\nA\nN\n2\n\nU\nl\nt\nr\na', bg=COLOR_MAIN_BG, fg='#88929e', font=('Impact', 20, 'bold'), justify=tk.CENTER)
        lbl_watermark.pack(side=tk.RIGHT, fill=tk.Y, padx=4)

        # 4. BOTTOM FOOTER BAR
        self._build_bottom_footer()

    def _build_left_recipient_panel(self, parent):
        left_box = tk.Frame(parent, bg='#e2e8f0', bd=2, relief=tk.SOLID, width=250)
        left_box.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=1)

        # Top Button row
        top_btn_row = tk.Frame(left_box, bg='#e2e8f0')
        top_btn_row.pack(fill=tk.X, padx=4, pady=3)

        btn_paste = tk.Button(top_btn_row, text='Paste', bg='#f8fafc', fg='#000000', font=('Segoe UI', 9, 'bold'),
                              relief=tk.RAISED, bd=2, padx=12, command=self._paste_emails)
        btn_paste.pack(side=tk.LEFT)

        btn_trash = tk.Button(top_btn_row, text='🗑', bg='#3b82f6', fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                              relief=tk.RAISED, bd=1, padx=6, command=self._clear_emails)
        btn_trash.pack(side=tk.RIGHT)

        # Recipients Listbox / Text Area with checked marks
        text_container = tk.Frame(left_box, bg='#ffffff', bd=1, relief=tk.SOLID)
        text_container.pack(fill=tk.BOTH, expand=True, padx=3, pady=2)

        self.emails_text = tk.Text(text_container, width=28, height=25, bg='#ffffff', fg='#000000',
                                   font=('Consolas', 9), wrap=tk.NONE, bd=0)
        scroll = tk.Scrollbar(text_container, command=self.emails_text.yview)
        self.emails_text.configure(yscrollcommand=scroll.set)
        
        self.emails_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        sample_emails = [
            "aximuthial@yahoo.com",
            "kkjerook@suddenlink.net",
            "marciakitchin@yahoo.com",
            "wazthis68@aol.com",
            "bemiek62@cox.net",
            "bettlelady1@yahoo.com",
            "rhorine@woh.rr.com",
            "rosaphampton@yahoo.com",
            "tdkendrick3@yahoo.com",
            "ahirsch786@aol.com",
            "mitziazevedo@charter.net",
            "rbroome99@yahoo.com",
            "mcf227@yahoo.com",
            "allenlloyd@nc.rr.com",
            "sheribabee12@aol.com",
            "jab4lfz@verizon.net",
            "cindylou22312@yahoo.com",
            "tony.maldonado31@yahoo.com",
            "joeu3118@aol.com"
        ]
        self.emails_text.insert('1.0', '\n'.join(sample_emails))
        self.emails_text.bind('<KeyRelease>', lambda e: self._update_count_ui())

        # Bottom Controls
        bottom_box = tk.Frame(left_box, bg='#e2e8f0')
        bottom_box.pack(fill=tk.X, padx=3, pady=3)

        btn_import = tk.Button(bottom_box, text='Import Data', bg='#2563eb', fg='#ffffff', font=('Segoe UI', 8, 'bold'),
                               relief=tk.RAISED, bd=2, padx=6, pady=2, command=self._import_file)
        btn_import.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        self.lbl_success = tk.Label(bottom_box, text='Successed', bg='#16a34a', fg='#ffffff', font=('Segoe UI', 8, 'bold'), padx=6, pady=2)
        self.lbl_success.pack(side=tk.RIGHT, padx=1)

        # Specif Row
        specif_row = tk.Frame(left_box, bg='#e2e8f0')
        specif_row.pack(fill=tk.X, padx=3, pady=2)

        tk.Label(specif_row, text='Specif :', bg='#e2e8f0', fg='#000000', font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT)
        cmb_sp = ttk.Combobox(specif_row, textvariable=self.var_specif_type, values=['ALL', 'FIRST', 'RANGE'], width=5)
        cmb_sp.pack(side=tk.LEFT, padx=1)

        spn_sp = tk.Spinbox(specif_row, from_=1, to=10000, textvariable=self.var_specif_num, width=4)
        spn_sp.pack(side=tk.LEFT, padx=1)

        btn_get = tk.Button(specif_row, text='Get', bg='#e2e8f0', fg='#000000', font=('Segoe UI', 8), relief=tk.RAISED, bd=1,
                            command=self._slice_emails)
        btn_get.pack(side=tk.LEFT, padx=2)

    def _build_center_panel(self, parent):
        center = tk.Frame(parent, bg=COLOR_MAIN_BG)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3, pady=1)

        # ROW 1: Black Top Config Bar
        top_black = tk.Frame(center, bg=COLOR_DARK_PANEL, bd=1, relief=tk.SOLID)
        top_black.pack(fill=tk.X, pady=1)

        c_box = tk.Frame(top_black, bg=COLOR_DARK_PANEL, bd=1, relief=tk.SOLID)
        c_box.pack(side=tk.LEFT, padx=2, pady=2)
        for c in ['USA', 'AUS', 'UK']:
            tk.Radiobutton(c_box, text=c, value=c, variable=self.var_country, bg=COLOR_DARK_PANEL, fg='#ffffff',
                           selectcolor='#000000', activebackground=COLOR_DARK_PANEL, font=('Segoe UI', 7, 'bold')).pack(anchor='w')

        unsub_box = tk.Frame(top_black, bg=COLOR_DARK_PANEL)
        unsub_box.pack(side=tk.LEFT, padx=3)
        lbl_unsub = tk.Label(unsub_box, text='Unsubscriber Link', bg='#1e3a8a', fg='#60a5fa', font=('Segoe UI', 7, 'bold'), padx=3, pady=1)
        lbl_unsub.pack(anchor='w', pady=1)
        tk.Checkbutton(unsub_box, text='With Name', variable=self.var_with_name, bg=COLOR_DARK_PANEL, fg='#ffffff',
                       selectcolor='#000000', font=('Segoe UI', 7)).pack(anchor='w')

        m_box = tk.Frame(top_black, bg=COLOR_DARK_PANEL)
        m_box.pack(side=tk.LEFT, padx=4)
        for m in ['Mode 1', 'Mode 2', 'Mode 3']:
            tk.Radiobutton(m_box, text=m, value=m, variable=self.var_mode, bg=COLOR_DARK_PANEL, fg='#ffffff',
                           selectcolor='#000000', activebackground=COLOR_DARK_PANEL, font=('Segoe UI', 7)).pack(anchor='w')

        chk_box = tk.Frame(top_black, bg=COLOR_DARK_PANEL)
        chk_box.pack(side=tk.LEFT, padx=4)
        r1 = tk.Frame(chk_box, bg=COLOR_DARK_PANEL)
        r1.pack(anchor='w')
        tk.Checkbutton(r1, text='GrayScale', variable=self.var_grayscale, bg=COLOR_DARK_PANEL, fg='#ffffff', selectcolor='#000000', font=('Segoe UI', 7)).pack(side=tk.LEFT)
        tk.Checkbutton(r1, text='Crop Image', variable=self.var_crop, bg=COLOR_DARK_PANEL, fg='#ffffff', selectcolor='#000000', font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=2)

        r2 = tk.Frame(chk_box, bg=COLOR_DARK_PANEL)
        r2.pack(anchor='w')
        tk.Checkbutton(r2, text='High Quality', variable=self.var_quality, bg=COLOR_DARK_PANEL, fg='#6b7280', selectcolor='#000000', font=('Segoe UI', 7)).pack(side=tk.LEFT)
        tk.Checkbutton(r2, text='High Size', variable=self.var_highsize, bg=COLOR_DARK_PANEL, fg='#ffffff', selectcolor='#000000', font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=2)

        err_box = tk.Frame(top_black, bg=COLOR_DARK_PANEL)
        err_box.pack(side=tk.LEFT, padx=4)
        lbl_err = tk.Label(err_box, text='Error List', fg='#ef4444', bg=COLOR_DARK_PANEL, font=('Segoe UI', 8, 'bold', 'underline'), cursor='hand2')
        lbl_err.pack(anchor='w')
        lbl_err.bind('<Button-1>', lambda e: self.show_error_list())

        tk.Checkbutton(err_box, text='ReachedLimit Check', variable=self.var_limit_chk, bg=COLOR_DARK_PANEL, fg='#ef4444',
                       selectcolor='#000000', font=('Segoe UI', 7, 'bold')).pack(anchor='w')

        btn_pause = tk.Button(top_black, text='Pause', bg=COLOR_RED_BTN, fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                              relief=tk.RAISED, bd=2, padx=12, pady=4, command=self._toggle_pause)
        btn_pause.pack(side=tk.RIGHT, padx=6, pady=4)

        # ROW 2: Sender Config + TFN Box
        mid_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        mid_row.pack(fill=tk.X, pady=2)

        sender_col = tk.Frame(mid_row, bg=COLOR_MAIN_BG)
        sender_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        c1 = tk.Frame(sender_col, bg=COLOR_MAIN_BG)
        c1.pack(fill=tk.X, pady=1)
        tk.Button(c1, text='Clear cache', bg='#e2e8f0', font=('Segoe UI', 8, 'bold'), relief=tk.RAISED, bd=1, command=self._clear_cache).pack(side=tk.LEFT)
        tk.Checkbutton(c1, text='Change After Sent', variable=self.var_change_after, bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=4)
        tk.Spinbox(c1, from_=1, to=1000, textvariable=self.var_change_count, width=3).pack(side=tk.LEFT)

        c2 = tk.Frame(sender_col, bg=COLOR_MAIN_BG)
        c2.pack(fill=tk.X, pady=1)
        tk.Label(c2, text='Name *', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold'), width=9, anchor='w').pack(side=tk.LEFT)
        tk.Label(c2, text='Settings', bg='#dbeafe', fg='#1d4ed8', font=('Segoe UI', 7, 'underline'), bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=2)
        tk.Entry(c2, textvariable=self.var_name, font=('Segoe UI', 8), bg='#ffffff', bd=1, relief=tk.SOLID, width=24).pack(side=tk.LEFT, padx=2)
        tk.Button(c2, text='Pick', bg='#e2e8f0', font=('Segoe UI', 7), relief=tk.RAISED, bd=1).pack(side=tk.LEFT, padx=1)
        tk.Checkbutton(c2, text='Import', bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=1)

        c3 = tk.Frame(sender_col, bg=COLOR_MAIN_BG)
        c3.pack(fill=tk.X, pady=1)
        tk.Label(c3, text='Sender Mail', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold'), width=9, anchor='w').pack(side=tk.LEFT)
        tk.Entry(c3, textvariable=self.var_sender_email, font=('Consolas', 8), bg='#ffffff', bd=1, relief=tk.SOLID, width=30).pack(side=tk.LEFT, padx=2)
        tk.Label(c3, text='Gmass', fg='#1d4ed8', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'underline'), cursor='hand2').pack(side=tk.LEFT, padx=2)

        c4 = tk.Frame(sender_col, bg=COLOR_MAIN_BG)
        c4.pack(fill=tk.X, pady=1)
        tk.Label(c4, text='Subject', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold'), width=9, anchor='w').pack(side=tk.LEFT)
        tk.Button(c4, text='Pick', bg='#e2e8f0', font=('Segoe UI', 7), relief=tk.RAISED, bd=1).pack(side=tk.LEFT, padx=1)
        tk.Entry(c4, textvariable=self.var_subject, font=('Segoe UI', 8), bg='#ffffff', bd=1, relief=tk.SOLID, width=28).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(c4, text='Import', bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=1)

        tk.Button(sender_col, text='Check Bounce', bg=COLOR_RED_BTN, fg='#ffffff', font=('Segoe UI', 8, 'bold'),
                  relief=tk.RAISED, bd=1, padx=8, pady=2, command=lambda: messagebox.showinfo('Check Bounce', 'Bounce detection active!')).pack(anchor='w', pady=2)

        # Right: Orange Bordered TFN Box
        tfn_box = tk.Frame(mid_row, bg=COLOR_MAIN_BG, bd=2, relief=tk.SOLID, highlightbackground=COLOR_ORANGE_BORDER, highlightthickness=1)
        tfn_box.pack(side=tk.RIGHT, padx=4, pady=1)

        t1_row = tk.Frame(tfn_box, bg=COLOR_MAIN_BG)
        t1_row.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(t1_row, text='TFN 1 (#TFN#)', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'bold')).pack(side=tk.LEFT)
        tk.Label(t1_row, text='Base64', fg='#15803d', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(t1_row, variable=self.var_tfn1_b64, bg=COLOR_MAIN_BG).pack(side=tk.LEFT)
        tk.Entry(t1_row, textvariable=self.var_tfn1, font=('Consolas', 8, 'bold'), width=16, justify=tk.CENTER, bg='#ffffff', bd=1).pack(side=tk.RIGHT)

        t2_row = tk.Frame(tfn_box, bg=COLOR_MAIN_BG)
        t2_row.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(t2_row, text='TFN 2 (#TFNA#)', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'bold')).pack(side=tk.LEFT)
        tk.Label(t2_row, text='Base64', fg='#15803d', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(t2_row, variable=self.var_tfn2_b64, bg=COLOR_MAIN_BG).pack(side=tk.LEFT)
        tk.Entry(t2_row, textvariable=self.var_tfn2, font=('Consolas', 8, 'bold'), width=16, justify=tk.CENTER, bg='#ffffff', bd=1).pack(side=tk.RIGHT)

        t3_row = tk.Frame(tfn_box, bg=COLOR_MAIN_BG)
        t3_row.pack(fill=tk.X, padx=4, pady=1)
        tk.Checkbutton(t3_row, text='Software Format?', variable=self.var_sw_format, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT)
        tk.Label(t3_row, text='Settings', fg='#1d4ed8', bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'underline')).pack(side=tk.RIGHT, padx=4)

        # ROW 3: Body Editor
        body_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        body_row.pack(fill=tk.X, pady=1)

        b_opts = tk.Frame(body_row, bg=COLOR_MAIN_BG)
        b_opts.pack(side=tk.LEFT, anchor='n', padx=2)
        tk.Label(b_opts, text='Body', bg=COLOR_MAIN_BG, font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        tk.Checkbutton(b_opts, text='Html Body ?', variable=self.var_html_body, bg=COLOR_MAIN_BG, font=('Segoe UI', 7, 'bold')).pack(anchor='w')
        tk.Checkbutton(b_opts, text='Auto Body Style', variable=self.var_auto_style, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(anchor='w')
        tk.Checkbutton(b_opts, text='Import', variable=self.var_import_body, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(anchor='w')
        tk.Checkbutton(b_opts, text='Auto Body', variable=self.var_auto_body, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(anchor='w')
        tk.Button(b_opts, text='Pick', bg='#e2e8f0', font=('Segoe UI', 7), relief=tk.RAISED, bd=1).pack(anchor='e', pady=1)

        body_text_frame = tk.Frame(body_row, bg='#ffffff', bd=1, relief=tk.SOLID)
        body_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.txt_body = tk.Text(body_text_frame, height=4, font=('Consolas', 9), bd=0)
        self.txt_body.pack(fill=tk.BOTH, expand=True)
        self.txt_body.insert('1.0', '#RANDOM#\nDear #NAME#,\nThank you for choosing our service on #DATE#.\nOrder ID: #ORDER_ID#\nHelpline: #TFN#')

        # ROW 4: Modify HTML & Delay & Page Format
        mod_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        mod_row.pack(fill=tk.X, pady=1)

        lbl_mod = tk.Label(mod_row, text='■ Modify Html', bg='#d97706', fg='#ffffff', font=('Segoe UI', 8, 'bold'), padx=4, pady=1)
        lbl_mod.pack(side=tk.LEFT, padx=2)

        tk.Label(mod_row, text='Delay (M.Sec)', bg=COLOR_MAIN_BG, font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=2)
        tk.Spinbox(mod_row, from_=0, to=60000, textvariable=self.var_delay_ms, width=4).pack(side=tk.LEFT)

        tk.Radiobutton(mod_row, text='Each', value='Each', variable=self.var_delay_mode, bg=COLOR_MAIN_BG, font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(mod_row, text='Every 50', value='Every 50', variable=self.var_delay_mode, bg=COLOR_MAIN_BG, font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=2)

        page_box = tk.Frame(mod_row, bg=COLOR_MAIN_BG)
        page_box.pack(side=tk.RIGHT, padx=4)
        tk.Label(page_box, text='Page Format', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=2)
        cmb_pf = ttk.Combobox(page_box, textvariable=self.var_page_format, values=['A4', 'Letter'], width=8)
        cmb_pf.pack(side=tk.RIGHT)

        # ROW 5: Content (html) & Editor Section
        content_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        content_row.pack(fill=tk.BOTH, expand=True, pady=1)

        out_col = tk.Frame(content_row, bg=COLOR_MAIN_BG)
        out_col.pack(side=tk.LEFT, anchor='n', padx=2)
        tk.Label(out_col, text='Content (html)', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        for mode in ['To pdf', 'To image', 'Inline image', 'Raw pdf', 'Inline Html', 'Docx', 'PPTX']:
            tk.Radiobutton(out_col, text=mode, value=mode, variable=self.var_out_mode, bg=COLOR_MAIN_BG, font=('Segoe UI', 8), anchor='w').pack(fill=tk.X)

        html_col = tk.Frame(content_row, bg=COLOR_MAIN_BG)
        html_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

        top_fmt_bar = tk.Frame(html_col, bg=COLOR_MAIN_BG)
        top_fmt_bar.pack(fill=tk.X, pady=1)
        tk.Label(top_fmt_bar, text='ContentType', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT)
        ttk.Combobox(top_fmt_bar, textvariable=self.var_content_type, values=['Auto', 'HTML', 'Text'], width=8).pack(side=tk.LEFT, padx=2)

        tk.Label(top_fmt_bar, text='Img Forma', bg=COLOR_MAIN_BG, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=6)
        ttk.Combobox(top_fmt_bar, textvariable=self.var_img_format, values=['heic', 'png', 'jpg'], width=8).pack(side=tk.LEFT, padx=2)

        html_editor_frame = tk.Frame(html_col, bg='#ffffff', bd=1, relief=tk.SOLID)
        html_editor_frame.pack(fill=tk.BOTH, expand=True, pady=1)
        self.txt_html = tk.Text(html_editor_frame, font=('Consolas', 9), bd=0, height=8)
        self.txt_html.pack(fill=tk.BOTH, expand=True)

        sample_html_code = """</tr>
</tbody>
</table>
</div>
</body>
</html>"""
        self.txt_html.insert('1.0', sample_html_code)

        html_btn_row = tk.Frame(html_col, bg=COLOR_MAIN_BG)
        html_btn_row.pack(fill=tk.X, pady=1)

        btn_prev = tk.Button(html_btn_row, text='Preview HTML', bg=COLOR_LIME_GREEN, fg='#000000', font=('Segoe UI', 8, 'bold'),
                             relief=tk.RAISED, bd=2, padx=8, command=self._preview_html)
        btn_prev.pack(side=tk.LEFT)

        tk.Label(html_btn_row, text='Html. W', bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=2)
        tk.Spinbox(html_btn_row, from_=0, to=2000, textvariable=self.var_html_w, width=3).pack(side=tk.LEFT)
        tk.Label(html_btn_row, text='H :', bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=2)
        tk.Spinbox(html_btn_row, from_=0, to=2000, textvariable=self.var_html_h, width=3).pack(side=tk.LEFT)

        tk.Checkbutton(html_btn_row, text='Random Width', variable=self.var_rand_w, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(html_btn_row, text='Test Mail ?', variable=self.var_test_mail, bg=COLOR_MAIN_BG, font=('Segoe UI', 7)).pack(side=tk.RIGHT, padx=4)

        # ROW 6: Status Line, Stop, Sending, Total Sent
        action_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        action_row.pack(fill=tk.X, pady=2)

        btn_add_test = tk.Button(action_row, text='Add Test Mail', bg='#e2e8f0', fg='#000000', font=('Segoe UI', 8, 'bold'),
                                 relief=tk.RAISED, bd=2, padx=8, pady=2, command=self._open_test_mail_dialog)
        btn_add_test.pack(side=tk.LEFT, padx=2)

        lbl_sending_to = tk.Label(action_row, text='Sending to kneeley9451@charter.net', bg=COLOR_MAIN_BG, fg='#15803d', font=('Segoe UI', 9, 'bold'))
        lbl_sending_to.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(action_row, text='Stop', bg=COLOR_RED_BTN, fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, width=8, height=1, command=self._stop_task)
        self.btn_stop.pack(side=tk.RIGHT, padx=2)

        self.btn_send = tk.Button(action_row, text='Sending...', bg='#15803d', fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, width=10, height=1, command=self._start_task)
        self.btn_send.pack(side=tk.RIGHT, padx=2)

        # ROW 7: Ready to send & Total Sent Black Bar
        bar_row = tk.Frame(center, bg=COLOR_MAIN_BG)
        bar_row.pack(fill=tk.X, pady=2)

        self.lbl_ready = tk.Label(bar_row, textvariable=self.var_live_status, fg='#15803d', bg=COLOR_MAIN_BG, font=('Segoe UI', 10, 'bold'))
        self.lbl_ready.pack(side=tk.LEFT, padx=4)

        lbl_black_counter = tk.Label(bar_row, textvariable=self.var_total_sent_str, bg='#1e293b', fg='#ffffff',
                                     font=('Segoe UI', 11, 'bold'), padx=20, pady=3)
        lbl_black_counter.pack(side=tk.RIGHT)

    def _build_bottom_footer(self):
        footer = tk.Frame(self.root, bg='#0f172a', height=24)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_api = tk.Label(footer, text='Last Used API : rayyaoktavianikaylazia96@gmail.com', fg='#facc15', bg='#0f172a', font=('Segoe UI', 8))
        lbl_api.pack(side=tk.LEFT, padx=8)

        lbl_ver = tk.Label(footer, text='Version : AMAN2-v12.0', fg='#ffffff', bg='#0f172a', font=('Segoe UI', 8))
        lbl_ver.pack(side=tk.RIGHT, padx=8)

    # ---------------- UI ACTIONS ----------------
    def _select_task(self, task_id):
        self.current_task = task_id
        for tid, (lname, lsent, frame) in self.task_btns.items():
            if tid == task_id:
                lsent.config(bg=COLOR_LIME_GREEN)
            else:
                lsent.config(bg='#22c55e')

    def _paste_emails(self):
        try:
            txt = self.root.clipboard_get()
            self.emails_text.insert(tk.END, '\n' + txt)
            self._update_count_ui()
        except Exception:
            pass

    def _clear_emails(self):
        self.emails_text.delete('1.0', tk.END)
        self._update_count_ui()

    def _import_file(self):
        f = filedialog.askopenfilename(filetypes=[('Text/CSV Files', '*.txt;*.csv'), ('All Files', '*.*')])
        if f:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                lines = [l.strip() for l in content.splitlines() if '@' in l]
                self.emails_text.delete('1.0', tk.END)
                self.emails_text.insert('1.0', '\n'.join(lines))
            self.lbl_success.config(text=f'Imported {len(lines)}', bg='#16a34a')
            self._update_count_ui()
            messagebox.showinfo('Import Success', f'Successfully imported {len(lines)} email addresses!')

    def _slice_emails(self):
        raw = self.emails_text.get('1.0', tk.END).strip().splitlines()
        emails = [e.strip() for e in raw if e.strip()]
        lim = self.var_specif_num.get()
        self.emails_text.delete('1.0', tk.END)
        self.emails_text.insert('1.0', '\n'.join(emails[:lim]))
        self._update_count_ui()

    def _update_count_ui(self):
        raw = self.emails_text.get('1.0', tk.END).strip().splitlines()
        valid = [e.strip() for e in raw if '@' in e]
        self.var_total_sent_str.set(f"Total Sent 0 of {len(valid)}")

    def _clear_cache(self):
        messagebox.showinfo('Clear Cache', 'Cache and SMTP buffers cleared.')

    def _toggle_pause(self):
        if self.active_worker and self.active_worker.is_active:
            if self.active_worker.is_paused:
                self.active_worker.resume()
                self.var_live_status.set('Sending in progress...')
            else:
                self.active_worker.pause()
                self.var_live_status.set('Paused')

    def _stop_task(self):
        if self.active_worker:
            self.active_worker.stop()
            self.var_live_status.set('Stopped')

    def _start_task(self):
        accs = self.account_mgr.get_all_accounts()
        if not accs:
            self.show_admin_or_accounts()
            return

        raw = self.emails_text.get('1.0', tk.END).strip().splitlines()
        recipients = [e.strip() for e in raw if '@' in e]
        if not recipients:
            messagebox.showwarning('Empty List', 'Please import or paste recipient email addresses.')
            return

        cfg = {
            'rotate_after': self.var_change_count.get() if self.var_change_after.get() else 0,
            'delay_ms': self.var_delay_ms.get(),
            'delay_mode': self.var_delay_mode.get(),
            'sender_name': self.var_name.get(),
            'subject': self.var_subject.get(),
            'body': self.txt_body.get('1.0', tk.END).strip(),
            'html_content': self.txt_html.get('1.0', tk.END).strip(),
            'output_mode': self.var_out_mode.get(),
            'page_format': self.var_page_format.get(),
            'tfn1': self.var_tfn1.get(),
            'tfn2': self.var_tfn2.get(),
            'tfn1_base64': self.var_tfn1_b64.get(),
            'tfn2_base64': self.var_tfn2_b64.get(),
            'country': self.var_country.get()
        }

        self.active_worker = TaskWorker(self.current_task, self.account_mgr)
        self.active_worker.on_progress = self._on_prog
        self.active_worker.on_status = lambda msg, col: self.var_live_status.set(msg)
        self.active_worker.on_account_switch = lambda em: self.var_sender_email.set(em)
        self.active_worker.start(recipients, cfg)
        self.var_live_status.set('Sending...')

    def _on_prog(self, sent, total, cur_email):
        self.root.after(0, lambda: self._update_prog(sent, total, cur_email))

    def _update_prog(self, sent, total, cur_email):
        self.var_total_sent_str.set(f"Total Sent {sent} of {total}")
        self.tasks_data[self.current_task]['sent'] = sent
        lname, lsent, f = self.task_btns[self.current_task]
        lsent.config(text=f"Sent-{sent}")

    def _preview_html(self):
        raw = self.txt_body.get('1.0', tk.END)
        parsed = TagEngine.process_tags(raw, recipient_email='customer@example.com', tfn1=self.var_tfn1.get())
        html_out = ContentGenerator.plain_to_html(parsed)
        temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preview_exact.html')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_out)
        webbrowser.open(f'file:///{temp_file}')

    def _open_test_mail_dialog(self):
        w = tk.Toplevel(self.root)
        w.title('Send Test Mail')
        w.geometry('400x180')
        w.configure(bg='#e2e8f0')
        tk.Label(w, text='Recipient Email Address:', bg='#e2e8f0', font=('Segoe UI', 9, 'bold')).pack(pady=10)
        ent = tk.Entry(w, width=36, font=('Segoe UI', 9))
        ent.pack(pady=5)
        accs = self.account_mgr.get_all_accounts()
        if accs:
            ent.insert(0, accs[0].get('email', ''))

        def do_test():
            rec = ent.get().strip()
            if not rec or not accs:
                return
            acc = accs[0]
            msg = ContentGenerator.build_email_message(
                sender_email=acc['email'],
                sender_name=self.var_name.get(),
                recipient_email=rec,
                subject=TagEngine.process_tags(self.var_subject.get(), recipient_email=rec),
                body_text=TagEngine.process_tags(self.txt_body.get('1.0', tk.END), recipient_email=rec),
                html_content=TagEngine.process_tags(self.txt_html.get('1.0', tk.END), recipient_email=rec),
                output_mode=self.var_out_mode.get()
            )
            ok, err = GmailMailer.send_email(acc, rec, msg)
            if ok:
                messagebox.showinfo('Success', f'Test email sent to {rec}!', parent=w)
                w.destroy()
            else:
                messagebox.showerror('Error', err, parent=w)

        tk.Button(w, text='Send Test Mail Now', bg='#16a34a', fg='#ffffff', font=('Segoe UI', 9, 'bold'), command=do_test).pack(pady=15)

    def show_tags_modal(self):
        w = tk.Toplevel(self.root)
        w.title('ALL TAG - Reference')
        w.geometry('550x420')
        w.configure(bg='#1e293b')
        tk.Label(w, text='Available Tags in AMAN2 Ultra:', bg='#1e293b', fg='#38bdf8', font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        tags = [
            ('#RANDOM#', 'Generates 8-character random tracking ID'),
            ('#TFN# / #TFN1#', 'TFN 1 Phone Number (or Base64)'),
            ('#TFNA# / #TFN2#', 'TFN 2 Phone Number (or Base64)'),
            ('#ORDER_ID#', 'Dynamic Order ID format'),
            ('#INVOICE_ID#', 'Dynamic Invoice ID format'),
            ('#DATE# / #TIME#', 'Current date and timestamp'),
            ('#NAME#', 'Recipient name'),
            ('#EMAIL#', 'Recipient email address'),
            ('{Hi|Hello|Dear}', 'Anti-Detect Spintax variation')
        ]
        for t, d in tags:
            f = tk.Frame(w, bg='#334155')
            f.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(f, text=t, bg='#334155', fg='#22c55e', font=('Consolas', 9, 'bold'), width=18, anchor='w').pack(side=tk.LEFT, padx=4)
            tk.Label(f, text=d, bg='#334155', fg='#ffffff', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=4)

    def show_error_list(self):
        w = tk.Toplevel(self.root)
        w.title('Error List')
        w.geometry('500x300')
        t = tk.Text(w, bg='#1e293b', fg='#f87171', font=('Consolas', 9))
        t.pack(fill=tk.BOTH, expand=True)
        if self.active_worker and self.active_worker.errors:
            for err in self.active_worker.errors:
                t.insert(tk.END, f"{err['recipient']} -> {err['error']}\n")
        else:
            t.insert('1.0', 'No errors recorded.')

    def show_admin_or_accounts(self):
        w = tk.Toplevel(self.root)
        w.title('AMAN2 - Gmail Accounts & User Management')
        w.geometry('720x520')
        w.configure(bg='#1e293b')

        # User Creation Frame
        u_box = tk.LabelFrame(w, text='👥 Create User for Friends', bg='#1e293b', fg='#38bdf8', font=('Segoe UI', 9, 'bold'))
        u_box.pack(fill=tk.X, padx=10, pady=6)

        r1 = tk.Frame(u_box, bg='#1e293b')
        r1.pack(fill=tk.X, padx=4, pady=3)
        tk.Label(r1, text='Username:', bg='#1e293b', fg='#ffffff', font=('Segoe UI', 8)).pack(side=tk.LEFT)
        un_e = tk.Entry(r1, width=16, font=('Segoe UI', 8))
        un_e.pack(side=tk.LEFT, padx=2)

        tk.Label(r1, text='Password:', bg='#1e293b', fg='#ffffff', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=4)
        pw_e = tk.Entry(r1, width=16, font=('Segoe UI', 8))
        pw_e.pack(side=tk.LEFT, padx=2)

        def create_u():
            un = un_e.get().strip()
            pw = pw_e.get().strip()
            if not un or not pw:
                return
            ok, msg = self.auth_mgr.create_user(un, pw, daily_limit=5000, days_valid=30)
            messagebox.showinfo('User Result', msg, parent=w)
            un_e.delete(0, tk.END)
            pw_e.delete(0, tk.END)

        tk.Button(r1, text='+ Create User', bg='#16a34a', fg='#ffffff', font=('Segoe UI', 8, 'bold'), command=create_u).pack(side=tk.LEFT, padx=6)

        # Gmail Accounts Frame
        acc_box = tk.LabelFrame(w, text='🔑 Gmail SMTP Accounts Pool', bg='#1e293b', fg='#22c55e', font=('Segoe UI', 9, 'bold'))
        acc_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        f = tk.Frame(acc_box, bg='#334155')
        f.pack(fill=tk.X, padx=6, pady=4)
        
        tk.Label(f, text='Gmail:', bg='#334155', fg='#ffffff', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=4)
        em_ent = tk.Entry(f, width=22, font=('Segoe UI', 8))
        em_ent.pack(side=tk.LEFT, padx=2)

        tk.Label(f, text='16-Char App Password:', bg='#334155', fg='#ffffff', font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=4)
        pw_ent = tk.Entry(f, width=18, font=('Segoe UI', 8), show='*')
        pw_ent.pack(side=tk.LEFT, padx=2)

        tree = ttk.Treeview(acc_box, columns=('Email', 'Sent', 'Status'), show='headings', height=8)
        tree.heading('Email', text='Gmail Account')
        tree.heading('Sent', text='Sent Count')
        tree.heading('Status', text='Status')
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        def ref():
            for r in tree.get_children():
                tree.delete(r)
            for a in self.account_mgr.get_all_accounts():
                tree.insert('', tk.END, values=(a['email'], a.get('sent_count', 0), 'Active'))
        ref()

        def add_acc():
            e = em_ent.get().strip()
            p = pw_ent.get().strip()
            if not e or not p:
                return
            self.account_mgr.add_account(e, p)
            ref()
            em_ent.delete(0, tk.END)
            pw_ent.delete(0, tk.END)
            self.var_sender_email.set(e)

        btn_add = tk.Button(f, text='+ Save Gmail Account', bg='#16a34a', fg='#ffffff', font=('Segoe UI', 8, 'bold'), command=add_acc)
        btn_add.pack(side=tk.LEFT, padx=6)

    def _load_accounts_init(self):
        accs = self.account_mgr.get_all_accounts()
        if accs:
            self.var_sender_email.set(accs[0].get('email', ''))
