import time
import threading
from typing import Dict, Optional, List
from app.retrieval.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.retrieval.session_store")

class SessionStore:
    """
    In-memory registry of query trace sessions with simple TTL cleanup.
    """
    def __init__(self, retention_seconds: int = 86400):  # Default 24 hours retention
        self._store: Dict[str, Tuple[QueryTrace, float]] = {}
        self.retention_seconds = retention_seconds
        self._lock = threading.Lock()

    def save_session(self, trace: QueryTrace) -> None:
        with self._lock:
            self._store[trace.trace_id] = (trace, time.time())
            logger.info(f"Trace session '{trace.trace_id}' saved to SessionStore.")

    def get_session(self, trace_id: str) -> Optional[QueryTrace]:
        with self._lock:
            record = self._store.get(trace_id)
            if record:
                return record[0]
        return None

    def get_recent_sessions(self, limit: int = 20) -> List[QueryTrace]:
        with self._lock:
            records = list(self._store.values())
            # Sort by timestamp descending
            records.sort(key=lambda x: x[1], reverse=True)
            return [rec[0] for rec in records[:limit]]

    def run_cleanup(self) -> None:
        """
        Garbage collect sessions exceeding the expiration TTL.
        """
        now = time.time()
        expired_keys = []
        with self._lock:
            for trace_id, (trace, timestamp) in self._store.items():
                if now - timestamp > self.retention_seconds:
                    expired_keys.append(trace_id)
            for k in expired_keys:
                del self._store[k]
                
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired trace sessions from store.")

from typing import Tuple
# Export singleton session store instance
session_store = SessionStore()
