"""Tests for digest generator."""

import pytest
from unittest.mock import patch, MagicMock

from Backend.digest_generator import generate_digest


class TestGenerateDigest:
    def test_empty_data_returns_fallback(self):
        result = generate_digest()
        assert result == "No activity found in the last 24 hours."

    def test_github_data_formats_correctly(self, sample_github_repo_data):
        with patch("Backend.digest_generator._call_llm") as mock_llm:
            mock_llm.return_value = "Mock digest output"
            result = generate_digest(digest_data=sample_github_repo_data)
            assert result == "Mock digest output"
            # Verify the prompt contains repo data
            call_args = mock_llm.call_args[0][0]
            assert "test/repo" in call_args
            assert "Fix bug" in call_args

    def test_hf_data_formats_correctly(self):
        hf = {"papers": [{"title": "Test Paper", "url": "https://huggingface.co/papers/123"}], "models": []}
        with patch("Backend.digest_generator._call_llm") as mock_llm:
            mock_llm.return_value = "Mock digest"
            result = generate_digest(hf_data=hf)
            assert "Test Paper" in mock_llm.call_args[0][0]

    def test_llm_failure_returns_error_message(self, sample_github_repo_data):
        with patch("Backend.digest_generator._call_llm") as mock_llm:
            mock_llm.side_effect = Exception("API down")
            result = generate_digest(digest_data=sample_github_repo_data)
            assert "Digest generation failed" in result
            assert "test/repo" in result  # Raw data still included
