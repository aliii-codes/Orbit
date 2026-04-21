"""Tests for config module."""

import json

import pytest

from Backend.config import load_config, save_config, load_history, save_to_history, ensure_config


class TestConfig:
    def test_load_config_returns_defaults_when_missing(self, tmp_path, monkeypatch):
        import Backend.config as cfg
        monkeypatch.setattr(cfg, "CONFIG_PATH", str(tmp_path / "nonexistent.json"))
        result = load_config()
        assert result["email"] == ""
        assert result["repos"] == []
        assert "source_states" in result

    def test_save_and_load_config(self, tmp_path, monkeypatch):
        import Backend.config as cfg
        path = str(tmp_path / "test_config.json")
        monkeypatch.setattr(cfg, "CONFIG_PATH", path)

        test_config = {"email": "test@test.com", "repos": [{"name": "repo1", "owner": "user", "url": "http://x", "description": ""}]}
        save_config(test_config)

        loaded = load_config()
        assert loaded["email"] == "test@test.com"
        assert len(loaded["repos"]) == 1

    def test_load_config_merges_new_defaults(self, tmp_path, monkeypatch):
        import Backend.config as cfg
        path = str(tmp_path / "old_config.json")

        # Write a config missing new keys
        old_config = {"email": "test@test.com", "repos": []}
        with open(path, "w") as f:
            json.dump(old_config, f)

        monkeypatch.setattr(cfg, "CONFIG_PATH", path)
        result = load_config()
        # Should have old values
        assert result["email"] == "test@test.com"
        # And new default keys merged in
        assert "source_states" in result
        assert "schedule_time" in result
        assert "subreddits" in result


class TestHistory:
    def test_save_and_load_history(self, tmp_path, monkeypatch):
        import Backend.config as cfg
        path = str(tmp_path / "test_history.json")
        monkeypatch.setattr(cfg, "HISTORY_PATH", path)

        save_to_history("Test digest content")
        history = load_history()
        assert len(history) == 1
        assert history[0]["digest"] == "Test digest content"

    def test_history_max_30_entries(self, tmp_path, monkeypatch):
        import Backend.config as cfg
        path = str(tmp_path / "test_history.json")
        monkeypatch.setattr(cfg, "HISTORY_PATH", path)

        for i in range(35):
            save_to_history(f"Digest {i}")

        history = load_history()
        assert len(history) == 30
