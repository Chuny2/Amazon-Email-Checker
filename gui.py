import sys
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor
from utils import browse_file, generate_numbers, cancel_operations, on_closing
from constants import country_codes

# Maximum number of log lines to keep in the UI
MAX_LOG_LINES = 200
# Buffer zone - only trim when we exceed this percentage over maximum 
TRIM_BUFFER = 0.25
# Target size after trimming (percentage of max)
TRIM_TARGET = 0.75

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
        self.log_lines_count = 0
        self.auto_scroll = True  # Flag to track if auto-scrolling is enabled
        self.is_updating_text = False  # Flag to prevent recursive scroll updates
        self.last_manual_scroll_time = time.time()  # Track when user last scrolled
        self.user_scrolled = False  # Explicit flag for user scrolling
        self.setup_ui()
        
        # Connect scrollbar value change to track user scrolling
        self.result_text.verticalScrollBar().valueChanged.connect(self.scroll_changed)
        
        # Add timer to periodically check if we should reattach to bottom
        self.scroll_timer = QTimer()
        self.scroll_timer.setInterval(500)  # Check every 500ms
        self.scroll_timer.timeout.connect(self.check_auto_scroll)
        self.scroll_timer.start()

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

    def scroll_changed(self, value):
        """Track if user has scrolled up or is at the bottom"""
        # Skip if we're programmatically updating text
        if self.is_updating_text:
            return
            
        scrollbar = self.result_text.verticalScrollBar()
        max_value = scrollbar.maximum()
        
        # If scrollbar is at the bottom (with small margin)
        at_bottom = (max_value - value) <= 5
        
        # If moved away from bottom
        if not at_bottom and self.auto_scroll:
            self.auto_scroll = False
            self.user_scrolled = True
            self.last_manual_scroll_time = time.time()
        # If explicitly scrolled to bottom
        elif at_bottom and not self.auto_scroll:
            self.auto_scroll = True
            self.user_scrolled = False

    def check_auto_scroll(self):
        """Check if we should re-enable auto-scroll after user inactivity"""
        # If user previously scrolled away but hasn't scrolled in 3 seconds
        if self.user_scrolled and time.time() - self.last_manual_scroll_time > 3:
            scrollbar = self.result_text.verticalScrollBar() 
            at_bottom = (scrollbar.maximum() - scrollbar.value()) <= 5
            
            # If they're at the bottom now, re-enable auto-scroll
            if at_bottom:
                self.auto_scroll = True
                self.user_scrolled = False

    def append_text_safe(self, text):
        """Thread-safe method to append text to result_text with line limiting"""
        try:
            # Set flag to prevent scroll detection during update
            self.is_updating_text = True
            
            # Remember scroll position and auto-scroll state
            scrollbar = self.result_text.verticalScrollBar()
            prev_pos = scrollbar.value()
            should_auto_scroll = self.auto_scroll
            
            # Add the text to the end
            cursor = self.result_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.result_text.setTextCursor(cursor)
            self.result_text.insertPlainText(text + "\n")
            self.log_lines_count += 1
            
            # Only trim logs after accumulating a significant number beyond the limit
            trim_threshold = int(MAX_LOG_LINES * (1 + TRIM_BUFFER))
            if self.log_lines_count > trim_threshold:
                # Get current text and split into lines
                current_text = self.result_text.toPlainText()
                lines = current_text.split('\n')
                
                # Calculate how many lines to remove to get to the target size
                target_size = int(MAX_LOG_LINES * TRIM_TARGET)
                lines_to_remove = len(lines) - target_size
                
                if lines_to_remove > 0:
                    # Calculate approximately how much text will be removed
                    text_before = len(current_text)
                    
                    # Remove oldest lines
                    new_text = '\n'.join(lines[lines_to_remove:])
                    text_after = len(new_text)
                    
                    # Block UI updates during the change
                    self.result_text.setUpdatesEnabled(False)
                    
                    # Update content
                    self.result_text.setPlainText(new_text)
                    
                    # Update counter
                    self.log_lines_count = len(lines) - lines_to_remove
                    
                    # Re-enable UI updates
                    self.result_text.setUpdatesEnabled(True)
                    
                    # If not at bottom, adjust scroll position to maintain relative position
                    if not should_auto_scroll and prev_pos > 0:
                        # Calculate new position - if we removed text above the visible area
                        new_pos = max(0, prev_pos - (text_before - text_after))
                        scrollbar.setValue(new_pos)
            
            # Only scroll to bottom if auto-scroll is enabled
            if should_auto_scroll:
                QApplication.processEvents()  # Let UI update
                scrollbar.setValue(scrollbar.maximum())
            else:
                # Try to maintain previous scroll position if we weren't trimming
                if self.log_lines_count <= trim_threshold:
                    scrollbar.setValue(prev_pos)
                
        finally:
            # Always reset flag
            self.is_updating_text = False

    def browse_file_wrapper(self):
        # Force auto-scroll when starting new operations
        self.auto_scroll = True
        browse_file(self.result_text, self.stop_event, self.core_entry, self.signals)

    def generate_numbers_wrapper(self):
        # Force auto-scroll when starting new operations
        self.auto_scroll = True
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