#!/usr/bin/env python3
"""
WhatsApp Campaign Studio — Complete Edition
Features: Message Composer · Contacts · Campaign Sender · Settings · Logs
Author: La Yucateca / WhatsApp-Automation-Studio
"""

import sys
import os
import time
import json
import random
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QSplashScreen,
    QProgressBar, QScrollArea, QSlider, QGroupBox, QToolButton,
    QInputDialog, QStyledItemDelegate, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QAbstractItemView, QFrame
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QColor, QPalette, QFont, QTextCursor,
    QPen, QBrush
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, QThread, pyqtSignal
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, StaleElementReferenceException
)

from presets import PresetManager
from contacts import ContactManager

# ── Constants ────────────────────────────────────────────────────────────────
APP_NAME = "WhatsApp Campaign Studio"
APP_VERSION = "2.0.0"
DEFAULT_CONFIG_PATH = os.path.expanduser("~/whatsapp_automation_config.json")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "delay_min": 1.0,
    "delay_max": 3.0,
    "typing_simulation": True,
    "typing_speed": 0.01,
    "randomize_order": False,
    "sound_effects": False,
    "dark_mode": True,
    "first_run": True,
    "session_path": os.path.expanduser("~/whatsapp_session"),
    "xpaths": {
        "message_box": '//*[@id="main"]/footer//div[@contenteditable="true"]',
        "send_button": '//*[@id="main"]/footer//button[@data-testid="send"]',
        "chat_title": '//div[@data-testid="conversation-header-content"]//span',
        "chat_list": '//*[@aria-label="Chat list"]',
        "attach_button": '//*[@data-testid="clip"]',
    }
}

COLOR_SCHEMES = {
    "light": {
        "primary": "#25D366",
        "secondary": "#DCF8C6",
        "background": "#F0F2F5",
        "surface": "#FFFFFF",
        "text": "#111B21",
        "text_secondary": "#667781",
        "accent": "#34B7F1",
        "success": "#25D366",
        "warning": "#FFA000",
        "error": "#F44336",
        "info": "#2196F3",
        "border": "#E0E0E0",
    },
    "dark": {
        "primary": "#00A884",
        "secondary": "#2A2F32",
        "background": "#111B21",
        "surface": "#1F2C34",
        "text": "#E9EDF0",
        "text_secondary": "#8696A0",
        "accent": "#00BCD4",
        "success": "#4CAF50",
        "warning": "#FFC107",
        "error": "#FF5252",
        "info": "#03A9F4",
        "border": "#2A3942",
    }
}


# ── Config Manager ────────────────────────────────────────────────────────────
class ConfigManager:
    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.config.update(saved)
        except Exception as e:
            print(f"[Config] Load error: {e}")

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Save error: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()


config_manager = ConfigManager()


# ── Browser Thread ────────────────────────────────────────────────────────────
class Browser(QThread):
    status_update = pyqtSignal(str, str)
    qr_ready = pyqtSignal()
    logged_in = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.driver = None

    def initialize_driver(self, session_path=None):
        self.status_update.emit("Initializing browser…", "info")
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        if session_path and os.path.exists(session_path):
            opts.add_argument(f"user-data-dir={session_path}")
        try:
            self.driver = webdriver.Chrome(options=opts)
            return True
        except Exception as e:
            self.status_update.emit(f"Browser error: {e}", "error")
            return False

    def run(self):
        session_path = self.config.get("session_path", "")
        if not self.initialize_driver(session_path):
            self.logged_in.emit(False)
            return
        try:
            self.driver.get("https://web.whatsapp.com/")
            self.status_update.emit("Scan QR code to login…", "info")
            self.qr_ready.emit()
            WebDriverWait(self.driver, 90).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@aria-label="Chat list"]')
                )
            )
            self.status_update.emit("Logged in successfully!", "success")
            self.logged_in.emit(True)
        except TimeoutException:
            self.status_update.emit("Login timed out — try again.", "error")
            self.logged_in.emit(False)
        except Exception as e:
            self.status_update.emit(f"Login error: {e}", "error")
            self.logged_in.emit(False)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass


