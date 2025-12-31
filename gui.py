import sys
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit, QFrame, QCompleter)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor
from utils import on_browse_email_file, on_generate_phones_clicked, cancel_operations, on_closing
from constants import COUNTRY_NAME_TO_REGION, COUNTRY_NAME_TO_CODE, MAX_LOG_LINES

class Theme:
    """Holds all our styling info like colors and fonts in one place."""
    # Colors
    BACKGROUND = "#1e1e1e"
    SURFACE = "#252525"
    SURFACE_ALT = "#2d2d2d"
    INPUT_BG = "#333333"
    TEXT = "#e0e0e0"       # Slightly off-white for better readability
    TEXT_SECONDARY = "#aaaaaa"
    ACCENT = "#007acc"     # VS Code-like blue
    ACCENT_HOVER = "#0062a3"
    ACCENT_PRESSED = "#004d80"
    BORDER = "#404040"
    ERROR = "#f48771"
    SUCCESS = "#89d185"
    
    # Metric
    BORDER_RADIUS = "6px"
    PADDING = "10px"
    
    # Fonts
    FONT_FAMILY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"

class TextUpdateSignals(QObject):
    """Signals used to safely update the GUI from background threads."""
    append_text = pyqtSignal(str)


class SearchableComboBox(QComboBox):
    """
    A dropdown menu that lets you search for a country.
    It automatically formats things as 'Country (+Code)'.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._name_to_display = {}  # Spain -> Spain (+34)
        self._display_to_name = {}  # Spain (+34) -> Spain
        
    def addItems(self, country_data: dict):
        """Adds all the countries to the list and sets up the search filter.
        
        Args:
            country_data (dict): Dictionary of country names to codes.
        """
        display_items = []
        for name in sorted(country_data.keys()):
            code = country_data[name]
            display = f"{name} (+{code})"
            display_items.append(display)
            self._display_to_name[display] = name
            
        super().addItems(display_items)
        
        # This makes the search feel snappy
        completer = QCompleter(display_items, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCompleter(completer)
        
    def currentCountryName(self) -> str:
        """Helper to get just the country name, without the code part."""
        text = self.currentText()
        return self._display_to_name.get(text, text.split(" (+")[0] if " (+" in text else text)
        
    def setPopupStyle(self, style: str):
        """Applies styling to the dropdown list part."""
        if self.completer() and self.completer().popup():
            self.completer().popup().setStyleSheet(style)

class MainWindow(QMainWindow):
    """The main window of the application where everything is laid out."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amazon Email and Number Checker")
        self.setGeometry(100, 100, 1000, 700)
        
        self.signals = TextUpdateSignals()
        self.signals.append_text.connect(self.append_text_safe)
        self.stop_event = threading.Event()
        self.auto_scroll = True
        self.is_updating_text = False
        self.user_scrolled = False
        
        self.set_dark_theme()
        self.setup_ui()
        
        self.result_text.verticalScrollBar().valueChanged.connect(self.scroll_changed)

    def set_dark_theme(self):
        """Apply the global dark theme palette."""
        dark_palette = QPalette()
        
        # Map Theme colors to Palette roles
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(Theme.BACKGROUND))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(Theme.TEXT))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(Theme.SURFACE))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Theme.SURFACE_ALT))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Theme.SURFACE))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Theme.TEXT))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(Theme.TEXT))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(Theme.SURFACE_ALT))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(Theme.TEXT))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(Theme.ERROR))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(Theme.ACCENT))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(Theme.ACCENT))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        self.setPalette(dark_palette)

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Title
        title_label = QLabel("Amazon Email and Number Checker")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(Theme.FONT_FAMILY) 
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {Theme.ACCENT}; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Input Frame
        input_frame = QFrame()
        input_frame.setStyleSheet(f"background-color: {Theme.SURFACE}; border-radius: {Theme.BORDER_RADIUS}; border: 1px solid {Theme.BORDER};")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        input_frame.setLayout(input_layout)

        # Shared Input Style
        input_style = f"""
            /* Generic Input Styling */
            QLineEdit {{
                background: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                padding: 8px;
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                font-size: 14px;
                selection-background-color: {Theme.ACCENT};
                selection-color: {Theme.TEXT};
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.ACCENT};
            }}

            /* ComboBox Base Styling */
            QComboBox {{
                background: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                padding: 8px;
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                font-size: 14px;
                selection-background-color: {Theme.ACCENT};
                selection-color: {Theme.TEXT};
            }}
            QComboBox:focus {{
                border: 1px solid {Theme.ACCENT};
            }}
            
            /* The Text Field inside ComboBox */
            QComboBox:editable {{
                background: {Theme.INPUT_BG};
            }}
            QComboBox QLineEdit {{
                background: transparent; /* Let ComboBox BG show through */
                border: none;
                padding: 0px;
                margin: 0px;
            }}

            /* The Dropdown Button Area */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px; /* Wider for easier clicking */
                border-left-width: 1px;
                border-left-color: {Theme.BORDER};
                border-left-style: solid;
                border-top-right-radius: 4px; /* Match input radius */
                border-bottom-right-radius: 4px;
                background: {Theme.INPUT_BG};
            }}
            QComboBox::drop-down:hover {{
                background: {Theme.SURFACE_ALT};
            }}

            /* The Dropdown Arrow Icon */
            QComboBox::down-arrow {{
                image: none;
                width: 0; 
                height: 0; 
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid {Theme.ACCENT}; /* Use Accent color */
                margin-right: 6px;
                margin-top: 2px; /* Visual centering adjustment */
            }}
            QComboBox::down-arrow:on {{
                /* Shift slightly when pressed */
                margin-top: 4px;
            }}
            
            /* Dropdown List Popup */
            QListView, QAbstractItemView {{
                background: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 1px solid {Theme.BORDER};
                outline: none;
                selection-background-color: {Theme.ACCENT};
            }}
            
            QListView::item {{
                padding: 5px;
                min-height: 25px;
            }}
            
            QListView::item:selected {{
                background: {Theme.ACCENT};
                color: white;
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                background: {Theme.INPUT_BG};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

        # Cores
        core_label = QLabel("Number of Threads")
        core_label.setFont(QFont("Segoe UI", 11))
        # Reset border from QFrame inheritance
        core_label.setStyleSheet("border: none; color: " + Theme.TEXT) 
        input_layout.addWidget(core_label)

        self.core_entry = QLineEdit()
        self.core_entry.setStyleSheet(input_style)
        self.core_entry.setText("10") # Default value
        input_layout.addWidget(self.core_entry)

        # Country
        country_label = QLabel("Target Country")
        country_label.setFont(QFont("Segoe UI", 11))
        country_label.setStyleSheet("border: none; color: " + Theme.TEXT)
        input_layout.addWidget(country_label)

        self.country_combo = SearchableComboBox()
        self.country_combo.setStyleSheet(input_style)
        
        # Add items
        self.country_combo.addItems(COUNTRY_NAME_TO_CODE)
        
        # Apply same style to completer popup so it matches the dark theme
        self.country_combo.setPopupStyle(input_style)
        
        input_layout.addWidget(self.country_combo)

        # Prefix
        prefix_label = QLabel("Prefix (Optional, comma-separated)")
        prefix_label.setFont(QFont("Segoe UI", 11))
        prefix_label.setStyleSheet("border: none; color: " + Theme.TEXT)
        input_layout.addWidget(prefix_label)

        self.prefix_entry = QLineEdit()
        self.prefix_entry.setPlaceholderText("e.g. 6, 7 (Leave empty for all)")
        self.prefix_entry.setStyleSheet(input_style)
        input_layout.addWidget(self.prefix_entry)

        main_layout.addWidget(input_frame)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        button_style = f"""
            QPushButton {{
                background-color: {Theme.SURFACE_ALT};
                color: {Theme.TEXT};
                padding: 10px 20px;
                border-radius: 4px;
                border: 1px solid {Theme.BORDER};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                border-color: {Theme.ACCENT};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {Theme.ACCENT_PRESSED};
            }}
        """

        self.browse_button = QPushButton("Browse Email List")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setStyleSheet(button_style)
        self.browse_button.clicked.connect(self.browse_file_wrapper)
        button_layout.addWidget(self.browse_button)

        self.generate_button = QPushButton("Generate Numbers")
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.setStyleSheet(button_style)
        self.generate_button.clicked.connect(self.generate_numbers_wrapper)
        button_layout.addWidget(self.generate_button)

        self.cancel_button = QPushButton("Cancel Operations")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setStyleSheet(button_style.replace(Theme.ACCENT, Theme.ERROR).replace(Theme.ACCENT_PRESSED, "#c0392b")) # Red hover for cancel
        self.cancel_button.clicked.connect(self.cancel_operations_wrapper)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Results Log
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"background-color: {Theme.BACKGROUND}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: {Theme.BORDER_RADIUS}; padding: 10px; font-family: 'Consolas', 'Monospace'; font-size: 13px; line-height: 1.4;")
        main_layout.addWidget(self.result_text)

    def scroll_changed(self, value):
        """Track if user has scrolled up or is at the bottom"""
        if self.is_updating_text:
            return
            
        scrollbar = self.result_text.verticalScrollBar()
        max_value = scrollbar.maximum()
        

        at_bottom = (max_value - value) <= 20
        
        if not at_bottom and self.auto_scroll:
            self.auto_scroll = False
            self.user_scrolled = True

        elif at_bottom and not self.auto_scroll:
            self.auto_scroll = True
            self.user_scrolled = False


    def append_text_safe(self, text):
        """Thread-safe method to append text with Scroll Compensation.
        
        Args:
            text (str): Text to append.
        """
        try:
            self.is_updating_text = True
            
            scrollbar = self.result_text.verticalScrollBar()
            should_auto_scroll = self.auto_scroll
            
            # 1. Format text
            if "[+] Yes" in text:
                text = f'<span style="color: {Theme.SUCCESS};">{text}</span>'
            elif "[!] Error" in text or "[-]" in text:
                text = f'<span style="color: {Theme.ERROR};">{text}</span>'
            else:
                text = f'<span style="color: {Theme.TEXT_SECONDARY};">{text}</span>'

            # 2. Add the new line
            cursor = self.result_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(text)
            cursor.insertBlock()

            # 3. Handle Trimming & Compensation (Batch trimming for performance)
            doc = self.result_text.document()
            if doc.blockCount() > MAX_LOG_LINES + 50:  # Allow 50 lines of "cushion"
                # Capture current scroll state
                prev_val = scrollbar.value()
                prev_max = scrollbar.maximum()
                
                # Batch trim: remove 50 lines at once to save CPU
                trim_cursor = QTextCursor(doc.findBlockByNumber(0))
                for _ in range(50):
                    trim_cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.KeepAnchor)
                
                trim_cursor.removeSelectedText()
                trim_cursor.deleteChar() # Cleanup extra newline

                if not should_auto_scroll:
                    new_max = scrollbar.maximum()
                    diff = prev_max - new_max
                    scrollbar.setValue(prev_val - diff)
                else:
                    scrollbar.setValue(scrollbar.maximum())
            elif should_auto_scroll:
                scrollbar.setValue(scrollbar.maximum())
                
        finally:
            self.is_updating_text = False

    def browse_file_wrapper(self):
        self.auto_scroll = True
        on_browse_email_file(self.result_text, self.stop_event, self.core_entry, self.signals)

    def generate_numbers_wrapper(self):
        self.auto_scroll = True
        on_generate_phones_clicked(self.result_text, self.stop_event, self.core_entry, self.country_combo, self.prefix_entry, COUNTRY_NAME_TO_REGION, self.signals)

    def cancel_operations_wrapper(self):
        cancel_operations(self.stop_event)

    def closeEvent(self, event):
        on_closing(self, self.stop_event)
        event.accept()

def setup_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    setup_gui()