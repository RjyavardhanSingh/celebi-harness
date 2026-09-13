"""Global settings tab — provider, API key, model dropdown.

Flow: User selects provider → enters API key → models fetched → select from dropdown.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QGroupBox, QPushButton,
)
from PySide6.QtCore import Signal, Qt

from celebi.config import GlobalConfig, save_global
from celebi.workers import ModelFetchWorker


class SettingsTab(QWidget):
    """Global settings — provider, API key, model. Set once."""

    config_changed = Signal(GlobalConfig)

    def __init__(self, config: GlobalConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._fetch_worker = None
        self._setup_ui()
        self._load_from_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Provider group
        cred_group = QGroupBox("Provider Credentials")
        form = QFormLayout()

        # Provider dropdown
        self._provider_combo = QComboBox()
        self._provider_combo.addItems(["gemini", "openai", "anthropic"])
        self._provider_combo.setEditable(True)
        self._provider_combo.currentTextChanged.connect(self._on_provider_changed)
        form.addRow("Provider:", self._provider_combo)

        # API key
        key_layout = QHBoxLayout()
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setPlaceholderText("Enter your API key...")
        key_layout.addWidget(self._api_key_input)

        self._fetch_btn = QPushButton("Fetch Models")
        self._fetch_btn.setMinimumWidth(120)
        self._fetch_btn.clicked.connect(self._on_fetch_models)
        key_layout.addWidget(self._fetch_btn)
        form.addRow("API Key:", key_layout)

        # Model dropdown (populated after fetch)
        model_layout = QHBoxLayout()
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._model_combo.setPlaceholderText("Click 'Fetch Models' first...")
        model_layout.addWidget(self._model_combo)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setMinimumWidth(70)
        self._refresh_btn.clicked.connect(self._on_fetch_models)
        model_layout.addWidget(self._refresh_btn)
        form.addRow("Model:", model_layout)

        # Status label
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #888; font-size: 11px;")
        form.addRow("", self._status_label)

        cred_group.setLayout(form)
        layout.addWidget(cred_group)

        # Info
        info = QLabel(
            "These settings apply to all projects.\n"
            "Select a provider, enter your API key, then click 'Fetch Models' "
            "to see available models."
        )
        info.setStyleSheet("color: #666; font-style: italic; padding: 8px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

    def _load_from_config(self):
        # Set provider
        idx = self._provider_combo.findText(self._config.provider)
        if idx >= 0:
            self._provider_combo.setCurrentIndex(idx)
        elif self._config.provider:
            self._provider_combo.setEditText(self._config.provider)

        # Set API key
        self._api_key_input.setText(self._config.api_key)

        # Set model
        if self._config.model:
            self._model_combo.setEditText(self._config.model)

    def _on_provider_changed(self, text):
        pass  # User needs to click Fetch Models

    def _on_fetch_models(self):
        provider = self._provider_combo.currentText().strip()
        api_key = self._api_key_input.text().strip()

        if not provider:
            self._status_label.setText("Select a provider first")
            self._status_label.setStyleSheet("color: #f44336; font-size: 11px;")
            return

        if not api_key:
            self._status_label.setText("Enter an API key first")
            self._status_label.setStyleSheet("color: #f44336; font-size: 11px;")
            return

        self._fetch_btn.setEnabled(False)
        self._refresh_btn.setEnabled(False)
        self._status_label.setText("Fetching models...")
        self._status_label.setStyleSheet("color: #FFC107; font-size: 11px;")

        self._fetch_worker = ModelFetchWorker(provider, api_key)
        self._fetch_worker.finished.connect(self._on_models_fetched)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_models_fetched(self, models: list[str]):
        self._fetch_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)

        self._model_combo.clear()
        self._model_combo.addItems(models)

        # Restore current model if in list
        if self._config.model:
            idx = self._model_combo.findText(self._config.model)
            if idx >= 0:
                self._model_combo.setCurrentIndex(idx)
            else:
                self._model_combo.setEditText(self._config.model)

        self._status_label.setText(f"Found {len(models)} models")
        self._status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")

    def _on_fetch_error(self, msg: str):
        self._fetch_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)
        self._status_label.setText(f"Error: {msg}")
        self._status_label.setStyleSheet("color: #f44336; font-size: 11px;")

    def get_config(self) -> GlobalConfig:
        return GlobalConfig(
            provider=self._provider_combo.currentText().strip(),
            api_key=self._api_key_input.text().strip(),
            model=self._model_combo.currentText().strip(),
        )

    def save(self) -> GlobalConfig:
        config = self.get_config()
        save_global(config)
        self._config = config
        self.config_changed.emit(config)
        return config