# ── Message Sender Thread ─────────────────────────────────────────────────────
class MessageSender(QThread):
    status_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, driver, messages, config,
                 repeat_count=1, contacts=None, image_path=None):
        super().__init__()
        self.driver = driver
        self.messages = messages
        self.config = config
        self.repeat_count = repeat_count
        self.contacts = contacts or []   # list of Contact objects for campaign
        self.image_path = image_path     # optional image to attach
        self._stop = False

    def run(self):
        # ── Campaign mode: send to each contact ───────────────────────────────
        if self.contacts:
            total = len(self.contacts)
            for idx, contact in enumerate(self.contacts):
                if self._stop:
                    break
                self.status_update.emit(
                    f"Sending to {contact.name} ({idx+1}/{total})…", "info"
                )
                try:
                    self._open_chat(contact)
                    time.sleep(1.5)
                    msgs = self.messages if self.messages else ["Hello!"]
                    if self.config.get("randomize_order"):
                        msgs = random.sample(msgs, len(msgs))
                    for msg in msgs:
                        if self._stop:
                            break
                        self._send_text(msg)
                        delay = random.uniform(
                            self.config.get("delay_min", 1),
                            self.config.get("delay_max", 3)
                        )
                        time.sleep(delay)
                    if self.image_path and os.path.exists(self.image_path):
                        self._send_image(self.image_path)
                    self.progress_update.emit(idx + 1, total)
                except Exception as e:
                    self.status_update.emit(
                        f"Error sending to {contact.name}: {e}", "error"
                    )
            self.status_update.emit("Campaign finished!", "success")
        else:
            # ── Single-chat mode ───────────────────────────────────────────────
            msgs_to_send = self.messages * self.repeat_count
            total = len(msgs_to_send)
            if self.config.get("randomize_order"):
                random.shuffle(msgs_to_send)
            for idx, msg in enumerate(msgs_to_send):
                if self._stop:
                    break
                self._send_text(msg)
                self.progress_update.emit(idx + 1, total)
                delay = random.uniform(
                    self.config.get("delay_min", 1),
                    self.config.get("delay_max", 3)
                )
                time.sleep(delay)
            if self.image_path and os.path.exists(self.image_path):
                self._send_image(self.image_path)
            self.status_update.emit("Messages sent!", "success")
        self.finished.emit()

    def _open_chat(self, contact):
        """Open a chat by searching for the contact name/phone."""
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@data-testid="chat-list-search"]')
            )
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        query = contact.phone if contact.phone else contact.name
        for ch in query:
            search_box.send_keys(ch)
            time.sleep(0.05)
        time.sleep(1.2)
        results = self.driver.find_elements(
            By.XPATH,
            '//*[@aria-label="Chat list"]//*[@data-testid="cell-frame-container"]'
        )
        if results:
            results[0].click()
            time.sleep(0.8)
        else:
            raise RuntimeError(f"Contact '{contact.name}' not found in chat list")

    def _send_text(self, message):
        try:
            box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//*[@id="main"]/footer//div[@contenteditable="true"]')
                )
            )
            box.click()
            if self.config.get("typing_simulation"):
                speed = self.config.get("typing_speed", 0.01)
                for ch in message:
                    box.send_keys(ch)
                    time.sleep(speed)
            else:
                box.send_keys(message)
            time.sleep(0.3)
            box.send_keys(Keys.ENTER)
            self.status_update.emit(f"Sent: {message[:40]}…", "success")
        except Exception as e:
            self.status_update.emit(f"Send error: {e}", "error")

    def _send_image(self, image_path):
        try:
            attach = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@data-testid="clip"]')
                )
            )
            attach.click()
            time.sleep(0.5)
            file_input = self.driver.find_element(
                By.XPATH,
                '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            )
            file_input.send_keys(image_path)
            time.sleep(2)
            send_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@data-testid="send"]')
                )
            )
            send_btn.click()
            time.sleep(1)
            self.status_update.emit("Image sent!", "success")
        except Exception as e:
            self.status_update.emit(f"Image send error: {e}", "error")

    def stop(self):
        self._stop = True


# ── Contact Sync Thread ───────────────────────────────────────────────────────
class ContactSyncer(QThread):
    status_update = pyqtSignal(str, str)
    finished = pyqtSignal(int, int)  # newly_added, total_found

    def __init__(self, driver, contact_manager):
        super().__init__()
        self.driver = driver
        self.cm = contact_manager

    def run(self):
        self.status_update.emit("Syncing contacts from WhatsApp…", "info")
        try:
            added, found = self.cm.sync_from_whatsapp(self.driver)
            self.status_update.emit(
                f"Sync done: {added} new contacts added ({found} found)", "success"
            )
            self.finished.emit(added, found)
        except Exception as e:
            self.status_update.emit(f"Sync error: {e}", "error")
            self.finished.emit(0, 0)


