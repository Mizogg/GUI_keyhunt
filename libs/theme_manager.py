from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QPushButton, QWidget, QCheckBox,
                            QLineEdit, QGroupBox, QFormLayout, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
import configparser

# Initialize config parser
config = configparser.ConfigParser()
config.read('config.ini')

class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings
    """
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Bitcoin Private Key Search Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout()
        
        self.tab_widget = QTabWidget()
        
        self.appearance_tab = QWidget()

        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        

        self.setup_appearance_tab()

        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        
    def setup_appearance_tab(self):
        """Setup the appearance tab"""
        layout = QVBoxLayout()
        
        # Theme settings group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        themes = list(theme_manager.themes.keys())
        self.theme_combo.addItems(themes)
        self.theme_combo.setCurrentText(theme_manager.current_theme)
        
        # Add theme preview
        self.theme_preview = QLabel()
        self.theme_preview.setFixedSize(300, 200)
        self.update_theme_preview(theme_manager.current_theme)
        
        self.theme_combo.currentTextChanged.connect(self.update_theme_preview)
        
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("Preview:", self.theme_preview)
        
        theme_group.setLayout(theme_layout)
        
        # Add groups to layout
        layout.addWidget(theme_group)
        layout.addStretch()
        
        self.appearance_tab.setLayout(layout)
        
    def update_theme_preview(self, theme_name):
        """Update the theme preview to show a realistic representation of the theme"""
        theme = theme_manager.get_theme(theme_name)
        
        # Create a preview widget to demonstrate theme elements
        preview_widget = QWidget()
        preview_widget.setFixedSize(300, 300)
        
        # Create a layout for the preview
        layout = QVBoxLayout(preview_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Add a title bar to simulate window
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(8, 0, 8, 0)
        
        title_label = QLabel("Preview Window")
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_button)
        
        # Create content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # Add some common UI elements
        button = QPushButton("Sample Button")
        checkbox = QCheckBox("Enable Option")
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter text...")
        
        content_layout.addWidget(button)
        content_layout.addWidget(checkbox)
        content_layout.addWidget(combo)
        content_layout.addWidget(text_input)
        content_layout.addStretch()
        
        # Add status bar
        status_bar = QLabel("Status: Ready")
        status_bar.setFixedHeight(25)
        status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Add all components to main layout
        layout.addWidget(title_bar)
        layout.addWidget(content_area)
        layout.addWidget(status_bar)
        
        # Apply theme colors
        preview_style = f"""
            QWidget {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                border: none;
            }}
            
            QLabel {{
                padding: 2px;
            }}
            
            QPushButton {{
                background-color: {theme['button_color']};
                color: {theme['button_text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['button_hover_color']};
            }}
            
            QLineEdit {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QComboBox {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QCheckBox {{
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['border_color']};
                border-radius: 3px;
                background-color: {theme['background_color']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme['accent_color']};
            }}
        """
        
        preview_widget.setStyleSheet(preview_style)
        
        pixmap = QPixmap(preview_widget.size())
        preview_widget.render(pixmap)
 
        self.theme_preview.setPixmap(pixmap)
        
    def save_settings(self):
        """Save settings and close dialog"""
        self.apply_settings()
        self.accept()
        
    def apply_settings(self):
        """Apply settings without closing dialog"""
        # Save theme settings
        theme_name = self.theme_combo.currentText()
        if theme_name != theme_manager.current_theme:
            theme_manager.set_theme(theme_name)
            if not config.has_section('theme'):
                config.add_section('theme')
            config.set('theme', 'name', theme_name)
            
            # Save to file
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            # Apply theme to all windows
            stylesheet = theme_manager.get_stylesheet()
            QApplication.instance().setStyleSheet(stylesheet)
            
            # Emit signal to notify of changes
            self.settings_changed.emit()

class ThemeManager:
    """
    Manages application themes and provides styling
    """
    def __init__(self):
        self.themes = {
            "default": {
                "description": "Defualt Black A sleek and minimalistic black theme with bold red accents",
                "primary_color": "#E7481F",
                "secondary_color": "#A13316",
                "background_color": "#000000",
                "text_color": "#FFFFFF",
                "accent_color": "#FFD700",
                "button_color": "#E7481F",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#A13316",
                "tab_color": "#3D3D3D",
                "tab_selected_color": "#E7481F",
                "tab_text_color": "#FFFFFF",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#555555",
                "success_color": "#28A745",
                "warning_color": "#FFC107",
                "error_color": "#DC3545",
                "info_color": "#17A2B8"
            },
            "bitcoin": {
                "description": "A bright and bold theme inspired by Bitcoin's signature orange and gold.",
                "primary_color": "#F7931A",
                "secondary_color": "#D68411",
                "background_color": "#FFFFFF",
                "text_color": "#4D4D4D",
                "accent_color": "#FFD700",
                "button_color": "#F7931A",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#D68411",
                "tab_color": "#F5F5F5",
                "tab_selected_color": "#F7931A",
                "tab_text_color": "#4D4D4D",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#CCCCCC",
                "success_color": "#28A745",
                "warning_color": "#FFC107",
                "error_color": "#DC3545",
                "info_color": "#17A2B8"
            },

            "black": {
                "description": "A sleek and minimalistic black theme with bold red accents",
                "primary_color": "#E7481F",
                "secondary_color": "#A13316",
                "background_color": "#000000",
                "text_color": "#FFFFFF",
                "accent_color": "#FFD700",
                "button_color": "#E7481F",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#A13316",
                "tab_color": "#3D3D3D",
                "tab_selected_color": "#E7481F",
                "tab_text_color": "#FFFFFF",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#555555",
                "success_color": "#28A745",
                "warning_color": "#FFC107",
                "error_color": "#DC3545",
                "info_color": "#17A2B8"
            },

            "cyberpunk": {
                "description": "A futuristic neon theme inspired by cyberpunk aesthetics and city lights.",
                "primary_color": "#0FF0FC",
                "secondary_color": "#FF007F",
                "background_color": "#1A1A2E",
                "text_color": "#0FF0FC",
                "accent_color": "#FFD700",
                "button_color": "#FF007F",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#D4006A",
                "tab_color": "#16213E",
                "tab_selected_color": "#FF007F",
                "tab_text_color": "#0FF0FC",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#FF007F",
                "success_color": "#00FF00",
                "warning_color": "#FFC107",
                "error_color": "#FF3131",
                "info_color": "#0FF0FC"
            },

            "dark": {
                "description": "A modern dark theme with deep gray tones and striking red highlights.",
                "primary_color": "#E7481F",
                "secondary_color": "#A13316",
                "background_color": "#2D2D2D",
                "text_color": "#FFFFFF",
                "accent_color": "#FFD700",
                "button_color": "#E7481F",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#A13316",
                "tab_color": "#3D3D3D",
                "tab_selected_color": "#E7481F",
                "tab_text_color": "#FFFFFF",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#555555",
                "success_color": "#28A745",
                "warning_color": "#FFC107",
                "error_color": "#DC3545",
                "info_color": "#17A2B8"
            },

            "devil_flaming": {
                "description": "Fiery reds, dark shadows, and an intense, infernal vibe 🔥😈",
                "primary_color": "#FF0000",
                "secondary_color": "#8B0000",
                "background_color": "#1E0000",
                "text_color": "#FF4500",
                "accent_color": "#FFD700",
                "button_color": "#B22222",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#FF4500",
                "tab_color": "#300000",
                "tab_selected_color": "#FF0000",
                "tab_text_color": "#FF6347",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#8B0000",
                "success_color": "#FF4500",
                "warning_color": "#FFA500",
                "error_color": "#8B0000",
                "info_color": "#FF6347"
            },

            "ice_blue": {
                "description": "Frozen whites, icy blues, and chilling cold vibes ❄️💙",
                "primary_color": "#00BFFF",
                "secondary_color": "#1E90FF",
                "background_color": "#E0F7FA",
                "text_color": "#005F8F",
                "accent_color": "#FFFFFF",
                "button_color": "#00CED1",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#4682B4",
                "tab_color": "#B0E0E6",
                "tab_selected_color": "#00BFFF",
                "tab_text_color": "#005F8F",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#A0C4FF",
                "success_color": "#00FA9A",
                "warning_color": "#87CEFA",
                "error_color": "#4682B4",
                "info_color": "#00FFFF"
            },

            "light": {
                "description": "A bright and clean theme with soft gray and warm red elements.",
                "primary_color": "#E7481F",
                "secondary_color": "#A13316",
                "background_color": "#F8F9FA",
                "text_color": "#212529",
                "accent_color": "#FFD700",
                "button_color": "#E7481F",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#A13316",
                "tab_color": "#E9ECEF",
                "tab_selected_color": "#E7481F",
                "tab_text_color": "#212529",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#DEE2E6",
                "success_color": "#28A745",
                "warning_color": "#FFC107",
                "error_color": "#DC3545",
                "info_color": "#17A2B8"
            },

            "matrix": {
                "description": "A hacker-inspired green-on-black theme straight out of The Matrix.",
                "primary_color": "#00FF00",
                "secondary_color": "#008800",
                "background_color": "#000000",
                "text_color": "#00FF00",
                "accent_color": "#FFFFFF",
                "button_color": "#008800",
                "button_text_color": "#00FF00",
                "button_hover_color": "#00AA00",
                "tab_color": "#001100",
                "tab_selected_color": "#00FF00",
                "tab_text_color": "#00FF00",
                "tab_selected_text_color": "#000000",
                "border_color": "#00FF00",
                "success_color": "#00FF00",
                "warning_color": "#FFFF00",
                "error_color": "#FF0000",
                "info_color": "#00FFFF"
            },

            "unicorn": {
                "description": "A playful and magical pastel theme with pinks, purples, and dreamy colors.",
                "primary_color": "#FF69B4",
                "secondary_color": "#9370DB",
                "background_color": "#F0F8FF",
                "text_color": "#4B0082",
                "accent_color": "#FFD700",
                "button_color": "#FF69B4",
                "button_text_color": "#FFFFFF",
                "button_hover_color": "#9370DB",
                "tab_color": "#E6E6FA",
                "tab_selected_color": "#FF69B4",
                "tab_text_color": "#4B0082",
                "tab_selected_text_color": "#FFFFFF",
                "border_color": "#D8BFD8",
                "success_color": "#00FF00",
                "warning_color": "#FFFF00",
                "error_color": "#FF0000",
                "info_color": "#00FFFF"
            }
        }
        self.current_theme = "black"
        
    def get_theme(self, theme_name=None):
        """Get a theme by name or the current theme if none specified"""
        if theme_name is None:
            theme_name = self.current_theme
            
        return self.themes.get(theme_name, self.themes["default"])
        
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
        
    def apply_theme(self, app):
        """Apply the current theme to the application"""
        if not isinstance(app, QApplication):
            raise TypeError("Expected QApplication instance")
            
        theme = self.get_theme()
        
        # Create a palette for the application
        palette = QPalette()
        
        # Set colors based on theme
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["background_color"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme["background_color"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["tab_color"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme["background_color"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme["text_color"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme["button_color"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["button_text_color"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["accent_color"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(theme["primary_color"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["primary_color"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["button_text_color"]))
        
        # Apply the palette to the application
        app.setPalette(palette)

        return self.get_stylesheet()

        
    def get_stylesheet(self):
        """Get the stylesheet for the current theme"""
        theme = self.get_theme()
        
        return f"""
        QMainWindow, QDialog {{
            background-color: {theme["background_color"]};
            color: {theme["text_color"]};
        }}
        
        QPushButton {{
            background-color: {theme["button_color"]};
            color: {theme["button_text_color"]};
            border: 1px solid {theme["border_color"]};
            border-radius: 4px;
            padding: 5px 10px;
        }}
        
        QPushButton:hover {{
            background-color: {theme["button_hover_color"]};
        }}
        
        QPushButton:pressed {{
            background-color: {theme["secondary_color"]};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme["border_color"]};
            background-color: {theme["background_color"]};
        }}
        
        QTabBar::tab {{
            background-color: {theme["tab_color"]};
            color: {theme["tab_text_color"]};
            border: 1px solid {theme["border_color"]};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 5px 10px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme["tab_selected_color"]};
            color: {theme["tab_selected_text_color"]};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {theme["button_hover_color"]};
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            border: 1px solid {theme["border_color"]};
            border-radius: 4px;
            padding: 3px;
            background-color: {theme["background_color"]};
            color: {theme["text_color"]};
        }}
        
        QLabel {{
            color: {theme["text_color"]};
        }}
        
        QCheckBox {{
            color: {theme["text_color"]};
        }}
        
        QRadioButton {{
            color: {theme["text_color"]};
        }}
        
        QGroupBox {{
            border: 1px solid {theme["border_color"]};
            border-radius: 4px;
            margin-top: 10px;
            color: {theme["text_color"]};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
        }}
        
        QMenuBar {{
            background-color: {theme["background_color"]};
            color: {theme["text_color"]};
        }}
        
        QMenuBar::item:selected {{
            background-color: {theme["primary_color"]};
            color: {theme["button_text_color"]};
        }}
        
        QMenu {{
            background-color: {theme["background_color"]};
            color: {theme["text_color"]};
            border: 1px solid {theme["border_color"]};
        }}
        
        QMenu::item:selected {{
            background-color: {theme["primary_color"]};
            color: {theme["button_text_color"]};
        }}
        
        QProgressBar {{
            border: 1px solid {theme["border_color"]};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme["primary_color"]};
        }}
        
        QScrollBar:vertical {{
            border: 1px solid {theme["border_color"]};
            background: {theme["background_color"]};
            width: 15px;
            margin: 15px 0 15px 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {theme["button_color"]};
            min-height: 20px;
        }}
        
        QScrollBar:horizontal {{
            border: 1px solid {theme["border_color"]};
            background: {theme["background_color"]};
            height: 15px;
            margin: 0 15px 0 15px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {theme["button_color"]};
            min-width: 20px;
        }}
        """
        
    def add_theme(self, name, theme_dict):
        """Add a new theme to the theme manager"""
        # Validate theme dict has all required keys
        required_keys = set(self.themes["default"].keys())
        if not required_keys.issubset(set(theme_dict.keys())):
            missing_keys = required_keys - set(theme_dict.keys())
            raise ValueError(f"Theme is missing required keys: {missing_keys}")
            
        self.themes[name] = theme_dict
        return True
        
# Create a singleton instance
theme_manager = ThemeManager() 