import platform

from .client import ClientService
from .oci_bucket import BucketService
from .oci_select_ai import SelectAIService
from .oci_select_ai_rag import SelectAIRAGService
from .oci_document_understanding import DocumentUnderstandingService
from .oci_speech import SpeechService
from .oci_document_multimodal import DocumentMultimodalService
from .oci_generative_ai_chat import GenerativeAIService
from .open_anonymizer_engine import AnalyzerEngineService

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    from .oci_speech_realtime import start_realtime_session, stop_realtime_session

__all__ = [
    "ClientService",
    "BucketService",
    "SelectAIService",
    "SelectAIRAGService",
    "DocumentUnderstandingService",
    "SpeechService",
    "DocumentMultimodalService",
    "GenerativeAIService",
    "AnalyzerEngineService",
]

if IS_WINDOWS:
    __all__ += ["start_realtime_session", "stop_realtime_session"]