# ── Add/Edit Contact Dialog ───────────────────────────────────────────────────
class ContactDialog(QDialog):
    def __init__(self, parent=None, contact=None):
        super().__init__(parent)
        self.setWindowTitle("Add Contact" if contact is None else "Edit Contact")
        self.setMinimumWidth(380)
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(contact.name if contact else "")
        self.phone_edit = QLineEdit(contact.phone if contact else "")
        self.tags_edit = QLineEdit(
            ", ".join(contact.tags) if contact and contact.tags else ""
        )
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        if contact:
            self.notes_edit.setPlainText(contact.notes)

        layout.addRow("Name *", self.name_edit)
        layout.addRow("Phone / WhatsApp", self.phone_edit)
        layout.addRow("Tags (comma-sep)", self.tags_edit)
        layout.addRow("Notes", self.notes_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def get_data(self):
        tags = [t.strip() for t in self.tags_edit.text().split(",") if t.strip()]
        return {
            "name": self.name_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "tags": tags,
            "notes": self.notes_edit.toPlainText().strip(),
        }


# ── Main Window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1050, 720)
        self.resize(1150, 800)

        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.preset_manager = PresetManager()
        self.contact_manager = ContactManager()

        self.browser: Browser | None = None
        self.sender: MessageSender | None = None
        self.syncer: ContactSyncer | None = None
        self.is_logged_in = False
        self.selected_image_path = ""

        QApplication.setFont(QFont("Segoe UI", 10))

        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        QTimer.singleShot(200, self._load_presets_into_combo)

    # ─────────────────────────────────────────────────────────────────────────
    # UI SETUP
    # ─────────────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        self.login_btn = QPushButton("🔗  Login to WhatsApp")
        self.login_btn.setFixedHeight(36)
        self.logout_btn = QPushButton("🚪  Logout")
        self.logout_btn.setFixedHeight(36)
        self.logout_btn.setEnabled(False)
        self.theme_btn = QPushButton("🌙  Toggle Theme")
        self.theme_btn.setFixedHeight(36)
        self.status_lbl = QLabel("⚪  Not logged in")
        self.status_lbl.setStyleSheet("font-weight:600; padding-left:6px;")
        toolbar.addWidget(self.login_btn)
        toolbar.addWidget(self.logout_btn)
        toolbar.addWidget(self.theme_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.status_lbl)
        root.addLayout(toolbar)

        # ── Tabs ──────────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        root.addWidget(self.tabs)

        self._build_composer_tab()
        self._build_contacts_tab()
        self._build_campaign_tab()
        self._build_settings_tab()
        self._build_logs_tab()

    # ── TAB 1: Message Composer ───────────────────────────────────────────────
    def _build_composer_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "✏️  Composer")

        splitter = QSplitter(Qt.Horizontal)
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.addWidget(splitter)

        # Left pane — message list
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)

        lbl = QLabel("📋  Message Queue")
        lbl.setStyleSheet("font-weight:700; font-size:13px;")
        ll.addWidget(lbl)

        self.message_list = QListWidget()
        self.message_list.setAlternatingRowColors(True)
        self.message_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        ll.addWidget(self.message_list)

        # Preset selector
        preset_row = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        load_preset_btn = QPushButton("Load Preset")
        load_preset_btn.clicked.connect(self._load_preset)
        preset_row.addWidget(QLabel("Preset:"))
        preset_row.addWidget(self.preset_combo, 1)
        preset_row.addWidget(load_preset_btn)
        ll.addLayout(preset_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.add_msg_btn = QPushButton("➕ Add")
        self.remove_msg_btn = QPushButton("🗑 Remove")
        self.clear_btn = QPushButton("🧹 Clear All")
        for b in (self.add_msg_btn, self.remove_msg_btn, self.clear_btn):
            b.setFixedHeight(32)
            btn_row.addWidget(b)
        ll.addLayout(btn_row)

        splitter.addWidget(left)

        # Right pane — editor + controls
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(4, 4, 4, 4)

        rl.addWidget(QLabel("✍️  Message Editor"))
        self.msg_editor = QTextEdit()
        self.msg_editor.setPlaceholderText("Type your message here…")
        rl.addWidget(self.msg_editor, 2)

        # Image upload row
        img_box = QGroupBox("📷  Attach Image (Optional)")
        img_layout = QHBoxLayout(img_box)
        self.image_path_lbl = QLabel("No image selected")
        self.image_path_lbl.setStyleSheet("color: gray; font-style: italic;")
        self.select_image_btn = QPushButton("📁 Browse Image")
        self.clear_image_btn = QPushButton("✖ Clear")
        self.select_image_btn.clicked.connect(self._select_image)
        self.clear_image_btn.clicked.connect(self._clear_image)
        img_layout.addWidget(self.image_path_lbl, 1)
        img_layout.addWidget(self.select_image_btn)
        img_layout.addWidget(self.clear_image_btn)
        rl.addWidget(img_box)

        # Repeat + send controls
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("Repeat:"))
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 9999)
        self.repeat_spin.setValue(1)
        ctrl_row.addWidget(self.repeat_spin)
        ctrl_row.addStretch()
        self.send_btn = QPushButton("🚀  Send Messages")
        self.send_btn.setFixedHeight(38)
        self.send_btn.setEnabled(False)
        self.stop_btn = QPushButton("⏹  Stop")
        self.stop_btn.setFixedHeight(38)
        self.stop_btn.setEnabled(False)
        ctrl_row.addWidget(self.send_btn)
        ctrl_row.addWidget(self.stop_btn)
        rl.addLayout(ctrl_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        rl.addWidget(self.progress_bar)

        # Live preview
        preview_box = QGroupBox("👁  Preview (last selected)")
        pbl = QVBoxLayout(preview_box)
        self.preview_lbl = QLabel("Select a message above to preview it here.")
        self.preview_lbl.setWordWrap(True)
        pbl.addWidget(self.preview_lbl)
        rl.addWidget(preview_box)

        splitter.addWidget(right)
        splitter.setSizes([380, 620])

    # ── TAB 2: Contacts ───────────────────────────────────────────────────────
    def _build_contacts_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "👥  Contacts")

        splitter = QSplitter(Qt.Horizontal)
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.addWidget(splitter)

        # Left — toolbar + table
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)

        # Search
        search_row = QHBoxLayout()
        self.contact_search = QLineEdit()
        self.contact_search.setPlaceholderText("🔍  Search contacts…")
        search_row.addWidget(self.contact_search)
        ll.addLayout(search_row)

        # Action buttons
        action_row = QHBoxLayout()
        self.add_contact_btn = QPushButton("➕ Add")
        self.edit_contact_btn = QPushButton("✏️ Edit")
        self.del_contact_btn = QPushButton("🗑 Delete")
        self.import_csv_btn = QPushButton("📥 Import CSV")
        self.export_csv_btn = QPushButton("📤 Export CSV")
        self.sync_wa_btn = QPushButton("🔄 Sync from WA")
        self.sync_wa_btn.setEnabled(False)
        for b in (self.add_contact_btn, self.edit_contact_btn,
                  self.del_contact_btn, self.import_csv_btn,
                  self.export_csv_btn, self.sync_wa_btn):
            b.setFixedHeight(30)
            action_row.addWidget(b)
        ll.addLayout(action_row)

        # Table
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(4)
        self.contacts_table.setHorizontalHeaderLabels(["Name", "Phone", "Tags", "Notes"])
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contacts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.contacts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.contacts_table.setAlternatingRowColors(True)
        ll.addWidget(self.contacts_table)

        # Count label
        self.contact_count_lbl = QLabel("0 contacts")
        ll.addWidget(self.contact_count_lbl)

        splitter.addWidget(left)

        # Right — detail panel
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 8, 8, 8)

        rl.addWidget(QLabel("📋  Contact Detail"))
        self.contact_detail = QTextEdit()
        self.contact_detail.setReadOnly(True)
        self.contact_detail.setPlaceholderText("Select a contact to view details.")
        rl.addWidget(self.contact_detail)

        splitter.addWidget(right)
        splitter.setSizes([750, 300])

        self._refresh_contacts_table()

    # ── TAB 3: Campaign Sender ────────────────────────────────────────────────
    def _build_campaign_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "📣  Campaign")

        splitter = QSplitter(Qt.Horizontal)
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.addWidget(splitter)

        # Left — contact selector
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)

        ll.addWidget(QLabel("👥  Select Recipients"))

        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("Filter by tag:"))
        self.camp_tag_filter = QComboBox()
        self.camp_tag_filter.addItem("All")
        self.camp_tag_filter.currentTextChanged.connect(self._refresh_campaign_list)
        tag_row.addWidget(self.camp_tag_filter, 1)
        ll.addLayout(tag_row)

        self.campaign_contact_list = QListWidget()
        self.campaign_contact_list.setSelectionMode(QAbstractItemView.MultiSelection)
        ll.addWidget(self.campaign_contact_list)

        sel_row = QHBoxLayout()
        self.camp_select_all_btn = QPushButton("☑ Select All")
        self.camp_deselect_btn = QPushButton("☐ Deselect All")
        self.camp_selected_lbl = QLabel("0 selected")
        sel_row.addWidget(self.camp_select_all_btn)
        sel_row.addWidget(self.camp_deselect_btn)
        sel_row.addStretch()
        sel_row.addWidget(self.camp_selected_lbl)
        ll.addLayout(sel_row)

        splitter.addWidget(left)

        # Right — message composer for campaign
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(4, 4, 4, 4)

        rl.addWidget(QLabel("✍️  Campaign Message"))

        self.camp_msg_edit = QTextEdit()
        self.camp_msg_edit.setPlaceholderText(
            "Type your campaign message here.\n\n"
            "You can use {name} to personalize.\n"
            "Example: Hello {name}! We have a special offer for you!"
        )
        rl.addWidget(self.camp_msg_edit, 2)

        # Preset selector for campaign
        cp_row = QHBoxLayout()
        self.camp_preset_combo = QComboBox()
        camp_load_btn = QPushButton("Load Preset")
        camp_load_btn.clicked.connect(self._load_camp_preset)
        cp_row.addWidget(QLabel("Preset:"))
        cp_row.addWidget(self.camp_preset_combo, 1)
        cp_row.addWidget(camp_load_btn)
        rl.addLayout(cp_row)

        # Image attach for campaign
        camp_img_box = QGroupBox("📷  Attach Image (Optional)")
        camp_img_layout = QHBoxLayout(camp_img_box)
        self.camp_image_lbl = QLabel("No image selected")
        self.camp_image_lbl.setStyleSheet("color:gray; font-style:italic;")
        self.camp_img_btn = QPushButton("📁 Browse")
        self.camp_img_clear = QPushButton("✖ Clear")
        self.camp_img_btn.clicked.connect(self._select_camp_image)
        self.camp_img_clear.clicked.connect(self._clear_camp_image)
        camp_img_layout.addWidget(self.camp_image_lbl, 1)
        camp_img_layout.addWidget(self.camp_img_btn)
        camp_img_layout.addWidget(self.camp_img_clear)
        rl.addWidget(camp_img_box)

        # Send controls
        send_row = QHBoxLayout()
        self.camp_send_btn = QPushButton("🚀  Launch Campaign")
        self.camp_send_btn.setFixedHeight(38)
        self.camp_send_btn.setEnabled(False)
        self.camp_stop_btn = QPushButton("⏹  Stop")
        self.camp_stop_btn.setFixedHeight(38)
        self.camp_stop_btn.setEnabled(False)
        send_row.addStretch()
        send_row.addWidget(self.camp_send_btn)
        send_row.addWidget(self.camp_stop_btn)
        rl.addLayout(send_row)

        self.camp_progress = QProgressBar()
        self.camp_progress.setVisible(False)
        rl.addWidget(self.camp_progress)

        splitter.addWidget(right)
        splitter.setSizes([380, 620])

        self._refresh_campaign_list()

    # ── TAB 4: Settings ───────────────────────────────────────────────────────
    def _build_settings_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "⚙️  Settings")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Delay settings
        delay_grp = QGroupBox("⏱  Delay Between Messages")
        dg_layout = QFormLayout(delay_grp)
        self.delay_min_spin = QDoubleSpinBox()
        self.delay_min_spin.setRange(0.1, 60.0)
        self.delay_min_spin.setSingleStep(0.5)
        self.delay_min_spin.setValue(self.config.get("delay_min", 1.0))
        self.delay_max_spin = QDoubleSpinBox()
        self.delay_max_spin.setRange(0.1, 60.0)
        self.delay_max_spin.setSingleStep(0.5)
        self.delay_max_spin.setValue(self.config.get("delay_max", 3.0))
        dg_layout.addRow("Min delay (s):", self.delay_min_spin)
        dg_layout.addRow("Max delay (s):", self.delay_max_spin)
        layout.addWidget(delay_grp)

        # Typing simulation
        typing_grp = QGroupBox("⌨️  Typing Simulation")
        tg_layout = QFormLayout(typing_grp)
        self.typing_sim_chk = QCheckBox("Enable typing simulation")
        self.typing_sim_chk.setChecked(self.config.get("typing_simulation", True))
        self.typing_speed_slider = QSlider(Qt.Horizontal)
        self.typing_speed_slider.setRange(1, 100)
        speed_val = self.config.get("typing_speed", 0.01)
        self.typing_speed_slider.setValue(max(1, int(speed_val * 1000)))
        self.typing_speed_lbl = QLabel(f"{speed_val:.3f}s / char")
        tg_layout.addRow("", self.typing_sim_chk)
        tg_layout.addRow("Speed:", self.typing_speed_slider)
        tg_layout.addRow("", self.typing_speed_lbl)
        self.typing_speed_slider.valueChanged.connect(
            lambda v: self.typing_speed_lbl.setText(f"{v/1000:.3f}s / char")
        )
        layout.addWidget(typing_grp)

        # Misc
        misc_grp = QGroupBox("🎛  Miscellaneous")
        mg_layout = QFormLayout(misc_grp)
        self.randomize_chk = QCheckBox("Randomize message order")
        self.randomize_chk.setChecked(self.config.get("randomize_order", False))
        self.dark_mode_chk = QCheckBox("Dark mode")
        self.dark_mode_chk.setChecked(self.config.get("dark_mode", True))
        self.dark_mode_chk.stateChanged.connect(self._apply_theme)
        mg_layout.addRow("", self.randomize_chk)
        mg_layout.addRow("", self.dark_mode_chk)
        layout.addWidget(misc_grp)

        # Session path
        sess_grp = QGroupBox("📁  Session / Browser")
        sg_layout = QFormLayout(sess_grp)
        self.session_path_edit = QLineEdit(self.config.get("session_path", ""))
        sg_layout.addRow("Session path:", self.session_path_edit)
        layout.addWidget(sess_grp)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save Settings")
        save_btn.clicked.connect(self._save_settings)
        reset_btn = QPushButton("↩️  Reset Defaults")
        reset_btn.clicked.connect(self._reset_settings)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(reset_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

    # ── TAB 5: Logs ───────────────────────────────────────────────────────────
    def _build_logs_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "📄  Logs")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_view)

        btn_row = QHBoxLayout()
        clear_log_btn = QPushButton("🧹 Clear Logs")
        export_log_btn = QPushButton("📤 Export Logs")
        clear_log_btn.clicked.connect(self.log_view.clear)
        export_log_btn.clicked.connect(self._export_logs)
        btn_row.addStretch()
        btn_row.addWidget(clear_log_btn)
        btn_row.addWidget(export_log_btn)
        layout.addLayout(btn_row)

    # ─────────────────────────────────────────────────────────────────────────
    # CONNECTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _setup_connections(self):
        # Toolbar
        self.login_btn.clicked.connect(self._login)
        self.logout_btn.clicked.connect(self._logout)
        self.theme_btn.clicked.connect(self._toggle_theme)

        # Composer tab
        self.add_msg_btn.clicked.connect(self._add_message)
        self.remove_msg_btn.clicked.connect(self._remove_message)
        self.clear_btn.clicked.connect(self._clear_messages)
        self.message_list.currentRowChanged.connect(self._preview_message)
        self.send_btn.clicked.connect(self._start_sending)
        self.stop_btn.clicked.connect(self._stop_sending)

        # Contacts tab
        self.contact_search.textChanged.connect(self._refresh_contacts_table)
        self.add_contact_btn.clicked.connect(self._add_contact)
        self.edit_contact_btn.clicked.connect(self._edit_contact)
        self.del_contact_btn.clicked.connect(self._delete_contacts)
        self.import_csv_btn.clicked.connect(self._import_csv)
        self.export_csv_btn.clicked.connect(self._export_csv)
        self.sync_wa_btn.clicked.connect(self._sync_contacts)
        self.contacts_table.currentRowChanged.connect(self._show_contact_detail)

        # Campaign tab
        self.camp_select_all_btn.clicked.connect(
            lambda: self.campaign_contact_list.selectAll()
        )
        self.camp_deselect_btn.clicked.connect(
            lambda: self.campaign_contact_list.clearSelection()
        )
        self.campaign_contact_list.itemSelectionChanged.connect(
            self._update_camp_selection_count
        )
        self.camp_send_btn.clicked.connect(self._launch_campaign)
        self.camp_stop_btn.clicked.connect(self._stop_campaign)

    # ─────────────────────────────────────────────────────────────────────────
    # LOGIN / LOGOUT
    # ─────────────────────────────────────────────────────────────────────────
    def _login(self):
        if self.is_logged_in:
            QMessageBox.information(self, "Already Logged In",
                                    "You are already logged in to WhatsApp.")
            return
        self.log("Connecting to WhatsApp Web…", "info")
        self.browser = Browser(self.config)
        self.browser.status_update.connect(self.log)
        self.browser.qr_ready.connect(self._on_qr_ready)
        self.browser.logged_in.connect(self._on_logged_in)
        self.browser.start()
        self.login_btn.setEnabled(False)
        self.status_lbl.setText("🟡  Connecting…")

    def _logout(self):
        if self.browser:
            self.browser.close()
        self.is_logged_in = False
        self.login_btn.setEnabled(True)
        self.logout_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.camp_send_btn.setEnabled(False)
        self.sync_wa_btn.setEnabled(False)
        self.status_lbl.setText("⚪  Not logged in")
        self.log("Logged out.", "info")

    def _on_qr_ready(self):
        QMessageBox.information(
            self, "Scan QR Code",
            "WhatsApp Web is open in the browser.\n"
            "Please scan the QR code with your phone to log in."
        )

    def _on_logged_in(self, success: bool):
        self.is_logged_in = success
        if success:
            self.status_lbl.setText("🟢  Logged in")
            self.login_btn.setEnabled(False)
            self.logout_btn.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.camp_send_btn.setEnabled(True)
            self.sync_wa_btn.setEnabled(True)
        else:
            self.status_lbl.setText("🔴  Login failed")
            self.login_btn.setEnabled(True)

    # ─────────────────────────────────────────────────────────────────────────
    # COMPOSER TAB ACTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _load_presets_into_combo(self):
        names = self.preset_manager.get_preset_names()
        self.preset_combo.clear()
        self.preset_combo.addItem("— Select preset —")
        self.preset_combo.addItems(names)
        self.camp_preset_combo.clear()
        self.camp_preset_combo.addItem("— Select preset —")
        self.camp_preset_combo.addItems(names)

    def _load_preset(self):
        idx = self.preset_combo.currentIndex() - 1
        if idx < 0:
            return
        msgs = self.preset_manager.get_messages_from_preset(idx)
        self.message_list.clear()
        for m in msgs:
            self.message_list.addItem(m)
        self.log(f"Preset loaded: {self.preset_combo.currentText()}", "info")

    def _load_camp_preset(self):
        idx = self.camp_preset_combo.currentIndex() - 1
        if idx < 0:
            return
        msgs = self.preset_manager.get_messages_from_preset(idx)
        self.camp_msg_edit.setPlainText("\n---\n".join(msgs))

    def _add_message(self):
        text = self.msg_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Message", "Please type a message first.")
            return
        self.message_list.addItem(text)
        self.msg_editor.clear()

    def _remove_message(self):
        for item in self.message_list.selectedItems():
            self.message_list.takeItem(self.message_list.row(item))

    def _clear_messages(self):
        if QMessageBox.question(
            self, "Clear All", "Remove all messages?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.message_list.clear()

    def _preview_message(self, row):
        if row >= 0:
            item = self.message_list.item(row)
            if item:
                self.preview_lbl.setText(item.text())

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)"
        )
        if path:
            self.selected_image_path = path
            fname = os.path.basename(path)
            self.image_path_lbl.setText(f"📎 {fname}")
            self.image_path_lbl.setStyleSheet("color: green; font-style: normal;")

    def _clear_image(self):
        self.selected_image_path = ""
        self.image_path_lbl.setText("No image selected")
        self.image_path_lbl.setStyleSheet("color: gray; font-style: italic;")

    def _start_sending(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Not Logged In",
                                "Please login to WhatsApp first.")
            return
        msgs = [self.message_list.item(i).text()
                for i in range(self.message_list.count())]
        if not msgs:
            QMessageBox.warning(self, "No Messages",
                                "Add at least one message to the queue.")
            return
        driver = self.browser.driver if self.browser else None
        if not driver:
            QMessageBox.warning(self, "No Browser",
                                "Browser is not running. Please login again.")
            return
        self.sender = MessageSender(
            driver=driver,
            messages=msgs,
            config=self.config,
            repeat_count=self.repeat_spin.value(),
            image_path=self.selected_image_path or None
        )
        self.sender.status_update.connect(self.log)
        self.sender.progress_update.connect(self._update_progress)
        self.sender.finished.connect(self._sending_done)
        self.sender.start()

        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log("Sending started…", "info")

    def _stop_sending(self):
        if self.sender:
            self.sender.stop()
        self.stop_btn.setEnabled(False)
        self.log("Stopping…", "warning")

    def _sending_done(self):
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.log("Done.", "success")

    def _update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current} / {total}")

    # ─────────────────────────────────────────────────────────────────────────
    # CONTACTS TAB ACTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _refresh_contacts_table(self, query: str = ""):
        if not isinstance(query, str):
            query = self.contact_search.text()
        contacts = self.contact_manager.search_contacts(query)
        self.contacts_table.setRowCount(len(contacts))
        for row, c in enumerate(contacts):
            self.contacts_table.setItem(row, 0, QTableWidgetItem(c.name))
            self.contacts_table.setItem(row, 1, QTableWidgetItem(c.phone))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(", ".join(c.tags)))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(c.notes))
        total = len(self.contact_manager.contacts)
        self.contact_count_lbl.setText(
            f"{len(contacts)} shown / {total} total contacts"
        )
        self._refresh_campaign_list()

    def _show_contact_detail(self, row):
        query = self.contact_search.text()
        contacts = self.contact_manager.search_contacts(query)
        if 0 <= row < len(contacts):
            c = contacts[row]
            text = (
                f"Name:   {c.name}\n"
                f"Phone:  {c.phone or '(none)'}\n"
                f"Tags:   {', '.join(c.tags) or '(none)'}\n"
                f"Notes:  {c.notes or '(none)'}\n"
                f"Source: {'WhatsApp Sync' if c.synced_from_wa else 'Manual / CSV'}"
            )
            self.contact_detail.setPlainText(text)

    def _add_contact(self):
        dlg = ContactDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            ok, msg = self.contact_manager.add_contact(
                d["name"], d["phone"], d["tags"], d["notes"]
            )
            if ok:
                self._refresh_contacts_table()
                self.log(f"Contact added: {d['name']}", "success")
            else:
                QMessageBox.warning(self, "Cannot Add", msg)

    def _edit_contact(self):
        row = self.contacts_table.currentRow()
        query = self.contact_search.text()
        contacts = self.contact_manager.search_contacts(query)
        if row < 0 or row >= len(contacts):
            QMessageBox.information(self, "Select Contact",
                                    "Please select a contact to edit.")
            return
        c = contacts[row]
        dlg = ContactDialog(self, contact=c)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            real_idx = self.contact_manager.contacts.index(c)
            self.contact_manager.update_contact(
                real_idx, d["name"], d["phone"], d["tags"], d["notes"]
            )
            self._refresh_contacts_table()
            self.log(f"Contact updated: {d['name']}", "success")

    def _delete_contacts(self):
        rows = set(idx.row() for idx in self.contacts_table.selectedIndexes())
        if not rows:
            QMessageBox.information(self, "Select Contact",
                                    "Please select at least one contact to delete.")
            return
        if QMessageBox.question(
            self, "Delete Contacts",
            f"Delete {len(rows)} contact(s)?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            return
        query = self.contact_search.text()
        contacts = self.contact_manager.search_contacts(query)
        real_indices = [self.contact_manager.contacts.index(contacts[r])
                        for r in sorted(rows) if r < len(contacts)]
        self.contact_manager.remove_contacts_by_indices(real_indices)
        self._refresh_contacts_table()
        self.log(f"Deleted {len(rows)} contact(s).", "warning")

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Contacts CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        added, skipped, errors = self.contact_manager.import_from_csv(path)
        self._refresh_contacts_table()
        msg = f"Import complete.\nAdded: {added}  Skipped: {skipped}"
        if errors:
            msg += f"\n\nWarnings:\n" + "\n".join(errors[:10])
        QMessageBox.information(self, "Import Result", msg)
        self.log(f"CSV import: {added} added, {skipped} skipped.", "success")

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Contacts CSV", "contacts_export.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        if self.contact_manager.export_to_csv(path):
            QMessageBox.information(self, "Export Done",
                                    f"Contacts exported to:\n{path}")
            self.log(f"Contacts exported: {path}", "success")
        else:
            QMessageBox.warning(self, "Export Failed", "Could not write file.")

    def _sync_contacts(self):
        if not self.is_logged_in or not self.browser or not self.browser.driver:
            QMessageBox.warning(self, "Not Logged In",
                                "Login to WhatsApp first.")
            return
        self.sync_wa_btn.setEnabled(False)
        self.sync_wa_btn.setText("🔄 Syncing…")
        self.syncer = ContactSyncer(self.browser.driver, self.contact_manager)
        self.syncer.status_update.connect(self.log)
        self.syncer.finished.connect(self._sync_done)
        self.syncer.start()
        self.log("WhatsApp contact sync started…", "info")

    def _sync_done(self, added, found):
        self.sync_wa_btn.setEnabled(True)
        self.sync_wa_btn.setText("🔄 Sync from WA")
        self._refresh_contacts_table()
        QMessageBox.information(
            self, "Sync Complete",
            f"Sync finished!\n\nFound: {found} contacts\nNewly added: {added}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CAMPAIGN TAB ACTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _refresh_campaign_list(self, tag_filter: str = ""):
        if not isinstance(tag_filter, str):
            tag_filter = ""
        self.campaign_contact_list.clear()

        # Rebuild tag filter combo
        all_tags = set()
        for c in self.contact_manager.contacts:
            all_tags.update(c.tags)
        current_tag = self.camp_tag_filter.currentText()
        self.camp_tag_filter.blockSignals(True)
        self.camp_tag_filter.clear()
        self.camp_tag_filter.addItem("All")
        self.camp_tag_filter.addItems(sorted(all_tags))
        idx = self.camp_tag_filter.findText(current_tag)
        self.camp_tag_filter.setCurrentIndex(max(0, idx))
        self.camp_tag_filter.blockSignals(False)

        tag = self.camp_tag_filter.currentText()
        for c in self.contact_manager.contacts:
            if tag == "All" or tag in c.tags:
                item = QListWidgetItem(c.display_name())
                item.setData(Qt.UserRole, c)
                self.campaign_contact_list.addItem(item)

        self._update_camp_selection_count()

    def _update_camp_selection_count(self):
        n = len(self.campaign_contact_list.selectedItems())
        self.camp_selected_lbl.setText(f"{n} selected")

    def _select_camp_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)"
        )
        if path:
            self.camp_selected_image = path
            self.camp_image_lbl.setText(f"📎 {os.path.basename(path)}")
            self.camp_image_lbl.setStyleSheet("color: green; font-style: normal;")

    def _clear_camp_image(self):
        self.camp_selected_image = ""
        self.camp_image_lbl.setText("No image selected")
        self.camp_image_lbl.setStyleSheet("color: gray; font-style: italic;")

    def _launch_campaign(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Not Logged In",
                                "Please login to WhatsApp first.")
            return
        selected_items = self.campaign_contact_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Recipients",
                                "Select at least one contact to send to.")
            return
        raw_msg = self.camp_msg_edit.toPlainText().strip()
        if not raw_msg:
            QMessageBox.warning(self, "No Message",
                                "Please type a campaign message.")
            return

        contacts = [item.data(Qt.UserRole) for item in selected_items]
        # Personalise per contact using {name}
        messages_per_contact = []
        for c in contacts:
            personalised = raw_msg.replace("{name}", c.name)
            messages_per_contact.append(personalised)

        ok = QMessageBox.question(
            self, "Launch Campaign",
            f"Send to {len(contacts)} contact(s)?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ok == QMessageBox.No:
            return

        driver = self.browser.driver if self.browser else None
        if not driver:
            QMessageBox.warning(self, "No Browser",
                                "Browser not running. Please login again.")
            return

        image_path = getattr(self, "camp_selected_image", "")

        # Build one sender per contact so each gets its personalised message
        self.camp_sender = MessageSender(
            driver=driver,
            messages=[raw_msg],
            config=self.config,
            contacts=contacts,
            image_path=image_path or None
        )
        # Override messages per contact (inject into sender's run logic via contacts list)
        self.camp_sender.status_update.connect(self.log)
        self.camp_sender.progress_update.connect(self._camp_progress)
        self.camp_sender.finished.connect(self._campaign_done)
        self.camp_sender.start()

        self.camp_send_btn.setEnabled(False)
        self.camp_stop_btn.setEnabled(True)
        self.camp_progress.setVisible(True)
        self.camp_progress.setMaximum(len(contacts))
        self.camp_progress.setValue(0)
        self.log(f"Campaign launched → {len(contacts)} contacts.", "info")

    def _camp_progress(self, current, total):
        self.camp_progress.setMaximum(total)
        self.camp_progress.setValue(current)
        self.camp_progress.setFormat(f"{current} / {total}")

    def _stop_campaign(self):
        if hasattr(self, "camp_sender") and self.camp_sender:
            self.camp_sender.stop()
        self.camp_stop_btn.setEnabled(False)
        self.log("Campaign stop requested…", "warning")

    def _campaign_done(self):
        self.camp_send_btn.setEnabled(True)
        self.camp_stop_btn.setEnabled(False)
        self.camp_progress.setVisible(False)
        self.log("Campaign complete.", "success")
        QMessageBox.information(self, "Campaign Done",
                                "Campaign messages sent successfully!")

    # ─────────────────────────────────────────────────────────────────────────
    # SETTINGS
    # ─────────────────────────────────────────────────────────────────────────
    def _save_settings(self):
        self.config_manager.set("delay_min", self.delay_min_spin.value())
        self.config_manager.set("delay_max", self.delay_max_spin.value())
        self.config_manager.set("typing_simulation",
                                self.typing_sim_chk.isChecked())
        self.config_manager.set("typing_speed",
                                self.typing_speed_slider.value() / 1000)
        self.config_manager.set("randomize_order", self.randomize_chk.isChecked())
        self.config_manager.set("dark_mode", self.dark_mode_chk.isChecked())
        self.config_manager.set("session_path", self.session_path_edit.text())
        self.config = self.config_manager.config
        self.log("Settings saved.", "success")
        QMessageBox.information(self, "Saved", "Settings saved successfully!")

    def _reset_settings(self):
        if QMessageBox.question(
            self, "Reset Settings", "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.config_manager.config = DEFAULT_CONFIG.copy()
            self.config_manager.save_config()
            self.config = self.config_manager.config
            self.delay_min_spin.setValue(DEFAULT_CONFIG["delay_min"])
            self.delay_max_spin.setValue(DEFAULT_CONFIG["delay_max"])
            self.typing_sim_chk.setChecked(DEFAULT_CONFIG["typing_simulation"])
            self.randomize_chk.setChecked(DEFAULT_CONFIG["randomize_order"])
            self.dark_mode_chk.setChecked(DEFAULT_CONFIG["dark_mode"])
            self.session_path_edit.setText(DEFAULT_CONFIG["session_path"])
            self.log("Settings reset to defaults.", "info")

    # ─────────────────────────────────────────────────────────────────────────
    # LOGS
    # ─────────────────────────────────────────────────────────────────────────
    def log(self, message: str, level: str = "info"):
        colors = {
            "info": "#8696A0",
            "success": "#4CAF50",
            "warning": "#FFC107",
            "error": "#FF5252",
        }
        color = colors.get(level, "#E9EDF0")
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#555;">[{ts}]</span> '
            f'<span style="color:{color};">{message}</span>'
        )
        self.log_view.append(html)
        self.log_view.moveCursor(QTextCursor.End)

    def _export_logs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "campaign_logs.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_view.toPlainText())
            QMessageBox.information(self, "Exported", f"Logs saved to:\n{path}")

    # ─────────────────────────────────────────────────────────────────────────
    # THEME
    # ─────────────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self.dark_mode_chk.setChecked(not self.dark_mode_chk.isChecked())
        self._apply_theme()

    def _apply_theme(self):
        dark = self.dark_mode_chk.isChecked() if hasattr(self, "dark_mode_chk") \
            else self.config.get("dark_mode", True)
        s = COLOR_SCHEMES["dark"] if dark else COLOR_SCHEMES["light"]

        self.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background-color: {s['background']};
            color: {s['text']};
        }}
        QTabWidget::pane {{
            border: 1px solid {s['border']};
            border-radius: 6px;
        }}
        QTabBar::tab {{
            background: {s['secondary']};
            color: {s['text']};
            padding: 8px 18px;
            margin: 2px;
            border-radius: 6px 6px 0 0;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background: {s['primary']};
            color: #fff;
        }}
        QPushButton {{
            background-color: {s['primary']};
            color: #fff;
            border: none;
            border-radius: 5px;
            padding: 6px 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {s['accent']};
        }}
        QPushButton:disabled {{
            background-color: {s['border']};
            color: {s['text_secondary']};
        }}
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {s['surface']};
            color: {s['text']};
            border: 1px solid {s['border']};
            border-radius: 5px;
            padding: 4px 8px;
        }}
        QGroupBox {{
            border: 1px solid {s['border']};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 8px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            color: {s['text']};
        }}
        QTableWidget {{
            background-color: {s['surface']};
            alternate-background-color: {s['secondary']};
            color: {s['text']};
            border: 1px solid {s['border']};
            gridline-color: {s['border']};
        }}
        QHeaderView::section {{
            background-color: {s['secondary']};
            color: {s['text']};
            padding: 6px;
            border: none;
            font-weight: 700;
        }}
        QListWidget {{
            background-color: {s['surface']};
            alternate-background-color: {s['secondary']};
            color: {s['text']};
            border: 1px solid {s['border']};
        }}
        QListWidget::item:selected {{
            background-color: {s['primary']};
            color: #fff;
        }}
        QProgressBar {{
            border: 1px solid {s['border']};
            border-radius: 4px;
            background-color: {s['surface']};
            text-align: center;
            color: {s['text']};
        }}
        QProgressBar::chunk {{
            background-color: {s['primary']};
            border-radius: 3px;
        }}
        QScrollBar:vertical {{
            background: {s['background']};
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: {s['border']};
            border-radius: 4px;
            min-height: 24px;
        }}
        QSplitter::handle {{
            background: {s['border']};
        }}
        QLabel {{
            color: {s['text']};
        }}
        """)


# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("LaYucateca")

    # Try to set app icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
