"""Base class for Orbit source plugins."""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SourcePlugin(ABC):
    """Protocol for a data source plugin."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the source (e.g., 'HuggingFace')."""
        ...

    @property
    @abstractmethod
    def key(self) -> str:
        """Short key used in config/source_states (e.g., 'hf')."""
        ...

    @abstractmethod
    def fetch(self) -> object:
        """Fetch data from this source. Returns source-specific data structure."""
        ...

    def format_raw(self, data: object) -> str:
        """Format fetched data into raw text for the LLM prompt.

        Override this to customize how data appears in the digest prompt.
        Default implementation returns empty string (data is ignored).
        """
        return ""

    def __repr__(self) -> str:
        return f"<SourcePlugin key={self.key} name={self.name}>"
