"""Setup wizard — two-page flow: Project → Credentials → Done."""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog,
    QFormLayout, QGroupBox, QMessageBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from celebi.config import (
    GlobalConfig, save_global, add_project, load_projects, ProjectConfig,
)
from celebi.agents import get_agent_names, get_agent_display_name
from celebi.model_fetcher import fetch_models

import asyncio
from PySide6.QtCore import QThread


class ModelFetchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, provider, api_key, parent=None):
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


class SetupWizard(QWidget):
    """Two-page setup wizard. Emits finished() when complete."""

    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project: ProjectConfig = None
        self._global_config = GlobalConfig()
        self._fetch_worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("Celebi Setup")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 24px 0 8px 0;")
        layout.addWidget(header)

        # Stacked pages
        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_project_page())
        self._pages.addWidget(self._build_credentials_page())
        layout.addWidget(self._pages, stretch=1)

        # Navigation buttons
        nav = QHBoxLayout()
        nav.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setMinimumWidth(100)
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setEnabled(False)
        nav.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next →")
        self._next_btn.setMinimumWidth(100)
        self._next_btn.setDefault(True)
        self._next_btn.clicked.connect(self._go_next)
        nav.addWidget(self._next_btn)

        layout.addLayout(nav)

    # ── Page 1: Project ──────────────────────────────────────────

    def _build_project_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(80, 40, 80, 40)

        title = QLabel("Select a Project")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Choose the folder you want to work on and which coding agent you use.")
        subtitle.setStyleSheet("color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._name_field = QLineEdit()
        self._name_field.setPlaceholderText("my-project")
        form.addRow("Name:", self._name_field)

        path_row = QHBoxLayout()
        self._path_field = QLineEdit()
        self._path_field.setPlaceholderText("/path/to/project")
        path_row.addWidget(self._path_field)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_folder)
        path_row.addWidget(browse_btn)
        form.addRow("Folder:", path_row)

        self._agent_combo = QComboBox()
        for key in get_agent_names():
            self._agent_combo.addItem(get_agent_display_name(key), key)
        form.addRow("Agent:", self._agent_combo)

        layout.addLayout(form)
        layout.addStretch()

        return page

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self._path_field.setText(folder)
            if not self._name_field.text():
                self._name_field.setText(Path(folder).name)

    # ── Page 2: Credentials ──────────────────────────────────────

    def _build_credentials_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(80, 40, 80, 40)

        title = QLabel("Provider Credentials")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Enter your API key and select a model.")
        subtitle.setStyleSheet("color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._provider_combo = QComboBox()
        self._provider_combo.addItems(["gemini", "openai", "anthropic"])
        self._provider_combo.setEditable(True)
        form.addRow("Provider:", self._provider_combo)

        key_row = QHBoxLayout()
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setPlaceholderText("Enter your API key")
        key_row.addWidget(self._api_key_input)
        self._fetch_btn = QPushButton("Fetch Models")
        self._fetch_btn.setFixedWidth(120)
        self._fetch_btn.clicked.connect(self._fetch_models)
        key_row.addWidget(self._fetch_btn)
        form.addRow("API Key:", key_row)

        model_row = QHBoxLayout()
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._model_combo.setPlaceholderText("Click 'Fetch Models' first...")
        model_row.addWidget(self._model_combo)
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedWidth(30)
        refresh_btn.clicked.connect(self._fetch_models)
        model_row.addWidget(refresh_btn)
        form.addRow("Model:", model_row)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size: 11px;")
        form.addRow("", self._status_label)

        layout.addLayout(form)
        layout.addStretch()

        return page

    def _fetch_models(self):
        provider = self._provider_combo.currentText().strip()
        api_key = self._api_key_input.text().strip()

        if not provider:
            self._set_status("Select a provider", error=True)
            return
        if not api_key:
            self._set_status("Enter an API key", error=True)
            return

        self._fetch_btn.setEnabled(False)
        self._set_status("Fetching models...")

        self._fetch_worker = ModelFetchWorker(provider, api_key)
        self._fetch_worker.finished.connect(self._on_models_fetched)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_models_fetched(self, models):
        self._fetch_btn.setEnabled(True)
        self._model_combo.clear()
        self._model_combo.addItems(models)
        self._set_status(f"Found {len(models)} models", error=False)

    def _on_fetch_error(self, msg):
        self._fetch_btn.setEnabled(True)
        self._set_status(f"Error: {msg}", error=True)

    def _set_status(self, msg, error=False):
        self._status_label.setText(msg)
        color = "#f44336" if error else "#4CAF50"
        self._status_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    # ── Navigation ───────────────────────────────────────────────

    def _go_next(self):
        current = self._pages.currentIndex()

        if current == 0:
            # Validate project page
            name = self._name_field.text().strip()
            path = self._path_field.text().strip()
            if not name:
                QMessageBox.warning(self, "Missing Name", "Enter a project name.")
                return
            if not path:
                QMessageBox.warning(self, "Missing Folder", "Select a project folder.")
                return

            # Save project
            agent = self._agent_combo.currentData()
            self._project = add_project(name, path, agent)

            self._back_btn.setEnabled(True)
            self._next_btn.setText("Finish ✓")
            self._pages.setCurrentIndex(1)

        elif current == 1:
            # Validate credentials page
            api_key = self._api_key_input.text().strip()
            model = self._model_combo.currentText().strip()
            provider = self._provider_combo.currentText().strip()

            if not api_key:
                QMessageBox.warning(self, "Missing API Key", "Enter your API key.")
                return
            if not model:
                QMessageBox.warning(self, "Missing Model", "Fetch and select a model.")
                return

            # Save global config
            self._global_config = GlobalConfig(
                provider=provider,
                api_key=api_key,
                model=model,
            )
            save_global(self._global_config)

            self.finished.emit()

    def _go_back(self):
        current = self._pages.currentIndex()
        if current == 1:
            self._back_btn.setEnabled(False)
            self._next_btn.setText("Next →")
            self._pages.setCurrentIndex(0)

    def get_project(self) -> ProjectConfig:
        return self._project

    def get_global_config(self) -> GlobalConfig:
        return self._global_config
