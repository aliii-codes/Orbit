import sys
import json
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QFrame, QTextEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "data", "history.json")
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
"""


def save_to_history(digest_text: str):
    history = []
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r") as f:
            history = json.load(f)
    history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "digest": digest_text
    })
    history = history[:30]
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)


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
    done = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, email, source_states):
        super().__init__()
        self.email = email
        self.source_states = source_states

    def run(self):
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Backend"))
            from github_fetcher import fetch_repo_data
            from digest_generator import generate_digest
            from emailer import send_digest
            from hf_fetcher import fetch_hf_data
            from reddit_fetcher import fetch_reddit_data
            from devto_fetcher import fetch_devto_data
            from gh_trending_fetcher import fetch_gh_trending

            data = fetch_repo_data()
            hf = fetch_hf_data() if self.source_states["hf"] else None
            reddit = fetch_reddit_data() if self.source_states["reddit"] else None
            devto = fetch_devto_data() if self.source_states["devto"] else None
            trending = fetch_gh_trending() if self.source_states["trending"] else None

            digest = generate_digest(data, hf_data=hf, reddit_data=reddit, devto_data=devto, gh_trending=trending)
            send_digest(self.email, digest)
            self.done.emit("Digest sent ✓", digest)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbit — GitHub Agent")
        self.setMinimumSize(860, 620)
        self.resize(960, 660)
        self.config = self.load_config()
        self.history = self.load_history()
        self.setStyleSheet(STYLE)
        self.build_ui()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {"email": "", "repos": []}

    def load_history(self):
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        return []

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

        email_lbl = QLabel("RECIPIENT EMAIL")
        email_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(email_lbl)
        sidebar_layout.addSpacing(8)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@gmail.com")
        self.email_input.setText(self.config.get("email", ""))
        sidebar_layout.addWidget(self.email_input)

        sidebar_layout.addSpacing(24)

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

        self.source_states = {
            "hf": True, "reddit": True, "devto": True, "trending": True
        }

        self.toggle_hf = QPushButton("✓  HuggingFace")
        self.toggle_reddit = QPushButton("✓  Reddit")
        self.toggle_devto = QPushButton("✓  Dev.to")
        self.toggle_trending = QPushButton("✓  GitHub Trending")

        for btn, key in [
            (self.toggle_hf, "hf"),
            (self.toggle_reddit, "reddit"),
            (self.toggle_devto, "devto"),
            (self.toggle_trending, "trending")
        ]:
            btn.setObjectName("toggle_on")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, b=btn, k=key: self.toggle_source(b, k))
            sidebar_layout.addWidget(btn)
            sidebar_layout.addSpacing(4)

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

        tab_row.addWidget(self.tab_repos)
        tab_row.addWidget(self.tab_history)
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

        self.refresh_history()
        layout.addWidget(main)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.tab_repos.setObjectName("tab_active")
            self.tab_history.setObjectName("tab")
        else:
            self.tab_repos.setObjectName("tab")
            self.tab_history.setObjectName("tab_active")
        self.tab_repos.setStyle(self.tab_repos.style())
        self.tab_history.setStyle(self.tab_history.style())

    def toggle_source(self, btn, key):
        self.source_states[key] = not self.source_states[key]
        if self.source_states[key]:
            btn.setObjectName("toggle_on")
            btn.setText("✓  " + btn.text().replace("✗  ", ""))
        else:
            btn.setObjectName("toggle_off")
            btn.setText("✗  " + btn.text().replace("✓  ", ""))
        btn.setStyle(btn.style())

    def refresh_history(self):
        self.history = self.load_history()
        self.history_list.clear()
        for entry in self.history:
            self.history_list.addItem(f"  {entry['timestamp']}")

    def show_digest(self, index):
        if 0 <= index < len(self.history):
            self.digest_view.setText(self.history[index]["digest"])

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
        self.digest_thread = DigestThread(email, self.source_states)
        self.digest_thread.done.connect(self.on_digest_done)
        self.digest_thread.error.connect(lambda err: self.status_lbl.setText(f"Error: {err}"))
        self.digest_thread.start()

    def on_digest_done(self, msg, digest_text):
        self.status_lbl.setText(msg)
        save_to_history(digest_text)
        self.refresh_history()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())