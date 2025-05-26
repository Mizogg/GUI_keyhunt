"""
@author: Team Mizogg
"""
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os
import glob
import subprocess
import webbrowser
import signal
import platform
import multiprocessing
from libs.console_gui import ConsoleWindow
from libs.command_thread import CommandThread
from libs.about_dialog import AboutDialog
from libs.progress_dialog import ProgressDialog
from libs.Range_gui import RangeDialog
from libs.theme_manager import ThemeManager
import configparser

theme_manager = ThemeManager()
ICO_ICON = "images/miz.ico"
TITLE_ICON = "images/mizogglogo.png"
RED_ICON = "images/mizogg-eyes.png"
version = '1.2'
current_platform = platform.system()

def open_website(self):
    webbrowser.open("https://mizogg.co.uk")

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_instances = 1
        self.keyhunt_frames = []
        self.shared_config = None  # Will hold shared configuration
        self.cpu_count = multiprocessing.cpu_count()  # Initialize cpu_count
        self.command_threads = {}  # Dictionary to store command threads for each instance
        self.initUI()

    def initUI(self):
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # Add shared configuration at the top
        self.shared_config = self.create_shared_config()
        main_layout.addWidget(self.shared_config)

        # Add grid for console windows
        self.grid_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.grid_widget)
        main_layout.addWidget(self.grid_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Settings", self.open_settings)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.exit_app)

        instances_menu = menubar.addMenu("Instances")
        instances_menu.addAction("1", lambda: self.update_grid_layout(1))
        instances_menu.addAction("2", lambda: self.update_grid_layout(2))
        instances_menu.addAction("4", lambda: self.update_grid_layout(4))
        instances_menu.addAction("6", lambda: self.update_grid_layout(6))
        instances_menu.addAction("8", lambda: self.update_grid_layout(8))
        file_menu.addSeparator()

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Help Telegram Group", self.open_telegram)
        help_menu.addAction("About", self.about)

        # Add credits
        self.add_credits(main_layout)

        self.setGeometry(60, 100, 400, 300)
        self.setWindowTitle("KeyHunter Puzzles GUI")
        self.setWindowIcon(QIcon(f"{ICO_ICON}"))
        self.update_grid_layout(1)

    def create_shared_config(self):
        group_box = QGroupBox("Shared Configuration")
        layout = QVBoxLayout()

        # Add all configuration controls from KeyHuntFrame
        keyhunt_config = self.create_threadGroupBox()
        layout.addWidget(keyhunt_config)
        
        keyspace_config = self.create_keyspaceGroupBox()
        layout.addWidget(keyspace_config)

        output_config = self.create_outputFileGroupBox()
        layout.addWidget(output_config)

        # Add start/stop buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start All Instances")
        self.start_button.clicked.connect(self.start_all_instances)
        self.stop_button = QPushButton("Stop All Instances")
        self.stop_button.clicked.connect(self.stop_all_instances)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        group_box.setLayout(layout)
        return group_box

    def update_grid_layout(self, num_instances):
        self.current_instances = num_instances
        self.keyhunt_frames.clear()
        
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

        # Set up grid dimensions
        if num_instances == 1:
            rows, cols = 1, 1
        elif num_instances == 2:
            rows, cols = 1, 2
        elif num_instances == 4:
            rows, cols = 2, 2
        elif num_instances == 6:
            rows, cols = 2, 3
        elif num_instances == 8:
            rows, cols = 2, 4

        # Calculate max CPUs per instance
        max_cpus_per_instance = self.cpu_count // num_instances
        if max_cpus_per_instance < 1:
            max_cpus_per_instance = 1

        # Update CPU combo box with new limits
        self.threadComboBox_key.clear()
        for i in range(1, max_cpus_per_instance + 1):
            self.threadComboBox_key.addItem(str(i))
        self.threadComboBox_key.setCurrentIndex(0)  # Set to first available option

        # Create new console windows
        instance_number = 1
        for row in range(rows):
            for col in range(cols):
                console = ConsoleWindow(self)
                console.setWindowTitle(f"Instance {instance_number}/{num_instances}")
                self.grid_layout.addWidget(console, row, col)
                self.keyhunt_frames.append(console)
                instance_number += 1

        self.grid_widget.setLayout(self.grid_layout)
        self.adjust_size()

    def start_all_instances(self):
        try:
            # Get the range from shared input
            range_text = self.keyspaceLineEdit.text().strip()
            if not range_text:
                QMessageBox.warning(self, "Error", "Please enter a range")
                return

            start_range, end_range = range_text.split(':')
            # Convert hex strings to integers, handling both with and without 0x prefix
            start_range = int(start_range, 16) if start_range.startswith('0x') else int(start_range, 16)
            end_range = int(end_range, 16) if end_range.startswith('0x') else int(end_range, 16)

            # Split range among instances
            ranges = self.split_range(start_range, end_range, len(self.keyhunt_frames))

            # Start each instance with its portion of the range
            for i, console in enumerate(self.keyhunt_frames):
                instance_start, instance_end = ranges[i]
                self.start_instance(console, instance_start, instance_end, i + 1)

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid range format: {str(e)}\nPlease use hex format (e.g., 400000000000000000:7FFFFFFFFFFFFFFFFF)")

    def start_instance(self, console, start_range, end_range, instance_number):
        """Start a single instance with the given range"""
        console.append_output(f"Instance {instance_number}/{len(self.keyhunt_frames)}")
        console.append_output(f"Range: {format(start_range, 'x')} to {format(end_range, 'x')}")
        
        command = self.construct_command_key(start_range, end_range)
        self.execute_command(console, command, instance_number)

    def construct_command_key(self, start_range, end_range):
        """Construct keyhunt command with current configuration"""
        mode = self.modeComboBox.currentText().strip()
        thread_count = int(self.threadComboBox_key.currentText())
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyhunt")

        if platform.system() == "Windows":
            command = [os.path.join(base_path, "keyhunt.exe"), "-m", mode, "-t", str(thread_count)]
        else:
            command = [os.path.join(base_path, "keyhunt"), "-m", mode, "-t", str(thread_count)]

        # Add range
        command.extend(["-r", f"{format(start_range, 'x')}:{format(end_range, 'x')}"])

        # Add other parameters from shared configuration
        file = self.inputFileLineEdit.text().strip()
        if file:
            input_file_relative_path = ["input", file]
            input_file_path = os.path.join(*input_file_relative_path)
            command.extend(["-f", input_file_path])

        move_mode = self.move_modeEdit.currentText().strip()
        if move_mode == 'random':
            if mode == 'bsgs':
                command.extend(["-B", move_mode])
            else:
                command.append("-R")
        elif move_mode == 'sequential':
            if mode == 'bsgs':
                command.extend(["-B", move_mode])
            else:
                command.append("-S")
        elif move_mode == 'backward' and mode == 'bsgs':
            command.extend(["-B", move_mode])
        elif move_mode == 'dance' and mode == 'bsgs':
            command.extend(["-B", move_mode])
        elif move_mode == 'both' and mode == 'bsgs':
            command.extend(["-B", move_mode])

        if not (mode == 'bsgs' and move_mode == 'both'):
            stride = self.strideLineEdit.text().strip()
            if stride:
                command.extend(["-I", stride])

        crypto = self.cryptoComboBox.currentText().strip()
        if crypto == "eth":
            command.extend(["-c", crypto])
            
        look = self.lookComboBox.currentText().strip()
        if look:
            command.extend(["-l", look])

        if mode == 'bsgs':
            n_value = self.nValueLineEdit.text().strip()
            if n_value:
                command.extend(["-n", n_value])
            kamount = int(self.kComboBox.currentText().strip())
            command.extend(["-k", str(kamount)])

        if self.flagQCheckBox.isChecked():
            command.append("-q")

        return command

    def execute_command(self, console, command, instance_number):
        """Execute command and show output in the given console window"""
        # Stop existing thread for this instance if it exists
        if instance_number in self.command_threads:
            self.command_threads[instance_number].terminate()
            self.command_threads[instance_number].wait()

        # Convert command list to string for display
        command_str = ' '.join(str(x) for x in command)
        console.append_output(f"Executing command: {command_str}")

        # Create and start new thread for this instance
        thread = CommandThread(command)
        thread.commandOutput.connect(console.append_output)
        thread.commandFinished.connect(lambda: self.command_finished(console, instance_number))
        thread.start()
        
        # Store the thread
        self.command_threads[instance_number] = thread

    def command_finished(self, console, instance_number):
        """Handle command completion for a specific instance"""
        if instance_number in self.command_threads:
            thread = self.command_threads[instance_number]
            if thread and thread.isRunning():
                thread.terminate()
            console.append_output("Process stopped by user")
            del self.command_threads[instance_number]

    def stop_all_instances(self):
        """Stop all running instances"""
        try:
            for instance_number, thread in list(self.command_threads.items()):
                if thread and thread.isRunning():
                    # Terminate the thread
                    thread.terminate()
                    thread.wait()
                    
                    # Kill any remaining keyhunt processes
                    if platform.system() == "Windows":
                        try:
                            subprocess.run(["taskkill", "/f", "/im", "keyhunt.exe"], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
                        except Exception:
                            pass
                    else:
                        try:
                            subprocess.run(["pkill", "-f", "keyhunt"], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
                        except Exception:
                            pass
                    
                if instance_number <= len(self.keyhunt_frames):
                    self.keyhunt_frames[instance_number - 1].append_output("Process stopped by user")
            
            # Clear the thread dictionary
            self.command_threads.clear()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def split_range(self, start, end, num_splits):
        """Split a range into equal parts"""
        total_range = end - start
        chunk_size = total_range // num_splits
        remainder = total_range % num_splits
        
        ranges = []
        current_start = start
        
        for i in range(num_splits):
            extra = 1 if i < remainder else 0
            current_end = current_start + chunk_size + extra - 1
            if i == num_splits - 1:
                current_end = end
            ranges.append((current_start, current_end))
            current_start = current_end + 1
        
        return ranges

    def open_settings(self):
        from libs.theme_manager import SettingsDialog
        settings = SettingsDialog(self)
        settings.settings_changed.connect(self.apply_settings_changes)
        settings.exec()
        
    def apply_settings_changes(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        theme_name = config.get('theme', 'name', fallback='dark')
        theme_manager.set_theme(theme_name)
        stylesheet = theme_manager.get_stylesheet()
        QApplication.instance().setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(stylesheet)

    def exit_app(self):
        QApplication.quit()

    def open_telegram(self):
        webbrowser.open("https://t.me/TeamHunter_GUI")

    def about(self):
        about_dialog = AboutDialog(self)
        about_dialog.show()

    def add_credits(self, layout):
        labels_info = [
            {"text": "Made by Team Mizogg", "object_name": "madeby"},
            {"text": f"Full Version {version} ({current_platform})", "object_name": f"{current_platform}_version"},
            {"text": "© mizogg.com 2018 - 2025", "object_name": "copyright"},
        ]

        dot_labels = [QLabel("●", objectName=f"dot{i}") for i in range(1, 3)]

        credit_label = QHBoxLayout()
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_size = QSize(26, 26)
        iconred = QIcon(QPixmap(RED_ICON))

        def create_miz_git_mode_button():
            button = QPushButton(self)
            button.setToolTip('<span style="font-size: 10pt; font-weight: bold;">Help ME. Just by visiting my site https://mizogg.co.uk keep up those clicks. Mizogg Website and Information </span>')
            button.setStyleSheet("font-size: 12pt;")
            button.setIconSize(icon_size)
            button.setIcon(iconred)
            button.clicked.connect(open_website)
            return button

        self.miz_git_mode_button = create_miz_git_mode_button()
        self.miz_git_mode_button1 = create_miz_git_mode_button()
        
        credit_label.addWidget(self.miz_git_mode_button)

        mizlogo = QPixmap(f"{TITLE_ICON}")
        miz_label = QLabel(self)
        miz_label.setPixmap(mizlogo)
        miz_label1 = QLabel(self)
        miz_label1.setPixmap(mizlogo)

        credit_label.addWidget(miz_label)

        for info in labels_info:
            label = QLabel(info["text"])
            credit_label.addWidget(label)
            if dot_labels:
                dot_label = dot_labels.pop(0)
                credit_label.addWidget(dot_label)

        credit_label.addWidget(miz_label1)
        credit_label.addWidget(self.miz_git_mode_button1)
        layout.addLayout(credit_label)

    def create_threadGroupBox(self):
        self.keyhuntLayout = QVBoxLayout()
        threadGroupBox = QGroupBox(self)
        threadGroupBox.setTitle("Key Hunt Configuration")
        threadGroupBox.setStyleSheet("QGroupBox { border: 3px solid; padding: 15px; }")
        self.row1Layout = QHBoxLayout()
        self.threadLabel = QLabel("Number of CPUs:", self)
        self.row1Layout.addWidget(self.threadLabel)
        self.threadComboBox_key = QComboBox()
        
        # Initial CPU options based on current instances
        max_cpus_per_instance = self.cpu_count // self.current_instances
        if max_cpus_per_instance < 1:
            max_cpus_per_instance = 1
            
        for i in range(1, max_cpus_per_instance + 1):
            self.threadComboBox_key.addItem(str(i))
            
        self.threadComboBox_key.setCurrentIndex(0)
        self.threadComboBox_key.setToolTip(f'<span style="font-size: 10pt; font-weight: bold;"> Maximum CPUs per instance: {max_cpus_per_instance} (Total CPUs: {self.cpu_count})</span>')
        self.row1Layout.setStretchFactor(self.threadComboBox_key, 1)
        self.row1Layout.addWidget(self.threadComboBox_key)

        self.cryptoLabel = QLabel("Crypto:", self)
        self.row1Layout.addWidget(self.cryptoLabel)
        self.cryptoComboBox = QComboBox()
        self.cryptoComboBox.addItem("btc")
        self.cryptoComboBox.addItem("eth")
        self.cryptoComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Crypto Scanning Type BTC or ETH (default BTC)</span>')
        self.row1Layout.addWidget(self.cryptoComboBox)

        self.modeLabel = QLabel("Mode:", self)
        self.row1Layout.addWidget(self.modeLabel)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("address")
        self.modeComboBox.addItem("bsgs")
        self.modeComboBox.addItem("rmd160")
        self.modeComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Keyhunt can work in diferent ways at different speeds. The current availables modes are:</span>')
        self.row1Layout.addWidget(self.modeComboBox)
        self.move_modeLabel = QLabel("Movement Mode:", self)
        self.row1Layout.addWidget(self.move_modeLabel)
        self.move_modeEdit = QComboBox(self)
        self.move_modeEdit.addItem("random")
        self.move_modeEdit.addItem("sequential")
        self.move_modeEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Direction of Scan </span>')
        self.row1Layout.addWidget(self.move_modeEdit)
        self.modeComboBox.currentIndexChanged.connect(self.update_movement_mode_options)
        self.strideLabel = QLabel("Stride/Jump/Magnitude:", self)
        self.row1Layout.addWidget(self.strideLabel)
        self.strideLineEdit = QLineEdit("1")
        self.strideLineEdit.setPlaceholderText('10000')
        self.strideLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Increment by NUMBER (Not required BSGS Mode both)</span>')
        self.row1Layout.addWidget(self.strideLineEdit)
        self.kLabel = QLabel(" K factor:", self)
        self.kLabel.setToolTip('<span style="font-size: 10pt; font-weight: bold;">BSGS Modes only</span>')
        self.row1Layout.addWidget(self.kLabel)
        self.kComboBox = QComboBox()
        self.kComboBox.addItems(['1', '4', '8', '16', '24', '32', '64', '128', '256', '512', '756', '1024', '2048'])
        self.kComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold;">1, 32, 64, 128, 256, 512, 1024</span>')
        self.row1Layout.addWidget(self.kComboBox)
        self.keyhuntLayout.addLayout(self.row1Layout)
        self.nValueLabel = QLabel("N Value:", self)
        self.row1Layout.addWidget(self.nValueLabel)
        self.nValueLineEdit = QLineEdit(self)
        self.nValueLineEdit.setPlaceholderText('0x1000000000000000')
        self.row1Layout.addWidget(self.nValueLineEdit)
        self.row1Layout.setStretchFactor(self.nValueLineEdit, 2)
        
        threadGroupBox.setLayout(self.keyhuntLayout)
        return threadGroupBox

    def create_keyspaceGroupBox(self):
        keyspaceGroupBox = QGroupBox(self)
        keyspaceGroupBox.setTitle("Key Space Configuration")
        keyspaceGroupBox.setStyleSheet("QGroupBox { border: 3px solid; padding: 5px; }")
        keyspaceMainLayout = QVBoxLayout(keyspaceGroupBox)
        keyspaceLayout = QHBoxLayout()
        keyspaceLabel = QLabel("Key Space:")
        keyspaceLayout.addWidget(keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("400000000000000000:7FFFFFFFFFFFFFFFFF")
        self.keyspaceLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Type in your own HEX Range separated with : </span>')
        keyspaceLayout.addWidget(self.keyspaceLineEdit)
        keyspaceMainLayout.addLayout(keyspaceLayout)
        keyspacerange_layout = QHBoxLayout()
        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(71)
        self.keyspace_slider.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Drag Left to Right to Adjust Range (Address Mode 1-160 BSGS Mode 50-160)</span>')
        keyspacerange_layout1 = QHBoxLayout()
        keyspacerange_layout1.addWidget(self.keyspace_slider)
        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        self.bitsLabel = QLabel("Bits:", self)
        self.bitsLineEdit = QLineEdit(self)
        self.bitsLineEdit.setText("71")
        self.bitsLineEdit.textChanged.connect(self.updateSliderAndRanges)
        keyspacerange_layout1.addWidget(self.bitsLabel)
        keyspacerange_layout1.addWidget(self.bitsLineEdit)
        keyspaceMainLayout.addLayout(keyspacerange_layout)
        keyspaceMainLayout.addLayout(keyspacerange_layout1)
        return keyspaceGroupBox

    def update_keyspace_range(self, value):
        start_range = 2 ** (value - 1)
        end_range = 2 ** value - 1
        self.keyspaceLineEdit.setText(f"{start_range:X}:{end_range:X}")
        self.bitsLineEdit.setText(str(value))

    def updateSliderAndRanges(self, text):
        try:
            bits = int(text)
            mode = self.modeComboBox.currentText()
            if mode == "bsgs":
                bits = max(50, min(bits, 256))
            else:
                bits = max(1, min(bits, 256))
            
            if bits == 256:
                start_range = "8000000000000000000000000000000000000000000000000000000000000000"
                end_range = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140"
            else:
                start_range = 2 ** (bits - 1)
                end_range = 2 ** bits - 1
                start_range = f"{start_range:X}"
                end_range = f"{end_range:X}"
            
            self.keyspace_slider.setValue(bits)
            self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
        
        except ValueError:
            range_message = "Range should be in Bit 1-256"
            QMessageBox.information(self, "Range Error", range_message)

    def range_check(self):
        self.range_dialog = RangeDialog()
        self.range_dialog.show()

    def create_outputFileGroupBox(self):
        outputFileGroupBox = QGroupBox(self)
        outputFileGroupBox.setTitle("File Configuration and Look Type (Compressed/Uncompressed)")
        outputFileGroupBox.setStyleSheet("QGroupBox { border: 3px solid; padding: 5px; }")
        outputFileLayout = QHBoxLayout(outputFileGroupBox)
        self.lookLabel = QLabel("Look Type:", self)
        outputFileLayout.addWidget(self.lookLabel)
        self.lookComboBox = QComboBox()
        self.lookComboBox.addItem("compress")
        self.lookComboBox.addItem("uncompress")
        self.lookComboBox.addItem("both")
        self.lookComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Search for compressed keys (default). Can be used with also search uncompressed keys  </span>')
        outputFileLayout.addWidget(self.lookComboBox)
        self.inputFileLabel = QLabel("Input File:", self)
        outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit("btc.txt", self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your BTC database')
        self.inputFileLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Type the Name of database txt file or Browse location </span>')
        outputFileLayout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.setStyleSheet("")
        self.inputFileButton.clicked.connect(self.browse_input_file)
        self.inputFileButton.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Type the Name of database txt file or Browse location </span>')
        outputFileLayout.addWidget(self.inputFileButton)
        self.found_progButton = QPushButton("🔥 Check if Found 🔥")
        self.found_progButton.clicked.connect(self.found_prog)
        self.found_progButton.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Click Here to See if your a Winner </span>')
        outputFileLayout.addWidget(self.found_progButton)
        self.save_progButton = QPushButton("💾 Check Progress 💾")
        self.save_progButton.clicked.connect(self.check_prog)
        self.save_progButton.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Check if the Progress file exists Choose to Keep or Remove </span>')
        outputFileLayout.addWidget(self.save_progButton)
        self.flagQCheckBox = QCheckBox("Quite mode", self)
        self.flagQCheckBox.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Quiet the thread output Only Displays speed </span>')
        outputFileLayout.addWidget(self.flagQCheckBox)
        self.range_progButton = QPushButton("💾 Range Tools 💾")
        self.range_progButton.clicked.connect(self.range_check)
        self.range_progButton.setToolTip('<span style="font-size: 10pt; font-weight: bold;"> Ranges ....... </span>')
        outputFileLayout.addWidget(self.range_progButton)
        return outputFileGroupBox

    def update_kComboBox_status(self):
        mode = self.modeComboBox.currentText()
        if mode == "address" or mode == "rmd160":
            self.kComboBox.setDisabled(True)
            self.kComboBox.setStyleSheet("")
            self.nValueLineEdit.setDisabled(True)
            self.nValueLineEdit.setStyleSheet("")
        else:
            self.kComboBox.setEnabled(True)
            self.kComboBox.setStyleSheet("")
            self.nValueLineEdit.setEnabled(True)
            self.nValueLineEdit.setStyleSheet("")

    def update_movement_mode_options(self):
        mode = self.modeComboBox.currentText()
        if mode == "bsgs":
            self.move_modeEdit.clear()
            self.move_modeEdit.addItem("sequential")
            self.move_modeEdit.addItem("backward")
            self.move_modeEdit.addItem("both")
            self.move_modeEdit.addItem("random")
            self.move_modeEdit.addItem("dance")
            self.keyspace_slider.setMinimum(50)
        else:
            self.move_modeEdit.clear()
            self.move_modeEdit.addItem("random")
            self.move_modeEdit.addItem("sequential")
            self.keyspace_slider.setMinimum(1)

    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)

    def found_prog(self):
        file_path = 'KEYFOUNDKEYFOUND.txt'
        self.read_and_display_file(file_path, "😀😀 Keyhunt File found. Check for Winners 😀😀.", "😞😞No Winners Yet 😞😞")

    def read_and_display_file(self, file_path, success_message, error_message):
        for console in self.keyhunt_frames:
            console.append_output(f"Attempting to read file: {file_path}")
            try:
                if not os.path.exists(file_path):
                    console.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
                    return None
                    
                with open(file_path, 'r') as file:
                    output_from_text = file.read()
                    console.append_output(success_message)
                    console.append_output(output_from_text)
                    return output_from_text
            except FileNotFoundError:
                console.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
                return None
            except Exception as e:
                console.append_output(f"An error occurred: {str(e)}")
                return None

    def check_prog(self):
        directory = '.'
        dat_files = glob.glob(os.path.join(directory, '*.dat'))
        
        if dat_files:
            file_path = dat_files[0]
            custom_dialog = ProgressDialog(self)
            choice = custom_dialog.exec()
            if choice == QDialog.DialogCode.Accepted:
                os.remove(file_path)
                for console in self.keyhunt_frames:
                    console.append_output("Progress deleted successfully.")
            else:
                for console in self.keyhunt_frames:
                    console.append_output("Progress kept.")
        else:
            for console in self.keyhunt_frames:
                console.append_output("Progress not found.")

    def adjust_size(self):
        """Adjust the window size based on the grid layout"""
        grid_size = self.grid_widget.sizeHint()
        # Add some padding for the shared configuration
        config_height = self.shared_config.sizeHint().height()
        self.resize(max(800, grid_size.width()), max(600, grid_size.height() + config_height + 100))

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop all instances first
            self.stop_all_instances()
            
            # Additional cleanup
            if platform.system() == "Windows":
                try:
                    subprocess.run(["taskkill", "/f", "/im", "keyhunt.exe"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                except Exception:
                    pass
            else:
                try:
                    subprocess.run(["pkill", "-f", "keyhunt"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                except Exception:
                    pass
                
            event.accept()
        except Exception as e:
            print(f"Error during window close: {str(e)}")
            event.accept()

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.stop_all_instances()
        except:
            pass


if __name__ == "__main__":
    app = QApplication([])
    config = configparser.ConfigParser()
    
    # Check if config.ini exists, if not create it with default settings
    if not os.path.exists('config.ini'):
        config['theme'] = {'name': 'dark'}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    
    config.read('config.ini')
    theme_name = config.get('theme', 'name', fallback='dark')
    theme_manager.set_theme(theme_name)
    stylesheet = theme_manager.get_stylesheet()
    app.setStyleSheet(stylesheet)
    window = GUI()
    window.show()
    app.exec()