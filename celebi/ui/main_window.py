"""Main window — wizard first, then dashboard."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QWidget,
)

from celebi.agents import generate_agent_config
from celebi.config import (
    ProjectConfig,
    find_available_port,
    get_project,
    is_port_available,
    load_global,
    load_projects,
)
from celebi.ui.project_dashboard import ProjectDashboard
from celebi.ui.projects_sidebar import ProjectsSidebar
from celebi.ui.settings_tab import SettingsTab
from celebi.ui.setup_wizard import SetupWizard

API_DIR = Path(__file__).resolve().parent.parent.parent / "api"


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle (no system Python/uv)."""
    return getattr(sys, "frozen", False)


def _server_workdir() -> str:
    """Writable CWD for server child processes (install dir is read-only)."""
    workdir = Path.home() / ".celebi"
    workdir.mkdir(parents=True, exist_ok=True)
    return str(workdir)


class MainWindow(QMainWindow):
    """Celebi — wizard first, then dashboard."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Celebi — LLM Time Travel Harness")
        self.setMinimumSize(1100, 700)

        self._global_config = load_global()
        self._current_project: ProjectConfig = None
        self._processes: dict[str, dict] = {}

        self._setup_ui()
        self._connect_signals()

        # Show wizard if no projects exist
        if not load_projects():
            self._show_wizard()
        else:
            self._show_dashboard()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self._root_layout = QHBoxLayout(central)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Stack: wizard or dashboard
        self._stack = QStackedWidget()

        # Page 0: Setup wizard
        self._wizard = SetupWizard()
        self._stack.addWidget(self._wizard)

        # Page 1: Dashboard (sidebar + content)
        self._dashboard_page = self._build_dashboard_page()
        self._stack.addWidget(self._dashboard_page)

        self._root_layout.addWidget(self._stack)

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        self._add_project_action = QAction("Add Project", self)
        self._add_project_action.setShortcut("Ctrl+N")
        self._add_project_action.triggered.connect(self._show_wizard)
        file_menu.addAction(self._add_project_action)

        self._settings_action = QAction("Settings", self)
        self._settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(self._settings_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        self.statusBar().showMessage("Ready")

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self._sidebar = ProjectsSidebar()
        layout.addWidget(self._sidebar)

        # Dashboard
        self._dashboard = ProjectDashboard()
        layout.addWidget(self._dashboard, stretch=1)

        return page

    def _connect_signals(self):
        # Wizard
        self._wizard.finished.connect(self._on_wizard_finished)

        # Sidebar
        self._sidebar.project_selected.connect(self._on_project_selected)
        self._sidebar.project_added.connect(self._on_project_added)
        self._sidebar.project_removed.connect(self._on_project_removed)

        # Dashboard
        self._dashboard.start_requested.connect(self._on_start_project)
        self._dashboard.stop_requested.connect(self._on_stop_project)
        self._dashboard.open_folder_requested.connect(self._on_open_folder)

    def _show_wizard(self):
        self._stack.setCurrentWidget(self._wizard)

    def _show_dashboard(self):
        self._sidebar.refresh_list()
        self._stack.setCurrentWidget(self._dashboard_page)

    def _show_settings(self):
        # Open settings in a simple dialog
        from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout

        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.setMinimumWidth(450)
        dlg_layout = QVBoxLayout(dlg)
        settings = SettingsTab(self._global_config)
        dlg_layout.addWidget(settings)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self._on_settings_saved(settings, dlg))
        dlg_layout.addWidget(save_btn)
        dlg.exec()

    def _on_settings_saved(self, settings, dlg):
        config = settings.save()
        self._global_config = config

        if not config.model:
            dlg.accept()
            return

        errors = []

        # Regenerate agent config for current project if one is selected
        if self._current_project:
            try:
                generate_agent_config(
                    self._current_project.agent,
                    self._current_project.path,
                    self._current_project.proxy_port,
                    config.model,
                )
            except Exception as e:
                errors.append(f"Project config: {e}")

        # Also update the root-level opencode.json so OpenCode picks up the change
        try:
            from celebi.agents import write_opencode_config

            celebi_root = Path(__file__).resolve().parent.parent.parent
            write_opencode_config(str(celebi_root), 8000, config.model)
        except Exception as e:
            errors.append(f"Root config: {e}")

        if errors:
            self.statusBar().showMessage(f"Saved with errors: {'; '.join(errors)}", 5000)
        else:
            self.statusBar().showMessage("Settings saved — restart OpenCode to apply", 3000)

        dlg.accept()

    @Slot()
    def _on_wizard_finished(self):
        self._global_config = self._wizard.get_global_config()
        self._current_project = self._wizard.get_project()
        self._show_dashboard()

        # Generate agent config immediately
        if self._current_project and self._global_config.model:
            try:
                config_path = generate_agent_config(
                    self._current_project.agent,
                    self._current_project.path,
                    self._current_project.proxy_port,
                    self._global_config.model,
                )
                self.statusBar().showMessage(
                    f"Generated {config_path.name} in {self._current_project.path}",
                    5000,
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Config Warning",
                    f"Could not generate agent config:\n{e}",
                )

        # Auto-select the new project
        if self._current_project:
            self._dashboard.load_project(self._current_project)

    @Slot(str)
    def _on_project_selected(self, name: str):
        project = get_project(name)
        if project:
            self._current_project = project
            self._dashboard.load_project(project)
            if name in self._processes:
                self._dashboard.set_running()

    @Slot(str)
    def _on_project_added(self, name: str):
        self.statusBar().showMessage(f"Project '{name}' added", 3000)

    @Slot(str)
    def _on_project_removed(self, name: str):
        if name in self._processes:
            self._kill_project_processes(name)
            del self._processes[name]
        self.statusBar().showMessage(f"Project '{name}' removed", 3000)

    @Slot(str)
    def _on_start_project(self, name: str):
        project = get_project(name)
        if not project:
            return

        if self._is_running(name):
            self.statusBar().showMessage("Already running", 3000)
            return

        if not self._global_config.api_key:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Set your API key first (File → Settings).",
            )
            return

        # Auto-detect port conflicts and reassign if needed
        litellm_port = project.litellm_port
        proxy_port = project.proxy_port

        if not is_port_available(litellm_port):
            try:
                litellm_port = find_available_port(litellm_port + 1)
                self.statusBar().showMessage(
                    f"LiteLLM port {project.litellm_port} busy, using {litellm_port}",
                    4000,
                )
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    "Port Conflict",
                    f"LiteLLM port {project.litellm_port} is busy and no alternative ports are available.",
                )
                return

        if not is_port_available(proxy_port):
            try:
                proxy_port = find_available_port(proxy_port + 1)
                self.statusBar().showMessage(
                    f"Proxy port {project.proxy_port} busy, using {proxy_port}",
                    4000,
                )
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    "Port Conflict",
                    f"Proxy port {project.proxy_port} is busy and no alternative ports are available.",
                )
                return

        # Kill any stale processes on our ports
        self._kill_port(litellm_port)
        self._kill_port(proxy_port)

        # Generate agent config
        try:
            config_path = generate_agent_config(
                project.agent,
                project.path,
                proxy_port,
                self._global_config.model,
            )
            self.statusBar().showMessage(f"Generated {config_path.name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate config:\n{e}")
            return

        # Generate litellm config
        litellm_config_path = Path.home() / ".celebi" / "litellm-config.yaml"
        litellm_config_path.parent.mkdir(parents=True, exist_ok=True)
        litellm_model = self._global_config.litellm_model_name()
        env_key = self._global_config.env_key
        litellm_config_path.write_text(
            f"model_list:\n"
            f"  - model_name: {self._global_config.model}\n"
            f"    litellm_params:\n"
            f"      model: {litellm_model}\n"
            f"      api_key: os.environ/{env_key}\n"
        )

        self._dashboard.set_starting()

        # Start LiteLLM
        litellm_proc = QProcess(self)
        litellm_proc.setProcessChannelMode(QProcess.MergedChannels)
        litellm_proc.readyReadStandardOutput.connect(
            lambda: self._on_process_output(name, litellm_proc, "LITELLM")
        )

        litellm_env = self._global_config.litellm_env()
        process_env = litellm_proc.processEnvironment()
        for k, v in litellm_env.items():
            process_env.insert(k, v)
        litellm_proc.setProcessEnvironment(process_env)

        if is_frozen():
            # Packaged app: re-exec our own binary in server mode.
            # (`uv run` would try to create .venv inside the read-only
            # install dir, and `uv` may not exist on user machines.)
            litellm_proc.setWorkingDirectory(_server_workdir())
            litellm_proc.start(
                sys.executable,
                [
                    "--serve-litellm",
                    "--config",
                    str(litellm_config_path),
                    "--port",
                    str(litellm_port),
                ],
            )
        else:
            litellm_proc.setWorkingDirectory(str(API_DIR))
            uv_bin = shutil.which("uv") or "uv"
            litellm_proc.start(
                uv_bin,
                [
                    "run",
                    "litellm",
                    "--config",
                    str(litellm_config_path),
                    "--port",
                    str(litellm_port),
                ],
            )

        if not litellm_proc.waitForStarted(5000):
            self._dashboard.set_error("Failed to start LiteLLM")
            return

        # Start FastAPI proxy
        proxy_proc = QProcess(self)
        proxy_proc.setProcessChannelMode(QProcess.MergedChannels)
        proxy_proc.readyReadStandardOutput.connect(
            lambda: self._on_process_output(name, proxy_proc, "PROXY")
        )

        proxy_env = proxy_proc.processEnvironment()
        proxy_env.insert("CELEBI_UPSTREAM_PORT", str(litellm_port))
        proxy_env.insert("CELEBI_PROXY_PORT", str(proxy_port))
        proxy_env.insert("CELEBI_DATA_DIR", str(Path.home() / ".celebi"))
        proxy_proc.setProcessEnvironment(proxy_env)

        if is_frozen():
            # Packaged app: sys.executable is the frozen binary, not a
            # Python interpreter, so `-m uvicorn` would relaunch the GUI.
            proxy_proc.setWorkingDirectory(_server_workdir())
            proxy_proc.start(sys.executable, ["--serve-proxy"])
        else:
            proxy_proc.setWorkingDirectory(str(API_DIR))
            proxy_proc.start(
                sys.executable,
                [
                    "-m",
                    "uvicorn",
                    "main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(proxy_port),
                ],
            )

        if not proxy_proc.waitForStarted(5000):
            litellm_proc.kill()
            self._dashboard.set_error("Failed to start proxy")
            return

        self._processes[name] = {
            "proxy": proxy_proc,
            "litellm": litellm_proc,
        }

        self._dashboard.set_running()
        self.statusBar().showMessage(f"Running on :{proxy_port}", 5000)

    @Slot(str)
    def _on_stop_project(self, name: str):
        self._kill_project_processes(name)
        self._dashboard.set_stopped()
        self.statusBar().showMessage("Stopped", 3000)

    @Slot(str)
    def _on_open_folder(self, path: str):
        system = platform.system()
        if system == "Darwin":
            subprocess.Popen(["open", path])
        elif system == "Windows":
            subprocess.Popen(["start", path], shell=True)
        else:
            subprocess.Popen(["xdg-open", path])

    def _kill_project_processes(self, name: str):
        if name in self._processes:
            procs = self._processes[name]
            for key in ["proxy", "litellm"]:
                proc = procs.get(key)
                if proc and proc.state() == QProcess.Running:
                    proc.kill()
                    proc.waitForFinished(3000)

    def _kill_port(self, port: int):
        """Kill any process holding the given port."""
        try:
            subprocess.run(
                ["fuser", "-k", f"{port}/tcp"],
                capture_output=True,
                timeout=5,
            )
        except Exception:
            pass

    @Slot(object, str)
    def _on_process_output(self, project_name: str, process: QProcess, source: str):
        data = process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        for line in data.strip().split("\n"):
            if line:
                self._dashboard.add_log(line, source)

    def closeEvent(self, event):
        running = [n for n in self._processes if self._is_running(n)]
        if running:
            reply = QMessageBox.question(
                self,
                "Quit Celebi?",
                f"Projects running: {', '.join(running)}.\nStop and quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # Kill all child processes (QProcess already terminates on parent exit,
        # but explicit cleanup avoids zombies on some platforms)
        for name in list(self._processes.keys()):
            self._kill_project_processes(name)
        self._processes.clear()
        event.accept()

    def _is_running(self, name: str) -> bool:
        if name not in self._processes:
            return False
        return any(p and p.state() == QProcess.Running for p in self._processes[name].values())
