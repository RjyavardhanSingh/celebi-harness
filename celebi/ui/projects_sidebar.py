"""Projects sidebar — list projects, add/remove."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from celebi.agents import get_agent_display_name, get_agent_names
from celebi.config import (
    add_project,
    load_projects,
    remove_project,
)


class ProjectsSidebar(QWidget):
    """Left sidebar showing project list with add/remove."""

    project_selected = Signal(str)  # project name
    project_added = Signal(str)  # project name
    project_removed = Signal(str)  # project name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)
        self._setup_ui()
        self.refresh_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 4, 8)

        # Header
        header = QLabel("Projects")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 4px;")
        layout.addWidget(header)

        # Project list
        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.currentTextChanged.connect(self._on_selection_changed)
        self._list.setStyleSheet(
            "QListWidget { border: 1px solid #444; border-radius: 4px; }"
            "QListWidget::item { padding: 8px; }"
            "QListWidget::item:selected { background-color: #4FC3F7; color: #000; }"
        )
        layout.addWidget(self._list)

        # Buttons
        btn_layout = QHBoxLayout()

        self._add_btn = QPushButton("+ Add")
        self._add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self._add_btn)

        self._remove_btn = QPushButton("− Remove")
        self._remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self._remove_btn)

        layout.addLayout(btn_layout)

    def refresh_list(self):
        """Reload project list from config and update UI."""
        self._list.clear()
        projects = load_projects()
        for project in projects:
            item = QListWidgetItem(project.name)
            item.setData(Qt.ItemDataRole.UserRole, project.name)
            self._list.addItem(item)

    def _on_selection_changed(self, text):
        if text:
            self.project_selected.emit(text)

    def _on_add(self):
        dialog = AddProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, path, agent = dialog.get_result()
            if name and path:
                try:
                    add_project(name, path, agent)
                    self.refresh_list()
                    self.project_added.emit(name)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add project: {e}")

    def _on_remove(self):
        item = self._list.currentItem()
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Remove Project",
            f"Remove '{name}' from Celebi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            remove_project(name)
            self.refresh_list()
            self.project_removed.emit(name)


class AddProjectDialog(QDialog):
    """Dialog for adding a new project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Project")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Project name
        self._name_field = QLineEdit()
        self._name_field.setPlaceholderText("my-project")
        form.addRow("Name:", self._name_field)

        # Project path
        path_layout = QHBoxLayout()
        self._path_field = QLineEdit()
        self._path_field.setPlaceholderText("/path/to/project")
        path_layout.addWidget(self._path_field)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(browse_btn)
        form.addRow("Folder:", path_layout)

        # Agent selection
        self._agent_combo = QComboBox()
        for key in get_agent_names():
            self._agent_combo.addItem(get_agent_display_name(key), key)
        form.addRow("Agent:", self._agent_combo)

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self._path_field.setText(folder)
            if not self._name_field.text():
                self._name_field.setText(Path(folder).name)

    def _on_accept(self):
        if not self._name_field.text().strip():
            QMessageBox.warning(self, "Missing Name", "Enter a project name.")
            return
        if not self._path_field.text().strip():
            QMessageBox.warning(self, "Missing Folder", "Select a project folder.")
            return
        self.accept()

    def get_result(self) -> tuple:
        return (
            self._name_field.text().strip(),
            self._path_field.text().strip(),
            self._agent_combo.currentData(),
        )
