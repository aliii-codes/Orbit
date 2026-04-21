"""Tests for Reddit fetcher."""

import pytest
import responses

from Backend.reddit_fetcher import fetch_reddit_data


class TestFetchRedditData:
    @responses.activate
    def test_fetch_success(self, sample_reddit_data):
        responses.add(
            responses.GET,
            "https://www.reddit.com/r/MachineLearning/hot.json?limit=3",
            json=sample_reddit_data,
            status=200,
        )

        result = fetch_reddit_data(subreddits=["MachineLearning"])
        assert len(result) == 2
        assert result[0]["title"] == "ML Post 1"
        assert result[0]["subreddit"] == "MachineLearning"
        assert result[0]["upvotes"] == 100

    @responses.activate
    def test_fetch_error_returns_empty(self):
        responses.add(
            responses.GET,
            "https://www.reddit.com/r/NonExistent/hot.json?limit=3",
            status=404,
        )

        result = fetch_reddit_data(subreddits=["NonExistent"])
        assert result == []

    @responses.activate
    def test_fetch_multiple_subreddits(self, sample_reddit_data):
        for sub in ["MachineLearning", "artificial"]:
            responses.add(
                responses.GET,
                f"https://www.reddit.com/r/{sub}/hot.json?limit=3",
                json=sample_reddit_data,
                status=200,
            )

        result = fetch_reddit_data(subreddits=["MachineLearning", "artificial"])
        assert len(result) == 4  # 2 per subreddit
