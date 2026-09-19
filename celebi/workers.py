"""Shared QThread workers for background tasks."""

import asyncio
import logging

from PySide6.QtCore import QThread, Signal

from celebi.model_fetcher import fetch_models

logger = logging.getLogger(__name__)


class ModelFetchWorker(QThread):
    """Background thread to fetch models from provider API."""

    # NOTE: must NOT be named `finished` — QThread already defines a
    # no-arg `finished` signal and shadowing it breaks thread cleanup.
    models_fetched = Signal(list)
    error = Signal(str)

    def __init__(self, provider: str, api_key: str, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.api_key = api_key

    def run(self):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            models = loop.run_until_complete(fetch_models(self.provider, self.api_key))
            self.models_fetched.emit(models)
        except Exception as e:
            logger.warning("Model fetch failed: %s", e)
            self.error.emit(str(e))
        finally:
            if not loop.is_closed():
                loop.close()
            asyncio.set_event_loop(None)
