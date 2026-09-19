"""Shared QThread workers for background tasks."""

import asyncio
import logging

from PySide6.QtCore import QThread, Signal

from celebi.model_fetcher import fetch_models

logger = logging.getLogger(__name__)


class ModelFetchWorker(QThread):
    """Background thread to fetch models from provider API."""

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, provider: str, api_key: str, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.api_key = api_key
        self._loop: asyncio.AbstractEventLoop | None = None
        self.setDaemon(True)

    def run(self):
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            models = self._loop.run_until_complete(
                fetch_models(self.provider, self.api_key)
            )
            self.finished.emit(models)
        except Exception as e:
            logger.warning("Model fetch failed: %s", e)
            self.error.emit(str(e))
        finally:
            if self._loop and not self._loop.is_closed():
                self._loop.close()
            self._loop = None

    def cancel(self):
        """Cancel any pending async work."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
