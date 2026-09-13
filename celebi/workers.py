"""Shared QThread workers for background tasks."""

import asyncio

from PySide6.QtCore import QThread, Signal

from celebi.model_fetcher import fetch_models


class ModelFetchWorker(QThread):
    """Background thread to fetch models from provider API."""

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, provider: str, api_key: str, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.api_key = api_key

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            models = loop.run_until_complete(fetch_models(self.provider, self.api_key))
            loop.close()
            self.finished.emit(models)
        except Exception as e:
            self.error.emit(str(e))
