import json
import logging
import os
import sys

import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QPushButton, QSystemTrayIcon, QTextEdit, QTimeEdit, QVBoxLayout,
    QWidget, QStackedWidget,
)

import sys
from pathlib import Path

# Path(__file__).resolve().parent.parent / 'Backend'

from Backend.config import (
    CONFIG_PATH, HISTORY_PATH, load_config, save_config,
    load_history, save_to_history, ensure_config,
)

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/users/{}/repos"

STYLE = """
* {
    font-family: 'Segoe UI', sans-serif;
}
QMainWindow, QWidget#root {
    background-color: #0a0a0a;
}
QWidget#sidebar {
    background-color: #0f0f0f;
    border-right: 1px solid #1e1e1e;
}
QWidget#main {
    background-color: #0a0a0a;
}
QLabel#brand {
    font-size: 11px;
    letter-spacing: 4px;
    color: #c9a84c;
    font-weight: bold;
}
QLabel#tagline {
    font-size: 22px;
    color: #f0ece4;
    font-weight: 300;
    line-height: 1.4;
}
QLabel#tagline_accent {
    font-size: 22px;
    color: #c9a84c;
    font-weight: 600;
}
QLabel#section_title {
    font-size: 10px;
    letter-spacing: 3px;
    color: #555;
    font-weight: bold;
}
QLabel#status {
    font-size: 11px;
    color: #555;
    padding: 4px 0;
}
QLabel#status_ok {
    font-size: 11px;
    color: #4a7;
    padding: 4px 0;
}
QLabel#status_err {
    font-size: 11px;
    color: #c44;
    padding: 4px 0;
}
QLineEdit {
    background-color: #111;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 10px 14px;
    color: #f0ece4;
    font-size: 13px;
    selection-background-color: #c9a84c;
}
QLineEdit:focus {
    border: 1px solid #c9a84c;
    background-color: #131313;
}
QPushButton#primary {
    background-color: #c9a84c;
    color: #0a0a0a;
    border: none;
    border-radius: 6px;
    padding: 11px 20px;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
}
QPushButton#primary:hover {
    background-color: #d4b86a;
}
QPushButton#primary:pressed {
    background-color: #b8973d;
}
QPushButton#primary:disabled {
    background-color: #333;
    color: #666;
}
QPushButton#ghost {
    background-color: transparent;
    color: #555;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 11px 20px;
    font-size: 12px;
    letter-spacing: 1px;
}
QPushButton#ghost:hover {
    border: 1px solid #c9a84c;
    color: #c9a84c;
}
QPushButton#tab {
    background-color: transparent;
    color: #555;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 10px 20px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
}
QPushButton#tab:hover {
    color: #f0ece4;
}
QPushButton#tab_active {
    background-color: transparent;
    color: #c9a84c;
    border: none;
    border-bottom: 2px solid #c9a84c;
    border-radius: 0px;
    padding: 10px 20px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
}
QPushButton#danger {
    background-color: transparent;
    color: #555;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 11px;
    letter-spacing: 1px;
}
QPushButton#danger:hover {
    border: 1px solid #8b2e2e;
    color: #c0392b;
}
QPushButton#toggle_on {
    background-color: #1a1a0f;
    color: #c9a84c;
    border: 1px solid #c9a84c44;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 11px;
    text-align: left;
}
QPushButton#toggle_on:hover {
    background-color: #222210;
}
QPushButton#toggle_off {
    background-color: transparent;
    color: #444;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 11px;
    text-align: left;
}
QPushButton#toggle_off:hover {
    border: 1px solid #333;
    color: #666;
}
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 13px;
    color: #f0ece4;
}
QListWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #111;
    color: #888;
}
QListWidget::item:selected {
    background-color: #161410;
    color: #c9a84c;
    border-left: 2px solid #c9a84c;
}
QListWidget::item:hover {
    background-color: #0f0f0f;
    color: #f0ece4;
}
QTextEdit {
    background-color: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    color: #c9d1d9;
    font-size: 13px;
    padding: 12px;
    line-height: 1.6;
}
QScrollBar:vertical {
    background: transparent;
    width: 4px;
}
QScrollBar::handle:vertical {
    background: #1e1e1e;
    border-radius: 2px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QFrame#divider {
    background-color: #1e1e1e;
    max-height: 1px;
}
QTimeEdit {
    background-color: #111;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f0ece4;
    font-size: 13px;
}
QTimeEdit:focus {
    border: 1px solid #c9a84c;
}
QDialog {
    background-color: #0a0a0a;
}
"""


