"""Tests for Dev.to fetcher."""

import pytest
import responses

from Backend.devto_fetcher import DEVTO_API, fetch_devto_data


class TestFetchDevToData:
    @responses.activate
    def test_fetch_success(self, sample_devto_data):
        responses.add(
            responses.GET,
            DEVTO_API,
            json=sample_devto_data,
            status=200,
        )

        result = fetch_devto_data(tags=["python"])
        assert len(result) == 1
        assert result[0]["title"] == "Python Tips"
        assert result[0]["author"] == "Author1"

    @responses.activate
    def test_fetch_error_returns_empty(self):
        responses.add(
            responses.GET,
            DEVTO_API,
            status=500,
        )

        result = fetch_devto_data(tags=["python"])
        assert result == []
