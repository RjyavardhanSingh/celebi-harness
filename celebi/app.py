"""Celebi desktop application entry point.

Usage:
    python -m celebi.app
    or
    uv run celebi
"""

import logging
import sys

from PySide6.QtWidgets import QApplication

from celebi.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Celebi")
    app.setApplicationVersion("0.1.0")

    # Dark theme
    app.setStyleSheet("""
        QMainWindow { background-color: #2b2b2b; }
        QWidget { background-color: #2b2b2b; color: #d4d4d4; }
        QTabWidget::pane { border: 1px solid #444; }
        QTabBar::tab {
            background: #333; color: #aaa; padding: 8px 16px;
            border: 1px solid #444; border-bottom: none;
        }
        QTabBar::tab:selected {
            background: #2b2b2b; color: #fff; border-bottom: 2px solid #4FC3F7;
        }
        QGroupBox { border: 1px solid #444; border-radius: 4px; margin-top: 8px; padding-top: 16px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #333; color: #d4d4d4; border: 1px solid #555;
            border-radius: 3px; padding: 4px 8px;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border-color: #4FC3F7; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #333; color: #d4d4d4; selection-background-color: #4FC3F7; }
        QPushButton {
            background-color: #444; color: #d4d4d4; border: 1px solid #555;
            border-radius: 3px; padding: 6px 16px;
        }
        QPushButton:hover { background-color: #555; }
        QToolBar { background-color: #333; border-bottom: 1px solid #444; }
        QMenuBar { background-color: #333; color: #d4d4d4; }
        QMenuBar::item:selected { background-color: #444; }
        QMenu { background-color: #333; color: #d4d4d4; }
        QMenu::item:selected { background-color: #4FC3F7; }
        QStatusBar { background-color: #333; color: #888; }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
