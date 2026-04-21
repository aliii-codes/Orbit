"""Shared test fixtures for Orbit."""

import json
import os
import tempfile

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Provide a temporary config directory and patch CONFIG_PATH/HISTORY_PATH."""
    config_file = tmp_path / "config.json"
    history_file = tmp_path / "history.json"

    default_config = {
        "email": "test@test.com",
        "repos": [],
        "source_states": {"hf": True, "reddit": True, "devto": True, "trending": True},
        "schedule_time": "08:00",
        "subreddits": ["MachineLearning"],
        "devto_tags": ["python"],
        "trending_languages": ["python"],
        "llm_provider": "groq",
        "llm_model": "llama-3.3-70b-versatile",
        "notification_channels": ["email"],
        "slack_webhook_url": "",
        "discord_webhook_url": "",
    }
    config_file.write_text(json.dumps(default_config, indent=2))
    history_file.write_text("[]")

    # Monkey-patch the config module paths
    import Backend.config as cfg_mod
    original_config_path = cfg_mod.CONFIG_PATH
    original_history_path = cfg_mod.HISTORY_PATH

    cfg_mod.CONFIG_PATH = str(config_file)
    cfg_mod.HISTORY_PATH = str(history_file)

    yield tmp_path

    # Restore
    cfg_mod.CONFIG_PATH = original_config_path
    cfg_mod.HISTORY_PATH = original_history_path


@pytest.fixture
def sample_hf_papers():
    return [
        {
            "paper": {"id": "2301.00001", "title": "Test Paper 1"},
            "numComments": 5,
        },
        {
            "paper": {"id": "2301.00002", "title": "Test Paper 2"},
            "numComments": 3,
        },
    ]


@pytest.fixture
def sample_hf_models():
    return [
        {"id": "org/model1", "downloads": 1000, "likes": 50},
        {"id": "org/model2", "downloads": 500, "likes": 20},
    ]


@pytest.fixture
def sample_reddit_data():
    return {
        "data": {
            "children": [
                {"data": {"title": "ML Post 1", "permalink": "/r/MachineLearning/comments/abc", "ups": 100, "num_comments": 20}},
                {"data": {"title": "ML Post 2", "permalink": "/r/MachineLearning/comments/def", "ups": 50, "num_comments": 10}},
            ]
        }
    }


@pytest.fixture
def sample_devto_data():
    return [
        {"title": "Python Tips", "url": "https://dev.to/test/python-tips", "user": {"name": "Author1"}, "positive_reactions_count": 30, "tag": "python"},
    ]


@pytest.fixture
def sample_github_repo_data():
    return [
        {
            "repo": "test/repo",
            "url": "https://github.com/test/repo",
            "commits": [{"sha": "abc1234", "message": "Fix bug", "author": "Dev", "date": "2025-01-01 10:00"}],
            "issues": [{"title": "Bug report", "state": "open", "url": "https://github.com/test/repo/issues/1", "created_at": "2025-01-01 09:00"}],
            "pulls": [],
        }
    ]
