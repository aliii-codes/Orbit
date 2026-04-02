# frontend/GUI.py

import sys
import json
import os
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")
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
"""


class RepoFetchThread(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        try:
            url = GITHUB_API.format(self.username)
            res = requests.get(url, params={"per_page": 100, "sort": "updated"})
            if res.status_code == 200:
                self.result.emit(res.json())
            else:
                self.error.emit(f"GitHub error {res.status_code}")
        except Exception as e:
            self.error.emit(str(e))


class DigestThread(QThread):
    done = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Backend"))
            from github_fetcher import fetch_repo_data
            from digest_generator import generate_digest
            from emailer import send_digest

            data = fetch_repo_data()
            digest = generate_digest(data)
            send_digest(self.email, digest)
            self.done.emit("Digest sent ✓")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digest — GitHub Agent")
        self.setMinimumSize(860, 620)
        self.resize(960, 660)
        self.config = self.load_config()
        self.setStyleSheet(STYLE)
        self.build_ui()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {"email": "", "repos": []}

    def save_config(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)

    def build_ui(self):
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

        brand = QLabel("DIGEST AGENT")
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

        # Username
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

        sidebar_layout.addStretch()

        # Send Digest
        send_btn = QPushButton("SEND DIGEST NOW")
        send_btn.setObjectName("primary")
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self.send_digest_now)
        sidebar_layout.addWidget(send_btn)

        sidebar_layout.addSpacing(8)

        # Save Config
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

        # Available repos
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
        main_layout.addLayout(top_row)

        main_layout.addSpacing(16)

        self.repo_list = QListWidget()
        self.repo_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.repo_list.setMinimumHeight(220)
        main_layout.addWidget(self.repo_list)

        main_layout.addSpacing(28)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(divider)

        main_layout.addSpacing(24)

        # Monitored repos
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
        main_layout.addLayout(bottom_row)

        main_layout.addSpacing(16)

        self.monitored_list = QListWidget()
        self.monitored_list.setMinimumHeight(160)
        main_layout.addWidget(self.monitored_list)
        self.refresh_monitored()

        layout.addWidget(main)

    def fetch_repos(self):
        username = self.username_input.text().strip()
        if not username:
            self.status_lbl.setText("Enter a username first.")
            return
        self.status_lbl.setText(f"Fetching {username}...")
        self.repo_list.clear()
        self.thread = RepoFetchThread(username)
        self.thread.result.connect(self.on_fetched)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_fetched(self, repos):
        self.repo_list.clear()
        for r in repos:
            desc = r.get("description") or "No description"
            item = QListWidgetItem(f"  {r['name']}   —   {desc}")
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.repo_list.addItem(item)
        self.status_lbl.setText(f"{len(repos)} repos found")

    def on_error(self, err):
        self.status_lbl.setText(f"Error: {err}")

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
                    "description": r.get("description") or ""
                })
        self.refresh_monitored()

    def refresh_monitored(self):
        self.monitored_list.clear()
        for r in self.config["repos"]:
            self.monitored_list.addItem(f"  {r['owner']} / {r['name']}   —   {r['description']}")

    def remove_selected(self):
        indices = sorted(
            [self.monitored_list.row(i) for i in self.monitored_list.selectedItems()],
            reverse=True
        )
        for i in indices:
            self.config["repos"].pop(i)
        self.refresh_monitored()

    def save(self):
        self.config["email"] = self.email_input.text().strip()
        self.save_config()
        self.status_lbl.setText("Config saved ✓")

    def send_digest_now(self):
        email = self.email_input.text().strip()
        if not email:
            self.status_lbl.setText("No email set.")
            return
        self.status_lbl.setText("Sending digest...")
        self.digest_thread = DigestThread(email)
        self.digest_thread.done.connect(lambda msg: self.status_lbl.setText(msg))
        self.digest_thread.error.connect(lambda err: self.status_lbl.setText(f"Error: {err}"))
        self.digest_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())