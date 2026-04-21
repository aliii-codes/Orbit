"""Tests for HuggingFace fetcher."""

import json

import pytest
import responses

from Backend.hf_fetcher import HF_PAPERS_API, HF_MODELS_API, fetch_hf_data


class TestFetchHFData:
    @responses.activate
    def test_fetch_papers_success(self, sample_hf_papers):
        responses.add(
            responses.GET,
            HF_PAPERS_API,
            json=sample_hf_papers,
            status=200,
        )
        responses.add(
            responses.GET,
            HF_MODELS_API,
            json=[],
            status=200,
        )

        result = fetch_hf_data()
        assert len(result["papers"]) == 2
        assert result["papers"][0]["title"] == "Test Paper 1"
        assert "2301.00001" in result["papers"][0]["url"]

    @responses.activate
    def test_fetch_models_success(self, sample_hf_models):
        responses.add(
            responses.GET,
            HF_PAPERS_API,
            json=[],
            status=200,
        )
        responses.add(
            responses.GET,
            HF_MODELS_API,
            json=sample_hf_models,
            status=200,
        )

        result = fetch_hf_data()
        assert len(result["models"]) == 2
        assert result["models"][0]["id"] == "org/model1"
        assert result["models"][0]["downloads"] == 1000

    @responses.activate
    def test_fetch_papers_error_returns_empty(self):
        responses.add(
            responses.GET,
            HF_PAPERS_API,
            status=500,
        )
        responses.add(
            responses.GET,
            HF_MODELS_API,
            json=[],
            status=200,
        )

        result = fetch_hf_data()
        assert result["papers"] == []
        assert result["models"] == []

    @responses.activate
    def test_fetch_limits_to_5(self):
        many_papers = [{"paper": {"id": f"p{i}", "title": f"Paper {i}"}, "numComments": i} for i in range(10)]
        responses.add(
            responses.GET,
            HF_PAPERS_API,
            json=many_papers,
            status=200,
        )
        responses.add(
            responses.GET,
            HF_MODELS_API,
            json=[],
            status=200,
        )

        result = fetch_hf_data()
        assert len(result["papers"]) == 5
