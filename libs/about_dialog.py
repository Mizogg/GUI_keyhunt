"""
@author: Team Mizogg
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
import webbrowser
import platform

ICO_ICON = "images/miz.ico"
TITLE_ICON = "images/mizogglogo.png"
RED_ICON = "images/mizogg-eyes.png"
version = '1.2'

def open_website():
    webbrowser.open("https://mizogg.co.uk")

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KeyHunter Puzzles GUI")
        self.setWindowIcon(QIcon(ICO_ICON))
        self.setMinimumSize(800, 600)
        self.setStyleSheet("font-size: 14px; font-weight: bold;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header with logo
        header_pixmap = QPixmap(TITLE_ICON)
        header_label = QLabel()
        header_label.setPixmap(header_pixmap)
        layout.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        # Version and Platform Info
        current_platform = platform.system()
        info_label = QLabel(f"KeyHunter Puzzles GUI v{version} ({current_platform})\nMade by Team Mizogg")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        layout.addSpacing(20)

        # Main Content
        content_browser = QTextBrowser()
        content_browser.setOpenExternalLinks(True)
        content_browser.setHtml("""
<h2 style='text-align: center;'>🔍 KeyHunter Puzzles GUI - Advanced Bitcoin Key Hunting Tool 🔍</h2>

<h3>🌟 Major Features:</h3>

<h4>1. Multi-Instance Support</h4>
• Run up to 8 instances simultaneously<br>
• Each instance gets its own console window<br>
• Automatic CPU distribution<br>
• Shared configuration across all instances<br>
• Single start/stop control for all instances<br><br>

<h4>2. Theme Customization</h4>
• Light and dark theme options<br>
• Settings persist between sessions<br>
• Consistent styling across all components<br>
• Easy access through Settings menu<br><br>

<h4>3. Advanced Range Management</h4>
• Hexadecimal range calculator<br>
• Automatic range splitting for multiple instances<br>
• Percentage-based calculations<br>
• Visual range slider (1-256 bits)<br>
• Support for both compressed and uncompressed keys<br><br>

<h4>4. Enhanced Scanning Capabilities</h4>
• Multiple modes: address, bsgs, and rmd160<br>
• Support for both BTC and ETH<br>
• Configurable CPU usage per instance<br>
• Advanced progress tracking<br>
• File management tools<br><br>

<h4>5. User-Friendly Interface</h4>
• Modern, responsive design<br>
• Clear console output<br>
• Configurable console threshold<br>
• Copy and clear console functions<br>
• Helpful tooltips throughout<br><br>

<h3>💻 System Requirements:</h3>
• Python 3.6 or higher<br>
• PyQt6<br>
• Windows/Linux OS<br>
• RAM recommendations:<br>
  - 2 GB: -k 128<br>
  - 4 GB: -k 256<br>
  - 8 GB: -k 512<br>
  - 16 GB: -k 1024<br>
  - 32 GB: -k 2048<br><br>

<h3>🔧 CPU Distribution Examples:</h3>
• 8 CPUs, 8 instances = 1 CPU per instance<br>
• 8 CPUs, 4 instances = 2 CPUs per instance<br>
• Automatic optimization for your system<br><br>

<h3>📊 Default Range:</h3>
• 400000000000000000:7FFFFFFFFFFFFFFFFF (71 bits)<br>
• Fully adjustable through slider or direct input<br>
• Automatic splitting for multi-instance operation<br><br>

<h3>🚀 Quick Start:</h3>
1. Select instances (1-8) from menu<br>
2. Configure scanning parameters:<br>
   - Choose mode (address, bsgs, rmd160)<br>
   - Select cryptocurrency (BTC/ETH)<br>
   - Set CPU count per instance<br>
   - Configure range and other options<br>
3. Click "Start All Instances"<br>
4. Monitor progress in console windows<br>
5. Use "Stop All Instances" when needed<br><br>

<h3>🎯 Scanning Modes:</h3>
• Address mode: Search specific addresses<br>
• BSGS mode: Baby-Step Giant-Step algorithm<br>
• RMD160 mode: RIPEMD-160 hash search<br>
• Multiple movement modes (sequential, random, etc.)<br><br>

<h3>💡 Pro Tips:</h3>
• Use the range calculator for precise searches<br>
• Monitor CPU usage across instances<br>
• Save your configurations for future use<br>
• Check the tooltips for helpful information<br><br>

<h3>📞 Support:</h3>
• Website: <a href="https://mizogg.co.uk">https://mizogg.co.uk</a><br>
• Telegram: <a href="https://t.me/TeamHunter_GUI">https://t.me/TeamHunter_GUI</a><br><br>

<p style='text-align: center;'>
Made by Team Mizogg<br>
© mizogg.com 2018 - 2025
</p>
        """)
        layout.addWidget(content_browser)

        # Website Button
        icon_size = QSize(26, 26)
        iconred = QIcon(QPixmap(RED_ICON))
        self.miz_git_mode_button = QPushButton(self)
        self.miz_git_mode_button.setToolTip('<span style="font-size: 10pt; font-weight: bold;">Help ME. Just by visiting my site https://mizogg.co.uk keep up those clicks. Mizogg Website and Information </span>')
        self.miz_git_mode_button.setStyleSheet("font-size: 12pt;")
        self.miz_git_mode_button.setIconSize(icon_size)
        self.miz_git_mode_button.setIcon(iconred)
        self.miz_git_mode_button.clicked.connect(open_website)
        layout.addWidget(self.miz_git_mode_button)

        self.setLayout(layout)