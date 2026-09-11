"""Project dashboard — controls, graph, and logs for a single project."""

import httpx
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QFrame, QTextEdit,
    QTabWidget,
)
from PySide6.QtCore import Signal, Slot, Qt, QThread
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from celebi.config import ProjectConfig, GlobalConfig
from celebi.agents import get_agent_display_name


class StatusIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.set_off()

    def set_off(self):
        self.setStyleSheet("background-color: #666; border-radius: 6px;")
        self.setToolTip("Stopped")

    def set_on(self):
        self.setStyleSheet("background-color: #4CAF50; border-radius: 6px;")
        self.setToolTip("Running")

    def set_starting(self):
        self.setStyleSheet("background-color: #FFC107; border-radius: 6px;")
        self.setToolTip("Starting...")


class ProjectDashboard(QWidget):
    """Per-project view with status, controls, graph, and logs."""

    start_requested = Signal(str)  # project name
    stop_requested = Signal(str)   # project name
    open_folder_requested = Signal(str)  # project path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project: ProjectConfig = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Project header
        header_layout = QHBoxLayout()

        self._name_label = QLabel("No project selected")
        self._name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self._name_label)

        header_layout.addStretch()

        self._agent_label = QLabel()
        self._agent_label.setStyleSheet("color: #888; font-size: 12px;")
        header_layout.addWidget(self._agent_label)

        layout.addLayout(header_layout)

        # Status bar
        status_layout = QHBoxLayout()

        self._status_indicator = StatusIndicator()
        status_layout.addWidget(self._status_indicator)

        self._status_label = QLabel("Stopped")
        self._status_label.setStyleSheet("color: #888;")
        status_layout.addWidget(self._status_label)

        status_layout.addStretch()

        self._port_label = QLabel()
        self._port_label.setStyleSheet("color: #666; font-size: 11px;")
        status_layout.addWidget(self._port_label)

        layout.addLayout(status_layout)

        # Control buttons
        btn_layout = QHBoxLayout()

        self._start_btn = QPushButton("Start")
        self._start_btn.setMinimumHeight(36)
        self._start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:disabled { background-color: #555; color: #888; }"
        )
        self._start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self._start_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setMinimumHeight(36)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; font-weight: bold; border-radius: 4px; padding: 0 20px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
            "QPushButton:disabled { background-color: #555; color: #888; }"
        )
        self._stop_btn.clicked.connect(self._on_stop)
        btn_layout.addWidget(self._stop_btn)

        self._folder_btn = QPushButton("Open Folder")
        self._folder_btn.setMinimumHeight(36)
        self._folder_btn.clicked.connect(self._on_open_folder)
        btn_layout.addWidget(self._folder_btn)

        layout.addLayout(btn_layout)

        # Tabs: Graph + Logs
        self._tabs = QTabWidget()

        # Graph tab
        from celebi.ui.graph_view import GraphView
        self._graph_view = GraphView()
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(0, 4, 0, 0)

        graph_btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Graph")
        refresh_btn.clicked.connect(self._refresh_graph)
        graph_btn_layout.addWidget(refresh_btn)
        graph_btn_layout.addStretch()
        graph_layout.addLayout(graph_btn_layout)

        graph_layout.addWidget(self._graph_view)
        self._tabs.addTab(graph_widget, "Graph")

        # Logs tab
        self._log_display = QTextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setFont(QFont("Monospace", 10))
        self._log_display.setStyleSheet(
            "QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; }"
        )
        self._tabs.addTab(self._log_display, "Logs")

        layout.addWidget(self._tabs, stretch=1)

    def load_project(self, project: ProjectConfig):
        self._project = project
        self._name_label.setText(project.name)
        self._agent_label.setText(f"Agent: {get_agent_display_name(project.agent)}")
        self._port_label.setText(
            f"Proxy: :{project.proxy_port}  |  LiteLLM: :{project.litellm_port}"
        )
        self.set_stopped()

    def set_starting(self):
        self._status_indicator.set_starting()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("Starting...")
        self._status_label.setStyleSheet("color: #FFC107;")

    def set_running(self):
        self._status_indicator.set_on()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText("Running")
        self._status_label.setStyleSheet("color: #4CAF50;")

    def set_stopped(self):
        self._status_indicator.set_off()
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("Stopped")
        self._status_label.setStyleSheet("color: #888;")

    def set_error(self, msg: str):
        self._status_label.setText(f"Error: {msg}")
        self._status_label.setStyleSheet("color: #f44336;")

    @Slot(str)
    def add_log(self, message: str, source: str = "PROXY"):
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
        color = QColor("#4FC3F7") if source == "PROXY" else QColor("#81C784")

        cursor = self._log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#888"))
        cursor.insertText(f"[{timestamp}] ", fmt)

        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setFontWeight(QFont.Weight.Bold)
        cursor.insertText(f"[{source}] ", fmt)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#d4d4d4"))
        cursor.insertText(message + "\n", fmt)

        self._log_display.setTextCursor(cursor)
        self._log_display.ensureCursorVisible()

    def _refresh_graph(self):
        if not self._project:
            return

        url = f"http://localhost:{self._project.proxy_port}/graph"

        try:
            resp = httpx.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError:
            self._graph_view.clear()
            return
        except Exception as e:
            self._graph_view.clear()
            return

        if "error" in data:
            self._graph_view.clear()
            return

        edges = data.get("data", [])
        self._graph_view.load_graph(edges, self._project.proxy_port)

    def _on_start(self):
        if self._project:
            self.start_requested.emit(self._project.name)

    def _on_stop(self):
        if self._project:
            self.stop_requested.emit(self._project.name)

    def _on_open_folder(self):
        if self._project:
            self.open_folder_requested.emit(self._project.path)
