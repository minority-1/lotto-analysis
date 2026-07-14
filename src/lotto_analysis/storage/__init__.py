"""File storage adapters."""

from lotto_analysis.storage.collection_history import CollectionHistoryStore
from lotto_analysis.storage.raw_json import RawDataConflictError, RawJsonStore

__all__ = ["CollectionHistoryStore", "RawDataConflictError", "RawJsonStore"]
