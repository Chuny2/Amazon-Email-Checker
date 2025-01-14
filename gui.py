import sys
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThreadPool
from PyQt6.QtGui import QFont, QColor, QPalette
from utils import browse_file, generate_numbers, cancel_operations, on_closing
from constants import country_codes

class TextUpdateSignals(QObject):
    append_text = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amazon Email and Number Checker")
        self.setGeometry(100, 100, 1000, 700)
        
        self.signals = TextUpdateSignals()
        self.signals.append_text.connect(self.append_text_safe)
        self.stop_event = threading.Event()
        self.threadpool = QThreadPool()
        self.setup_ui()

    def setup_ui(self):
        # Set up the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Set the color scheme
        self.set_dark_theme()

        # Title
        title_label = QLabel("Amazon Email and Number Checker")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #61dafb; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; padding: 20px;")
        input_layout = QVBoxLayout()
        input_frame.setLayout(input_layout)

        core_label = QLabel("Number of Cores")
        core_label.setFont(QFont("Segoe UI", 12))
        input_layout.addWidget(core_label)

        self.core_entry = QLineEdit()
        self.core_entry.setStyleSheet("background-color: #3a3a3a; color: white; padding: 8px; border-radius: 5px; font-size: 14px;")
        input_layout.addWidget(self.core_entry)

        country_label = QLabel("Select Country")
        country_label.setFont(QFont("Segoe UI", 12))
        input_layout.addWidget(country_label)

        self.country_combo = QComboBox()
        self.country_combo.addItems(sorted(country_codes.keys()))
        self.country_combo.setStyleSheet("background-color: #3a3a3a; color: white; padding: 8px; border-radius: 5px; font-size: 14px;")
        input_layout.addWidget(self.country_combo)

        main_layout.addWidget(input_frame)

        # Buttons
        button_layout = QHBoxLayout()
        button_style = """
        QPushButton {
            background-color: #4a4a4a;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        """

        self.browse_button = QPushButton("Browse Email List")
        self.browse_button.setStyleSheet(button_style)
        self.browse_button.clicked.connect(self.browse_file_wrapper)
        button_layout.addWidget(self.browse_button)

        self.generate_button = QPushButton("Generate Numbers")
        self.generate_button.setStyleSheet(button_style)
        self.generate_button.clicked.connect(self.generate_numbers_wrapper)
        button_layout.addWidget(self.generate_button)

        self.cancel_button = QPushButton("Cancel Operations")
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.clicked.connect(self.cancel_operations_wrapper)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Result area
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("background-color: #2a2a2a; color: white; border-radius: 10px; padding: 10px; font-family: 'Consolas'; font-size: 14px;")
        main_layout.addWidget(self.result_text)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)

    def append_text_safe(self, text):
        """Thread-safe method to append text to result_text"""
        self.result_text.append(text)
        self.result_text.ensureCursorVisible()

    def browse_file_wrapper(self):
        browse_file(self.result_text, self.stop_event, self.core_entry, self.signals)

    def generate_numbers_wrapper(self):
        generate_numbers(self.result_text, self.stop_event, self.core_entry, self.country_combo, country_codes, self.signals)

    def cancel_operations_wrapper(self):
        cancel_operations(self.stop_event)

    def closeEvent(self, event):
        on_closing(self, self.stop_event)
        event.accept()

def setup_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    setup_gui()