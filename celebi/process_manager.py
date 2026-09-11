"""Process manager for Celebi backend services.

Spawns and manages FastAPI proxy and LiteLLM as subprocesses.
Uses QProcess for integration with PySide6 event loop.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QProcess, Signal, Slot

from celebi.config import CelebiConfig, generate_litellm_config

logger = logging.getLogger(__name__)

API_DIR = Path(__file__).resolve().parent.parent / "api"


class ProcessManager(QObject):
    """Manages FastAPI proxy and LiteLLM subprocesses."""

    proxy_started = Signal()
    proxy_stopped = Signal()
    litellm_started = Signal()
    litellm_stopped = Signal()
    proxy_log = Signal(str)
    litellm_log = Signal(str)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._proxy: Optional[QProcess] = None
        self._litellm: Optional[QProcess] = None
        self._config: Optional[CelebiConfig] = None

    @property
    def proxy_running(self) -> bool:
        return self._proxy is not None and self._proxy.state() == QProcess.Running

    @property
    def litellm_running(self) -> bool:
        return self._litellm is not None and self._litellm.state() == QProcess.Running

    def start(self, config: CelebiConfig) -> None:
        """Start both LiteLLM and FastAPI proxy."""
        self._config = config

        # Generate litellm config from celebi config
        litellm_config_path = generate_litellm_config(config)

        # Start LiteLLM first
        self._start_litellm(config, litellm_config_path)

        # Wait a moment for LiteLLM to bind its port
        time.sleep(1)

        # Start FastAPI proxy
        self._start_proxy(config)

    def stop(self) -> None:
        """Stop all running processes."""
        self._stop_proxy()
        self._stop_litellm()

    def _start_litellm(self, config: CelebiConfig, config_path: Path) -> None:
        """Start LiteLLM proxy subprocess."""
        if self.litellm_running:
            return

        self._litellm = QProcess(self)
        self._litellm.setProcessChannelMode(QProcess.MergedChannels)
        self._litellm.readyReadStandardOutput.connect(self._on_litellm_output)
        self._litellm.finished.connect(self._on_litellm_finished)

        env = config.litellm_env()
        process_env = self._litellm.processEnvironment()
        for key, value in env.items():
            process_env.insert(key, value)
        self._litellm.setProcessEnvironment(process_env)

        cmd = sys.executable
        args = [
            "-m", "litellm",
            "--config", str(config_path),
            "--port", str(config.litellm_port),
        ]

        logger.info("Starting LiteLLM: %s %s", cmd, " ".join(args))
        self._litellm.setWorkingDirectory(str(API_DIR))
        self._litellm.start(cmd, args)

        if not self._litellm.waitForStarted(5000):
            self.error.emit("Failed to start LiteLLM")
            return

        self.litellm_started.emit()

    def _start_proxy(self, config: CelebiConfig) -> None:
        """Start FastAPI proxy subprocess."""
        if self.proxy_running:
            return

        self._proxy = QProcess(self)
        self._proxy.setProcessChannelMode(QProcess.MergedChannels)
        self._proxy.readyReadStandardOutput.connect(self._on_proxy_output)
        self._proxy.finished.connect(self._on_proxy_finished)

        # Set env so proxy knows the upstream port
        process_env = self._proxy.processEnvironment()
        process_env.insert("CELEBI_UPSTREAM_PORT", str(config.litellm_port))
        process_env.insert("CELEBI_PROXY_PORT", str(config.proxy_port))
        self._proxy.setProcessEnvironment(process_env)

        cmd = sys.executable
        args = [
            "-m", "uvicorn",
            "main:app",
            "--host", "127.0.0.1",
            "--port", str(config.proxy_port),
        ]

        logger.info("Starting FastAPI proxy: %s %s", cmd, " ".join(args))
        self._proxy.setWorkingDirectory(str(API_DIR))
        self._proxy.start(cmd, args)

        if not self._proxy.waitForStarted(5000):
            self.error.emit("Failed to start FastAPI proxy")
            return

        self.proxy_started.emit()

    def _stop_proxy(self) -> None:
        if self._proxy and self._proxy.state() == QProcess.Running:
            self._proxy.kill()
            self._proxy.waitForFinished(3000)
        self._proxy = None
        self.proxy_stopped.emit()

    def _stop_litellm(self) -> None:
        if self._litellm and self._litellm.state() == QProcess.Running:
            self._litellm.kill()
            self._litellm.waitForFinished(3000)
        self._litellm = None
        self.litellm_stopped.emit()

    @Slot()
    def _on_proxy_output(self):
        if self._proxy:
            data = self._proxy.readAllStandardOutput().data().decode("utf-8", errors="replace")
            for line in data.strip().split("\n"):
                if line:
                    self.proxy_log.emit(line)

    @Slot()
    def _on_litellm_output(self):
        if self._litellm:
            data = self._litellm.readAllStandardOutput().data().decode("utf-8", errors="replace")
            for line in data.strip().split("\n"):
                if line:
                    self.litellm_log.emit(line)

    @Slot(int, QProcess.ExitStatus)
    def _on_proxy_finished(self, exit_code, exit_status):
        logger.info("FastAPI proxy exited with code %d", exit_code)
        self.proxy_stopped.emit()

    @Slot(int, QProcess.ExitStatus)
    def _on_litellm_finished(self, exit_code, exit_status):
        logger.info("LiteLLM exited with code %d", exit_code)
        self.litellm_stopped.emit()
