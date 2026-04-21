"""Source plugin system for Orbit.

Each source plugin implements the SourcePlugin protocol and is auto-discovered
from this directory. To add a new source, create a .py file here with a class
that inherits from SourcePlugin and register it in SOURCES.
"""

from Backend.sources.base import SourcePlugin
from Backend.sources.github_source import GitHubSource
from Backend.sources.hf_source import HuggingFaceSource
from Backend.sources.reddit_source import RedditSource
from Backend.sources.devto_source import DevToSource
from Backend.sources.gh_trending_source import GHTrendingSource

# Registry of all built-in sources
SOURCES: dict[str, SourcePlugin] = {
    "github": GitHubSource(),
    "hf": HuggingFaceSource(),
    "reddit": RedditSource(),
    "devto": DevToSource(),
    "trending": GHTrendingSource(),
}


def get_enabled_sources(source_states: dict[str, bool]) -> list[SourcePlugin]:
    """Return source plugins that are enabled in the given state dict."""
    return [s for key, s in SOURCES.items() if source_states.get(key, True)]


__all__ = ["SourcePlugin", "SOURCES", "get_enabled_sources"]
