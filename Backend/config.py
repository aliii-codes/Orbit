import json
import os
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Frontend", "Data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

DEFAULT_CONFIG = {
    "email": "",
    "repos": [],
    "source_states": {
        "hf": True,
        "reddit": True,
        "devto": True,
        "trending": True,
    },
    "schedule_time": "08:00",
    "subreddits": ["MachineLearning", "artificial", "learnpython"],
    "devto_tags": ["python", "ai", "machinelearning"],
    "trending_languages": ["python"],
    "llm_provider": "groq",
    "llm_model": "llama-3.3-70b-versatile",
    "notification_channels": ["email"],
    "slack_webhook_url": "",
    "discord_webhook_url": "",
}


def load_config() -> dict:
    """Load config from disk, creating with defaults if missing."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
            # Merge in any new default keys that don't exist yet
            for key, value in DEFAULT_CONFIG.items():
                if key not in cfg:
                    cfg[key] = value
            return cfg
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load config: %s", e)
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    """Persist config to disk."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
    except OSError as e:
        logger.error("Failed to save config: %s", e)


def ensure_config() -> None:
    """Create config file with defaults if it doesn't exist."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        logger.info("Created default config at %s", CONFIG_PATH)


def load_history() -> list[dict]:
    """Load digest history from disk."""
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load history: %s", e)
    return []


def save_to_history(digest_text: str) -> None:
    """Append a digest to history (max 30 entries)."""
    from datetime import datetime

    history = load_history()
    history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "digest": digest_text,
    })
    history = history[:30]
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    try:
        with open(HISTORY_PATH, "w") as f:
            json.dump(history, f, indent=4)
    except OSError as e:
        logger.error("Failed to save history: %s", e)
