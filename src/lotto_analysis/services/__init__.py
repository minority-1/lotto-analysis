"""Application services."""

from lotto_analysis.services.analysis_service import AnalysisService
from lotto_analysis.services.collection_service import CollectionService
from lotto_analysis.services.database_service import DatabaseService
from lotto_analysis.services.generation_service import GenerationService
from lotto_analysis.services.processing_service import ProcessingService

__all__ = [
    "AnalysisService",
    "CollectionService",
    "DatabaseService",
    "GenerationService",
    "ProcessingService",
]
