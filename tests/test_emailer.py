"""Tests for emailer module."""

import pytest
from unittest.mock import patch, MagicMock

from Backend.emailer import send_digest, send_digest_email, _markdown_to_html


class TestMarkdownToHtml:
    def test_headers(self):
        result = _markdown_to_html("# Hello")
        assert "<h1" in result
        assert "Hello" in result

    def test_bold(self):
        result = _markdown_to_html("**bold text**")
        assert "<strong" in result
        assert "bold text" in result

    def test_links(self):
        result = _markdown_to_html("[click](https://example.com)")
        assert "https://example.com" in result
        assert "click" in result


class TestSendDigestEmail:
    def test_missing_credentials_returns_false(self):
        with patch("Backend.emailer.GMAIL_USER", ""), \
             patch("Backend.emailer.GMAIL_APP_PASSWORD", ""):
            result = send_digest_email("test@test.com", "Hello")
            assert result is False

    def test_send_success(self):
        with patch("Backend.emailer.GMAIL_USER", "test@gmail.com"), \
             patch("Backend.emailer.GMAIL_APP_PASSWORD", "password"), \
             patch("Backend.emailer.smtplib.SMTP_SSL") as mock_smtp:

            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = send_digest_email("test@test.com", "Hello digest")
            assert result is True
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()


class TestSendDigest:
    def test_email_channel_only(self, tmp_config_dir):
        with patch("Backend.emailer.send_digest_email", return_value=True) as mock_email:
            result = send_digest("test@test.com", "Hello")
            assert result["email"] is True
            mock_email.assert_called_once()

    def test_slack_channel(self, tmp_config_dir):
        with patch("Backend.emailer.send_digest_email", return_value=True), \
             patch("Backend.emailer.send_digest_slack", return_value=True) as mock_slack:

            # Update config to include slack
            import Backend.config as cfg
            cfg_data = cfg.load_config()
            cfg_data["notification_channels"] = ["email", "slack"]
            cfg.save_config(cfg_data)

            result = send_digest("test@test.com", "Hello")
            assert result["email"] is True
            assert result["slack"] is True
