"""Project dashboard — controls, graph, and logs for a single project."""

from datetime import datetime

import httpx
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPainter, QTextCharFormat
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from celebi.agents import get_agent_display_name
from celebi.config import ProjectConfig


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


class GraphFetchWorker(QThread):
    """Fetch graph data in background to avoid blocking UI."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            resp = httpx.get(self.url, timeout=5)
            resp.raise_for_status()
            self.finished.emit(resp.json())
        except httpx.ConnectError:
            self.error.emit("connect_error")
        except Exception as e:
            self.error.emit(str(e))


class SearchFetchWorker(QThread):
    """Search conversations in background."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str, query: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.query = query

    def run(self):
        try:
            resp = httpx.get(self.url, params={"q": self.query}, timeout=10)
            resp.raise_for_status()
            self.finished.emit(resp.json())
        except Exception as e:
            self.error.emit(str(e))


class AnalyticsFetchWorker(QThread):
    """Fetch analytics data in background."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            resp = httpx.get(self.url, timeout=10)
            resp.raise_for_status()
            self.finished.emit(resp.json())
        except Exception as e:
            self.error.emit(str(e))


class ProjectDashboard(QWidget):
    """Per-project view with status, controls, graph, and logs."""

    start_requested = Signal(str)  # project name
    stop_requested = Signal(str)  # project name
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
        export_btn = QPushButton("Export PNG")
        export_btn.clicked.connect(self._export_graph)
        graph_btn_layout.addWidget(export_btn)
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

        # Search tab
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(8, 8, 8, 8)

        search_bar = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search conversations...")
        self._search_input.returnPressed.connect(self._on_search)
        search_bar.addWidget(self._search_input)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._on_search)
        search_bar.addWidget(search_btn)
        search_layout.addLayout(search_bar)

        self._search_results = QListWidget()
        self._search_results.setStyleSheet(
            "QListWidget { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; }"
            "QListWidget::item { padding: 8px; border-bottom: 1px solid #333; }"
            "QListWidget::item:selected { background-color: #2a4a5a; }"
        )
        self._search_results.itemDoubleClicked.connect(self._on_search_result_clicked)
        search_layout.addWidget(self._search_results)

        self._tabs.addTab(search_widget, "Search")

        # Analytics tab
        analytics_widget = QWidget()
        analytics_layout = QVBoxLayout(analytics_widget)
        analytics_layout.setContentsMargins(8, 8, 8, 8)

        analytics_btn_layout = QHBoxLayout()
        refresh_analytics_btn = QPushButton("Refresh Analytics")
        refresh_analytics_btn.clicked.connect(self._refresh_analytics)
        analytics_btn_layout.addWidget(refresh_analytics_btn)
        analytics_btn_layout.addStretch()
        analytics_layout.addLayout(analytics_btn_layout)

        self._analytics_summary = QLabel("No analytics loaded")
        self._analytics_summary.setStyleSheet("color: #888; font-size: 12px; padding: 8px;")
        analytics_layout.addWidget(self._analytics_summary)

        self._chart = QChart()
        self._chart.setTitle("Token Usage Per Request")
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        analytics_layout.addWidget(self._chart_view, stretch=1)

        self._tabs.addTab(analytics_widget, "Analytics")

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
        timestamp = datetime.now().strftime("%H:%M:%S")
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

        self._graph_worker = GraphFetchWorker(url)
        self._graph_worker.finished.connect(self._on_graph_fetched)
        self._graph_worker.error.connect(self._on_graph_error)
        self._graph_worker.start()

    def _on_graph_fetched(self, data: dict):
        if "error" in data:
            self._graph_view.clear()
            return
        edges = data.get("data", [])
        self._graph_view.load_graph(edges, self._project.proxy_port)

    def _on_graph_error(self, msg: str):
        self._graph_view.clear()

    def _export_graph(self):
        saved = self._graph_view.export_to_png(self.window())
        if saved:
            self._log_display.append("[celebi] Graph exported to PNG")
        else:
            self._log_display.append("[celebi] Export cancelled or failed")

    def _on_search(self):
        query = self._search_input.text().strip()
        if not query or not self._project:
            return

        url = f"http://localhost:{self._project.proxy_port}/search"
        self._search_worker = SearchFetchWorker(url, query)
        self._search_worker.finished.connect(self._on_search_results)
        self._search_worker.error.connect(self._on_search_error)
        self._search_worker.start()

    def _on_search_results(self, data: dict):
        self._search_results.clear()
        results = data.get("results", [])
        if not results:
            self._search_results.addItem("No results found")
            return

        for r in results:
            node_id = r["node_id"][:12]
            step_type = r["step_type"]
            payload = r["payload"]

            if step_type == "prompt":
                try:
                    import json

                    msg_data = json.loads(payload)
                    msgs = msg_data.get("messages", [])
                    for m in reversed(msgs):
                        if m.get("role") == "user":
                            text = m.get("content", "")[:80]
                            label = f"[{step_type}] {node_id}.. — {text}"
                            break
                    else:
                        label = f"[{step_type}] {node_id}.."
                except (json.JSONDecodeError, TypeError):
                    label = f"[{step_type}] {node_id}.. — {payload[:80]}"
            else:
                label = f"[{step_type}] {node_id}.. — {payload[:80]}"

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, r["node_id"])
            self._search_results.addItem(item)

    def _on_search_error(self, msg: str):
        self._search_results.clear()
        self._search_results.addItem(f"Error: {msg}")

    def _on_search_result_clicked(self, item: QListWidgetItem):
        from celebi.ui.graph_view import NodeDetailDialog

        node_id = item.data(Qt.ItemDataRole.UserRole)
        if not node_id or not self._project:
            return

        url = f"http://localhost:{self._project.proxy_port}/node/{node_id}"
        try:
            resp = httpx.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            dialog = NodeDetailDialog(
                data["node_id"],
                data["step_type"],
                data["payload"],
                self.window(),
                proxy_url=f"http://localhost:{self._project.proxy_port}",
            )
            dialog.exec()
        except Exception:
            pass

    def _refresh_analytics(self):
        if not self._project:
            return

        url = f"http://localhost:{self._project.proxy_port}/analytics"
        self._analytics_worker = AnalyticsFetchWorker(url)
        self._analytics_worker.finished.connect(self._on_analytics_fetched)
        self._analytics_worker.start()

    def _on_analytics_fetched(self, data: dict):
        if "error" in data:
            self._analytics_summary.setText(f"Error: {data['error']}")
            return

        total = data.get("total_tokens", 0)
        prompt = data.get("total_prompt_tokens", 0)
        completion = data.get("total_completion_tokens", 0)
        count = data.get("request_count", 0)

        self._analytics_summary.setText(
            f"Requests: {count}  |  "
            f"Prompt tokens: {prompt:,}  |  "
            f"Completion tokens: {completion:,}  |  "
            f"Total: {total:,}"
        )

        per_request = data.get("per_request", [])
        self._chart.removeAllSeries()

        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        if not per_request:
            return

        prompt_set = QBarSet("Prompt")
        completion_set = QBarSet("Completion")
        labels = []

        for req in per_request:
            prompt_set.append(req["prompt_tokens"])
            completion_set.append(req["completion_tokens"])
            labels.append(req["node_id"])

        series = QBarSeries()
        series.append(prompt_set)
        series.append(completion_set)
        self._chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Tokens")
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

    def _on_start(self):
        if self._project:
            self.start_requested.emit(self._project.name)

    def _on_stop(self):
        if self._project:
            self.stop_requested.emit(self._project.name)

    def _on_open_folder(self):
        if self._project:
            self.open_folder_requested.emit(self._project.path)