# ── First-Run Wizard ───────────────────────────────────────

class FirstRunWizard(QDialog):
    """Dialog shown on first launch when .env keys are missing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Orbit — Setup")
        self.setMinimumSize(480, 400)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Welcome to Orbit")
        title.setObjectName("tagline")
        layout.addWidget(title)

        subtitle = QLabel("Set up your API keys to get started. These are saved to your .env file.")
        subtitle.setObjectName("status")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(12)

        self.fields = {}
        env_vars = [
            ("GITHUB_TOKEN", "GitHub Personal Access Token", ""),
            ("GROQ_API_KEY", "Groq API Key", ""),
            ("GMAIL_USER", "Gmail Address", ""),
            ("GMAIL_APP_PASSWORD", "Gmail App Password", ""),
        ]

        for key, label_text, placeholder in env_vars:
            lbl = QLabel(label_text.upper())
            lbl.setObjectName("section_title")
            layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setEchoMode(QLineEdit.EchoMode.Password if "PASSWORD" in key or "TOKEN" in key else QLineEdit.EchoMode.Normal)
            layout.addWidget(inp)
            self.fields[key] = inp
            layout.addSpacing(4)

        layout.addSpacing(16)

        btn = QPushButton("SAVE & CONTINUE")
        btn.setObjectName("primary")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._save)
        layout.addWidget(btn)

    def _save(self):
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()

        existing = {}
        for line in lines:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()

        for key, inp in self.fields.items():
            val = inp.text().strip()
            if val:
                existing[key] = val

        with open(env_path, "w") as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")

        # Reload dotenv
        from dotenv import load_dotenv
        load_dotenv(override=True)

        self.accept()


# ── Worker Threads ─────────────────────────────────────────

class RepoFetchThread(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, username: str):
        super().__init__()
        self.username = username

    def run(self):
        try:
            url = GITHUB_API.format(self.username)
            res = requests.get(url, params={"per_page": 100, "sort": "updated"}, timeout=15)
            if res.status_code == 200:
                self.result.emit(res.json())
            else:
                self.error.emit(f"GitHub error {res.status_code}")
        except Exception as e:
            self.error.emit(str(e))


class DigestThread(QThread):
    """Fetches all sources and generates the digest (no sending)."""
    done = pyqtSignal(str, dict)  # (digest_text, per_source_status)
    error = pyqtSignal(str)

    def __init__(self, source_states: dict):
        super().__init__()
        self.source_states = source_states

    def run(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from Backend.github_fetcher import fetch_repo_data
        from Backend.hf_fetcher import fetch_hf_data
        from Backend.reddit_fetcher import fetch_reddit_data
        from Backend.devto_fetcher import fetch_devto_data
        from Backend.gh_trending_fetcher import fetch_gh_trending
        from Backend.digest_generator import generate_digest

        source_status: dict[str, str] = {}
        fetch_results: dict[str, object] = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(fetch_repo_data): "github",
            }
            if self.source_states.get("hf", True):
                futures[executor.submit(fetch_hf_data)] = "hf"
            if self.source_states.get("reddit", True):
                futures[executor.submit(fetch_reddit_data)] = "reddit"
            if self.source_states.get("devto", True):
                futures[executor.submit(fetch_devto_data)] = "devto"
            if self.source_states.get("trending", True):
                futures[executor.submit(fetch_gh_trending)] = "trending"

            for future in as_completed(futures):
                key = futures[future]
                try:
                    fetch_results[key] = future.result()
                    source_status[key] = "ok"
                except Exception as e:
                    logger.error("Failed to fetch %s: %s", key, e)
                    fetch_results[key] = None
                    source_status[key] = f"error: {e}"

        try:
            digest = generate_digest(
                digest_data=fetch_results.get("github"),
                hf_data=fetch_results.get("hf"),
                reddit_data=fetch_results.get("reddit"),
                devto_data=fetch_results.get("devto"),
                gh_trending=fetch_results.get("trending"),
            )
            self.done.emit(digest, source_status)
        except Exception as e:
            self.error.emit(str(e))


class SendThread(QThread):
    """Sends a pre-generated digest through configured channels."""
    done = pyqtSignal(dict)  # per-channel results
    error = pyqtSignal(str)

    def __init__(self, email: str, digest_text: str):
        super().__init__()
        self.email = email
        self.digest_text = digest_text

    def run(self):
        try:
            from Backend.emailer import send_digest
            results = send_digest(self.email, self.digest_text)
            self.done.emit(results)
        except Exception as e:
            self.error.emit(str(e))


# ── Preview Dialog ─────────────────────────────────────────

class PreviewDialog(QDialog):
    """Shows the generated digest and lets user confirm before sending."""

    def __init__(self, digest_text: str, source_status: dict[str, str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Orbit — Digest Preview")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(STYLE)
        self.confirmed = False
        self._build_ui(digest_text, source_status)

    def _build_ui(self, digest_text: str, source_status: dict[str, str]):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("DIGEST PREVIEW")
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Source status summary
        status_parts = []
        icons = {"ok": "✓", "error": "✗"}
        for key, status in source_status.items():
            icon = icons.get("ok" if status == "ok" else "error", "?")
            status_parts.append(f"{icon} {key}")
        status_label = QLabel("  ".join(status_parts))
        status_label.setObjectName("status")
        layout.addWidget(status_label)

        layout.addSpacing(8)

        view = QTextEdit()
        view.setReadOnly(True)
        view.setText(digest_text)
        view.setMinimumHeight(300)
        layout.addWidget(view)

        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setObjectName("ghost")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)

        send_btn = QPushButton("SEND DIGEST")
        send_btn.setObjectName("primary")
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self._confirm)
        btn_row.addWidget(send_btn)

        layout.addLayout(btn_row)

    def _confirm(self):
        self.confirmed = True
        self.accept()


# ── Main Window ────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbit — Daily Digest Agent")
        self.setMinimumSize(860, 620)
        self.resize(960, 660)

        ensure_config()
        self.config = load_config()
        self.history = load_history()
        self._pending_digest: str | None = None

        self.setStyleSheet(STYLE)
        self._build_ui()
        self._setup_tray()

    # ── Config helpers ─────────────────────────────────────

    def _save_config(self):
        save_config(self.config)

    # ── System Tray ────────────────────────────────────────

    def _setup_tray(self):
        # Use a simple built-in icon approach; in production, use a .ico file
        self.tray_icon = QSystemTrayIcon(self)

        # Try to load a custom icon, fall back to a standard pixmap
        icon_path = os.path.join(os.path.dirname(__file__), "Data", "orbit.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            pixmap = QIcon.fromTheme("applications-internet").pixmap(32, 32)
            if pixmap.isNull():
                # Create a minimal colored icon
                from PyQt6.QtGui import QPixmap, QColor, QPainter
                px = QPixmap(32, 32)
                px.fill(QColor(0, 0, 0, 0))
                painter = QPainter(px)
                painter.setBrush(QColor("#c9a84c"))
                painter.drawEllipse(4, 4, 24, 24)
                painter.end()
                self.tray_icon.setIcon(QIcon(px))

        tray_menu = QApplication.instance().style().standardIcon(
            QApplication.instance().style().StandardPixmap.SP_ComputerIcon
        )

        menu = self.tray_icon.contextMenu()
        if menu is None:
            menu = QApplication.instance().menuBar().addMenu("") if False else None
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()

        show_action = menu.addAction("Show Orbit")
        show_action.triggered.connect(self._show_window)

        digest_action = menu.addAction("Send Digest Now")
        digest_action.triggered.connect(self.send_digest_now)

        menu.addSeparator()

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()

    def _quit_app(self):
        self.tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Orbit",
            "Orbit is running in the background. Double-click the tray icon to show.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    # ── UI Build ───────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(28, 36, 28, 28)
        sidebar_layout.setSpacing(0)

        brand = QLabel("ORBIT")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)

        sidebar_layout.addSpacing(28)

        tagline = QLabel("Your repos.\nEvery morning.")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        sidebar_layout.addWidget(tagline)

        accent = QLabel("Delivered.")
        accent.setObjectName("tagline_accent")
        sidebar_layout.addWidget(accent)

        sidebar_layout.addSpacing(40)

        # Email
        email_lbl = QLabel("RECIPIENT EMAIL")
        email_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(email_lbl)
        sidebar_layout.addSpacing(8)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@gmail.com")
        self.email_input.setText(self.config.get("email", ""))
        sidebar_layout.addWidget(self.email_input)

        sidebar_layout.addSpacing(24)

        # GitHub username
        user_lbl = QLabel("GITHUB USERNAME")
        user_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(user_lbl)
        sidebar_layout.addSpacing(8)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("aliii-codes")
        self.username_input.returnPressed.connect(self.fetch_repos)
        sidebar_layout.addWidget(self.username_input)

        sidebar_layout.addSpacing(12)

        fetch_btn = QPushButton("FETCH REPOS")
        fetch_btn.setObjectName("primary")
        fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fetch_btn.clicked.connect(self.fetch_repos)
        sidebar_layout.addWidget(fetch_btn)

        sidebar_layout.addSpacing(8)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status")
        self.status_lbl.setWordWrap(True)
        sidebar_layout.addWidget(self.status_lbl)

        sidebar_layout.addSpacing(24)

        # Source toggles
        sources_lbl = QLabel("SOURCES")
        sources_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(sources_lbl)
        sidebar_layout.addSpacing(8)

        self.source_states = self.config.get("source_states", {
            "hf": True, "reddit": True, "devto": True, "trending": True,
        })

        self.toggle_hf = QPushButton("✓  HuggingFace")
        self.toggle_reddit = QPushButton("✓  Reddit")
        self.toggle_devto = QPushButton("✓  Dev.to")
        self.toggle_trending = QPushButton("✓  GitHub Trending")

        for btn, key in [
            (self.toggle_hf, "hf"),
            (self.toggle_reddit, "reddit"),
            (self.toggle_devto, "devto"),
            (self.toggle_trending, "trending"),
        ]:
            is_on = self.source_states.get(key, True)
            btn.setObjectName("toggle_on" if is_on else "toggle_off")
            prefix = "✓  " if is_on else "✗  "
            label = key.replace("hf", "HuggingFace").replace("devto", "Dev.to")
            if key == "trending":
                label = "GitHub Trending"
            elif key == "reddit":
                label = "Reddit"
            btn.setText(prefix + label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, b=btn, k=key: self.toggle_source(b, k))
            sidebar_layout.addWidget(btn)
            sidebar_layout.addSpacing(4)

        sidebar_layout.addSpacing(16)

        # Schedule time
        sched_lbl = QLabel("SCHEDULE TIME")
        sched_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(sched_lbl)
        sidebar_layout.addSpacing(8)

        self.schedule_time = QTimeEdit()
        sched_str = self.config.get("schedule_time", "08:00")
        parts = sched_str.split(":")
        from PyQt6.QtCore import QTime
        self.schedule_time.setTime(QTime(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0))
        self.schedule_time.setDisplayFormat("HH:mm")
        sidebar_layout.addWidget(self.schedule_time)

        sidebar_layout.addStretch()

        send_btn = QPushButton("SEND DIGEST NOW")
        send_btn.setObjectName("primary")
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self.send_digest_now)
        sidebar_layout.addWidget(send_btn)

        sidebar_layout.addSpacing(8)

        save_btn = QPushButton("SAVE CONFIG")
        save_btn.setObjectName("ghost")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save)
        sidebar_layout.addWidget(save_btn)

        layout.addWidget(sidebar)

        # ── Main Panel ───────────────────────────────────────
        main = QWidget()
        main.setObjectName("main")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(32, 36, 32, 28)
        main_layout.setSpacing(0)

        # Tab bar
        tab_row = QHBoxLayout()
        self.tab_repos = QPushButton("REPOS")
        self.tab_repos.setObjectName("tab_active")
        self.tab_repos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_repos.clicked.connect(lambda: self.switch_tab(0))

        self.tab_history = QPushButton("HISTORY")
        self.tab_history.setObjectName("tab")
        self.tab_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_history.clicked.connect(lambda: self.switch_tab(1))

        self.tab_settings = QPushButton("SETTINGS")
        self.tab_settings.setObjectName("tab")
        self.tab_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_settings.clicked.connect(lambda: self.switch_tab(2))

        tab_row.addWidget(self.tab_repos)
        tab_row.addWidget(self.tab_history)
        tab_row.addWidget(self.tab_settings)
        tab_row.addStretch()
        main_layout.addLayout(tab_row)
        main_layout.addSpacing(20)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # ── Page 0: Repos ──
        repos_page = QWidget()
        repos_layout = QVBoxLayout(repos_page)
        repos_layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        fetch_title = QLabel("AVAILABLE REPOS")
        fetch_title.setObjectName("section_title")
        top_row.addWidget(fetch_title)
        top_row.addStretch()
        add_btn = QPushButton("+ ADD SELECTED")
        add_btn.setObjectName("primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_selected)
        top_row.addWidget(add_btn)
        repos_layout.addLayout(top_row)
        repos_layout.addSpacing(16)

        self.repo_list = QListWidget()
        self.repo_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.repo_list.setMinimumHeight(200)
        repos_layout.addWidget(self.repo_list)

        repos_layout.addSpacing(24)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        repos_layout.addWidget(divider)
        repos_layout.addSpacing(20)

        bottom_row = QHBoxLayout()
        monitored_lbl = QLabel("MONITORED REPOS")
        monitored_lbl.setObjectName("section_title")
        bottom_row.addWidget(monitored_lbl)
        bottom_row.addStretch()
        remove_btn = QPushButton("REMOVE SELECTED")
        remove_btn.setObjectName("danger")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self.remove_selected)
        bottom_row.addWidget(remove_btn)
        repos_layout.addLayout(bottom_row)
        repos_layout.addSpacing(16)

        self.monitored_list = QListWidget()
        self.monitored_list.setMinimumHeight(140)
        repos_layout.addWidget(self.monitored_list)
        self.refresh_monitored()

        self.stack.addWidget(repos_page)

        # ── Page 1: History ──
        history_page = QWidget()
        history_layout = QVBoxLayout(history_page)
        history_layout.setContentsMargins(0, 0, 0, 0)

        history_top = QHBoxLayout()
        history_lbl = QLabel("PAST DIGESTS")
        history_lbl.setObjectName("section_title")
        history_top.addWidget(history_lbl)
        history_top.addStretch()

        # Search box
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search digests...")
        self.history_search.setFixedWidth(200)
        self.history_search.textChanged.connect(self._filter_history)
        history_top.addWidget(self.history_search)

        # Export button
        export_btn = QPushButton("EXPORT")
        export_btn.setObjectName("ghost")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_history)
        history_top.addWidget(export_btn)

        history_layout.addLayout(history_top)
        history_layout.addSpacing(16)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(160)
        self.history_list.currentRowChanged.connect(self.show_digest)
        history_layout.addWidget(self.history_list)

        history_layout.addSpacing(16)

        self.digest_view = QTextEdit()
        self.digest_view.setReadOnly(True)
        self.digest_view.setPlaceholderText("Select a digest to view...")
        history_layout.addWidget(self.digest_view)

        self.stack.addWidget(history_page)

        # ── Page 2: Settings ──
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(0, 0, 0, 0)

        # Subreddits
        sub_lbl = QLabel("SUBREDDITS (comma-separated)")
        sub_lbl.setObjectName("section_title")
        settings_layout.addWidget(sub_lbl)
        settings_layout.addSpacing(4)
        self.subreddits_input = QLineEdit()
        self.subreddits_input.setText(", ".join(self.config.get("subreddits", ["MachineLearning", "artificial", "learnpython"])))
        settings_layout.addWidget(self.subreddits_input)
        settings_layout.addSpacing(16)

        # Dev.to tags
        tags_lbl = QLabel("DEV.TO TAGS (comma-separated)")
        tags_lbl.setObjectName("section_title")
        settings_layout.addWidget(tags_lbl)
        settings_layout.addSpacing(4)
        self.devto_tags_input = QLineEdit()
        self.devto_tags_input.setText(", ".join(self.config.get("devto_tags", ["python", "ai", "machinelearning"])))
        settings_layout.addWidget(self.devto_tags_input)
        settings_layout.addSpacing(16)

        # Trending languages
        lang_lbl = QLabel("TRENDING LANGUAGES (comma-separated)")
        lang_lbl.setObjectName("section_title")
        settings_layout.addWidget(lang_lbl)
        settings_layout.addSpacing(4)
        self.trending_langs_input = QLineEdit()
        self.trending_langs_input.setText(", ".join(self.config.get("trending_languages", ["python"])))
        settings_layout.addWidget(self.trending_langs_input)
        settings_layout.addSpacing(16)

        # LLM Provider
        llm_lbl = QLabel("LLM PROVIDER")
        llm_lbl.setObjectName("section_title")
        settings_layout.addWidget(llm_lbl)
        settings_layout.addSpacing(4)
        self.llm_provider_input = QLineEdit()
        self.llm_provider_input.setPlaceholderText("groq")
        self.llm_provider_input.setText(self.config.get("llm_provider", "groq"))
        settings_layout.addWidget(self.llm_provider_input)
        settings_layout.addSpacing(8)

        llm_model_lbl = QLabel("LLM MODEL")
        llm_model_lbl.setObjectName("section_title")
        settings_layout.addWidget(llm_model_lbl)
        settings_layout.addSpacing(4)
        self.llm_model_input = QLineEdit()
        self.llm_model_input.setPlaceholderText("llama-3.3-70b-versatile")
        self.llm_model_input.setText(self.config.get("llm_model", "llama-3.3-70b-versatile"))
        settings_layout.addWidget(self.llm_model_input)
        settings_layout.addSpacing(16)

        # Notification channels
        notif_lbl = QLabel("NOTIFICATION CHANNELS")
        notif_lbl.setObjectName("section_title")
        settings_layout.addWidget(notif_lbl)
        settings_layout.addSpacing(8)

        channels = self.config.get("notification_channels", ["email"])
        self.channel_checks = {}
        for ch in ["email", "slack", "discord"]:
            cb = QCheckBox(ch.capitalize())
            cb.setChecked(ch in channels)
            cb.setStyleSheet("color: #c9d1d9; font-size: 13px;")
            settings_layout.addWidget(cb)
            self.channel_checks[ch] = cb

        settings_layout.addSpacing(12)

        # Webhook URLs
        webhook_lbl = QLabel("SLACK WEBHOOK URL")
        webhook_lbl.setObjectName("section_title")
        settings_layout.addWidget(webhook_lbl)
        settings_layout.addSpacing(4)
        self.slack_webhook_input = QLineEdit()
        self.slack_webhook_input.setText(self.config.get("slack_webhook_url", ""))
        self.slack_webhook_input.setPlaceholderText("https://hooks.slack.com/...")
        settings_layout.addWidget(self.slack_webhook_input)
        settings_layout.addSpacing(8)

        discord_lbl = QLabel("DISCORD WEBHOOK URL")
        discord_lbl.setObjectName("section_title")
        settings_layout.addWidget(discord_lbl)
        settings_layout.addSpacing(4)
        self.discord_webhook_input = QLineEdit()
        self.discord_webhook_input.setText(self.config.get("discord_webhook_url", ""))
        self.discord_webhook_input.setPlaceholderText("https://discord.com/api/webhooks/...")
        settings_layout.addWidget(self.discord_webhook_input)

        settings_layout.addStretch()
        self.stack.addWidget(settings_page)

        self.refresh_history()
        layout.addWidget(main)

    # ── Tab switching ──────────────────────────────────────

    def switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        tabs = [self.tab_repos, self.tab_history, self.tab_settings]
        for i, tab in enumerate(tabs):
            tab.setObjectName("tab_active" if i == index else "tab")
            tab.setStyle(tab.style())

    # ── Source toggles ─────────────────────────────────────

    def toggle_source(self, btn: QPushButton, key: str):
        self.source_states[key] = not self.source_states[key]
        if self.source_states[key]:
            btn.setObjectName("toggle_on")
            btn.setText("✓  " + btn.text().replace("✗  ", ""))
        else:
            btn.setObjectName("toggle_off")
            btn.setText("✗  " + btn.text().replace("✓  ", ""))
        btn.setStyle(btn.style())

    # ── History ────────────────────────────────────────────

    def refresh_history(self):
        self.history = load_history()
        self._populate_history_list(self.history)

    def _populate_history_list(self, entries: list[dict]):
        self.history_list.clear()
        for entry in entries:
            self.history_list.addItem(f"  {entry['timestamp']}")

    def _filter_history(self, query: str):
        query = query.lower().strip()
        if not query:
            self._populate_history_list(self.history)
            return
        filtered = [
            e for e in self.history
            if query in e.get("timestamp", "").lower() or query in e.get("digest", "").lower()
        ]
        self._populate_history_list(filtered)

    def show_digest(self, index: int):
        if 0 <= index < len(self.history):
            self.digest_view.setText(self.history[index]["digest"])

    def _export_history(self):
        if not self.history:
            self._set_status("No history to export.", "err")
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "orbit_history.md", "Markdown (*.md);;HTML (*.html);;JSON (*.json)"
        )
        if not path:
            return

        try:
            if path.endswith(".json"):
                with open(path, "w") as f:
                    json.dump(self.history, f, indent=2)
            elif path.endswith(".html"):
                import mistune
                md = mistune.create_markdown()
                html_parts = []
                for entry in self.history:
                    html_parts.append(f"<h2>{entry['timestamp']}</h2>")
                    html_parts.append(md(entry["digest"]))
                    html_parts.append("<hr>")
                with open(path, "w") as f:
                    f.write(f"<html><body style='font-family:sans-serif;max-width:700px;margin:auto;'>"
                            + "\n".join(html_parts) + "</body></html>")
            else:  # .md
                with open(path, "w") as f:
                    for entry in self.history:
                        f.write(f"## {entry['timestamp']}\n\n{entry['digest']}\n\n---\n\n")
            self._set_status(f"Exported to {path}", "ok")
        except Exception as e:
            self._set_status(f"Export failed: {e}", "err")

    # ── Repo management ───────────────────────────────────

    def fetch_repos(self):
        username = self.username_input.text().strip()
        if not username:
            self._set_status("Enter a username first.", "err")
            return
        self._set_status(f"Fetching {username}...")
        self.repo_list.clear()
        self._repo_thread = RepoFetchThread(username)
        self._repo_thread.result.connect(self.on_fetched)
        self._repo_thread.error.connect(self.on_error)
        self._repo_thread.start()

    def on_fetched(self, repos: list):
        self.repo_list.clear()
        for r in repos:
            desc = r.get("description") or "No description"
            item = QListWidgetItem(f"  {r['name']}   —   {desc}")
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.repo_list.addItem(item)
        self._set_status(f"{len(repos)} repos found", "ok")

    def on_error(self, err: str):
        self._set_status(f"Error: {err}", "err")

    def add_selected(self):
        selected = self.repo_list.selectedItems()
        if not selected:
            return
        existing = {r["url"] for r in self.config["repos"]}
        for item in selected:
            r = item.data(Qt.ItemDataRole.UserRole)
            if r["html_url"] not in existing:
                self.config["repos"].append({
                    "name": r["name"],
                    "owner": r["owner"]["login"],
                    "url": r["html_url"],
                    "description": r.get("description") or "",
                })
        self.refresh_monitored()

    def refresh_monitored(self):
        self.monitored_list.clear()
        for r in self.config["repos"]:
            self.monitored_list.addItem(f"  {r['owner']} / {r['name']}   —   {r.get('description', '')}")

    def remove_selected(self):
        indices = sorted(
            [self.monitored_list.row(i) for i in self.monitored_list.selectedItems()],
            reverse=True,
        )
        for i in indices:
            self.config["repos"].pop(i)
        self.refresh_monitored()

    # ── Save config ────────────────────────────────────────

    def save(self):
        self.config["email"] = self.email_input.text().strip()
        self.config["source_states"] = self.source_states
        self.config["schedule_time"] = self.schedule_time.time().toString("HH:mm")

        # Settings page values
        def _parse_csv(text: str) -> list[str]:
            return [s.strip() for s in text.split(",") if s.strip()]

        self.config["subreddits"] = _parse_csv(self.subreddits_input.text())
        self.config["devto_tags"] = _parse_csv(self.devto_tags_input.text())
        self.config["trending_languages"] = _parse_csv(self.trending_langs_input.text())
        self.config["llm_provider"] = self.llm_provider_input.text().strip() or "groq"
        self.config["llm_model"] = self.llm_model_input.text().strip() or "llama-3.3-70b-versatile"

        channels = [ch for ch, cb in self.channel_checks.items() if cb.isChecked()]
        self.config["notification_channels"] = channels if channels else ["email"]
        self.config["slack_webhook_url"] = self.slack_webhook_input.text().strip()
        self.config["discord_webhook_url"] = self.discord_webhook_input.text().strip()

        # Clear cached LLM client so new provider/model takes effect
        from Backend.digest_generator import _get_llm_client
        _get_llm_client.cache_clear()

        self._save_config()
        self._set_status("Config saved ✓", "ok")

    # ── Digest flow ────────────────────────────────────────

    def send_digest_now(self):
        email = self.email_input.text().strip()
        if not email:
            self._set_status("No email set.", "err")
            return
        self._set_status("Generating digest...")
        self._digest_thread = DigestThread(self.source_states)
        self._digest_thread.done.connect(self._on_digest_generated)
        self._digest_thread.error.connect(lambda err: self._set_status(f"Error: {err}", "err"))
        self._digest_thread.start()

    def _on_digest_generated(self, digest_text: str, source_status: dict[str, str]):
        self._pending_digest = digest_text

        # Show preview dialog
        preview = PreviewDialog(digest_text, source_status, self)
        if preview.exec() == QDialog.DialogCode.Accepted and preview.confirmed:
            self._set_status("Sending digest...")
            self._send_thread = SendThread(self.email_input.text().strip(), digest_text)
            self._send_thread.done.connect(self._on_digest_sent)
            self._send_thread.error.connect(lambda err: self._set_status(f"Send error: {err}", "err"))
            self._send_thread.start()
        else:
            self._set_status("Digest cancelled.")

    def _on_digest_sent(self, results: dict[str, bool]):
        parts = []
        for channel, ok in results.items():
            icon = "✓" if ok else "✗"
            parts.append(f"{icon} {channel}")
        self._set_status("Sent: " + " · ".join(parts), "ok" if all(results.values()) else "err")

        # Save to history
        if self._pending_digest:
            save_to_history(self._pending_digest)
            self._pending_digest = None
            self.refresh_history()

    # ── Status helper ─────────────────────────────────────

    def _set_status(self, text: str, kind: str = ""):
        """Set status label text and style."""
        self.status_lbl.setText(text)
        if kind == "ok":
            self.status_lbl.setObjectName("status_ok")
        elif kind == "err":
            self.status_lbl.setObjectName("status_err")
        else:
            self.status_lbl.setObjectName("status")
        self.status_lbl.setStyle(self.status_lbl.style())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
