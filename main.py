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

ICO_ICON = "images/miz.ico"
TITLE_ICON = "images/mizogglogo.png"
RED_ICON = "images/mizogg-eyes.png"
version = '1.1'
current_platform = platform.system()

def open_website(self):
    webbrowser.open("https://mizogg.co.uk")

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        self.grid_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.grid_widget)
        main_layout.addWidget(self.grid_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        menubar = self.menuBar()

        def add_menu_action(menu, text, function):
            action = QAction(text, self)
            action.triggered.connect(function)
            menu.addAction(action)

        file_menu = menubar.addMenu("File")
        add_menu_action(file_menu, "New Window", self.new_window)
        file_menu.addSeparator()
        add_menu_action(file_menu, "Quit", self.exit_app)

        instances_menu = menubar.addMenu("Instances")
        add_menu_action(instances_menu, "1", lambda: self.update_grid_layout(1))
        add_menu_action(instances_menu, "2", lambda: self.update_grid_layout(2))
        add_menu_action(instances_menu, "4", lambda: self.update_grid_layout(4))
        add_menu_action(instances_menu, "6", lambda: self.update_grid_layout(6))
        add_menu_action(instances_menu, "8", lambda: self.update_grid_layout(8))

        help_menu = menubar.addMenu("Help")
        add_menu_action(help_menu, "Help Telegram Group", self.open_telegram)
        add_menu_action(help_menu, "About", self.about)

        labels_info = [
            {"text": "Made by Team Mizogg", "object_name": "madeby"},
            {"text": f"Full Version {version} ({current_platform})", "object_name": f"{current_platform}_version"},
            {"text": "© mizogg.com 2018 - 2024", "object_name": "copyright"},
        ]

        dot_labels = [QLabel("●", objectName=f"dot{i}") for i in range(1, 3)]

        credit_label = QHBoxLayout()
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_size = QSize(26, 26)
        iconred = QIcon(QPixmap(RED_ICON))

        def create_miz_git_mode_button():
            button = QPushButton(self)
            button.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;">Help ME. Just by visiting my site https://mizogg.co.uk keep up those clicks. Mizogg Website and Information </span>')
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
        main_layout.addLayout(credit_label)

        self.setGeometry(60, 100, 400, 300)
        self.setWindowTitle("KeyHunter Puzzles GUI")
        self.setWindowIcon(QIcon(f"{ICO_ICON}"))
        self.update_grid_layout(1)

    def new_window(self):
        new_gui = GUI()
        new_gui.show()

    def exit_app(self):
        QApplication.quit()

    def open_telegram(self):
        webbrowser.open("https://t.me/TeamHunter_GUI")

    def about(self):
        about_dialog = AboutDialog(self)
        about_dialog.show()

    def update_grid_layout(self, num_instances):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

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

        for row in range(rows):
            for col in range(cols):
                instance = KeyHuntFrame(row, col)
                self.grid_layout.addWidget(instance, row, col)

        self.grid_widget.setLayout(self.grid_layout)
        self.adjust_size()

    def adjust_size(self):
        grid_size = self.grid_widget.sizeHint()
        self.resize(grid_size.width(), grid_size.height())

class KeyHuntFrame(QMainWindow):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.cpu_count = multiprocessing.cpu_count()
        self.scanning = False
        self.user_stopped = False
        self.timer = QTimer(self)
        self.commandThread = None
        
        main_layout = QVBoxLayout()

        keyhunt_config = self.create_threadGroupBox()
        main_layout.addWidget(keyhunt_config)
        
        Keysapce_config = self.create_keyspaceGroupBox()
        main_layout.addWidget(Keysapce_config)

        outputFile_config = self.create_outputFileGroupBox()
        main_layout.addWidget(outputFile_config)

        buttonLayout = QHBoxLayout()
        start_button = self.create_start_button()
        stop_button = self.create_stop_button()

        buttonLayout.addWidget(start_button)
        buttonLayout.addWidget(stop_button)

        main_layout.addLayout(buttonLayout)

        self.consoleWindow = ConsoleWindow(self)
        main_layout.addWidget(self.consoleWindow)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.kComboBox.setDisabled(True)
        self.kComboBox.setStyleSheet("QComboBox::disabled { background-color: darkgray; color: black; }")
        self.nValueLineEdit.setDisabled(True)
        self.nValueLineEdit.setStyleSheet("QLineEdit:disabled { background-color: darkgray; color: black; }")
        self.modeComboBox.currentIndexChanged.connect(self.update_kComboBox_status)

    def create_keyspaceGroupBox(self):
        keyspaceGroupBox = QGroupBox(self)
        keyspaceGroupBox.setTitle("Key Space Configuration")
        keyspaceGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        keyspaceMainLayout = QVBoxLayout(keyspaceGroupBox)
        keyspaceLayout = QHBoxLayout()
        keyspaceLabel = QLabel("Key Space:")
        keyspaceLayout.addWidget(keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("2000000000000000:3FFFFFFFFFFFFFFFF")
        self.keyspaceLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Type in your own HEX Range separated with : </span>')
        keyspaceLayout.addWidget(self.keyspaceLineEdit)
        keyspaceMainLayout.addLayout(keyspaceLayout)
        keyspacerange_layout = QHBoxLayout()
        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)
        self.keyspace_slider.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Drag Left to Right to Adjust Range (Address Mode 1-160 BSGS Mode 50-160)</span>')
        keyspacerange_layout1 = QHBoxLayout()
        keyspacerange_layout1.addWidget(self.keyspace_slider)
        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        self.bitsLabel = QLabel("Bits:", self)
        self.bitsLineEdit = QLineEdit(self)
        self.bitsLineEdit.setText("66")
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


    def create_stop_button(self):
        stopButton = QPushButton("Stop KeyHunt", self)
        stopButton.clicked.connect(self.stop_hunt)
        stopButton.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Stop Keyhunt  </span>')
        stopButton.setStyleSheet(
            "QPushButton { font-size: 12pt; background-color: #1E1E1E; color: white; }"
            "QPushButton:hover { font-size: 12pt; background-color: #5D6062; color: white; }"
        )
        return stopButton

    def create_start_button(self):
        StartButton = QPushButton("Start KeyHunt", self)
        StartButton.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Start Keyhunt </span>')
        StartButton.setStyleSheet(
                "QPushButton { font-size: 12pt; background-color: #E7481F; color: white; }"
                "QPushButton:hover { font-size: 12pt; background-color: #A13316; color: white; }"
            )
        StartButton.clicked.connect(self.run_keyhunt)
        return StartButton

    def create_outputFileGroupBox(self):
        outputFileGroupBox = QGroupBox(self)
        outputFileGroupBox.setTitle("File Configuration and Look Type (Compressed/Uncompressed)")
        outputFileGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        outputFileLayout = QHBoxLayout(outputFileGroupBox)
        self.lookLabel = QLabel("Look Type:", self)
        outputFileLayout.addWidget(self.lookLabel)
        self.lookComboBox = QComboBox()
        self.lookComboBox.addItem("compress")
        self.lookComboBox.addItem("uncompress")
        self.lookComboBox.addItem("both")
        self.lookComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Search for compressed keys (default). Can be used with also search uncompressed keys  </span>')
        outputFileLayout.addWidget(self.lookComboBox)
        self.inputFileLabel = QLabel("Input File:", self)
        outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit("btc.txt", self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your BTC database')
        self.inputFileLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Type the Name of database txt file or Browse location </span>')
        outputFileLayout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.setStyleSheet("color: #E7481F;")
        self.inputFileButton.clicked.connect(self.browse_input_file)
        self.inputFileButton.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Type the Name of database txt file or Browse location </span>')
        outputFileLayout.addWidget(self.inputFileButton)
        self.found_progButton = QPushButton("🔥 Check if Found 🔥")
        self.found_progButton.clicked.connect(self.found_prog)
        self.found_progButton.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Click Here to See if your a Winner </span>')
        outputFileLayout.addWidget(self.found_progButton)
        self.save_progButton = QPushButton("💾 Check Progress 💾")
        self.save_progButton.clicked.connect(self.check_prog)
        self.save_progButton.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Check if the Progress file exists Choose to Keep or Remove </span>')
        outputFileLayout.addWidget(self.save_progButton)
        self.flagQCheckBox = QCheckBox("Quite mode", self)
        self.flagQCheckBox.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Quiet the thread output Only Displays speed </span>')
        outputFileLayout.addWidget(self.flagQCheckBox)
        return outputFileGroupBox

    def update_kComboBox_status(self):
        mode = self.modeComboBox.currentText()
        if mode == "address" or mode == "rmd160":
            self.kComboBox.setDisabled(True)
            self.kComboBox.setStyleSheet("QComboBox::disabled { background-color: darkgray; color: black; }")
            self.nValueLineEdit.setDisabled(True)
            self.nValueLineEdit.setStyleSheet("QLineEdit:disabled { background-color: darkgray; color: black; }")
        else:
            self.kComboBox.setEnabled(True)
            self.kComboBox.setStyleSheet("")
            self.nValueLineEdit.setEnabled(True)
            self.nValueLineEdit.setStyleSheet("")

    def create_threadGroupBox(self):
        self.keyhuntLayout = QVBoxLayout()
        threadGroupBox = QGroupBox(self)
        threadGroupBox.setTitle("Key Hunt Configuration")
        threadGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 15px; }")
        self.row1Layout = QHBoxLayout()
        self.threadLabel = QLabel("Number of CPUs:", self)
        self.row1Layout.addWidget(self.threadLabel)
        self.threadComboBox_key = QComboBox()
        for i in range(1, self.cpu_count + 1):
            self.threadComboBox_key.addItem(str(i))
        self.threadComboBox_key.setCurrentIndex(2)
        self.threadComboBox_key.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Pick Your ammount to CPUs to start scaning with</span>')
        self.row1Layout.setStretchFactor(self.threadComboBox_key, 1)
        self.row1Layout.addWidget(self.threadComboBox_key)

        self.cryptoLabel = QLabel("Crypto:", self)
        self.row1Layout.addWidget(self.cryptoLabel)
        self.cryptoComboBox = QComboBox()
        self.cryptoComboBox.addItem("btc")
        self.cryptoComboBox.addItem("eth")
        self.cryptoComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Crypto Scanning Type BTC or ETH (default BTC)</span>')
        self.row1Layout.addWidget(self.cryptoComboBox)

        self.modeLabel = QLabel("Mode:", self)
        self.row1Layout.addWidget(self.modeLabel)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("address")
        self.modeComboBox.addItem("bsgs")
        self.modeComboBox.addItem("rmd160")
        self.modeComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Keyhunt can work in diferent ways at different speeds. The current availables modes are:</span>')
        self.row1Layout.addWidget(self.modeComboBox)
        self.move_modeLabel = QLabel("Movement Mode:", self)
        self.row1Layout.addWidget(self.move_modeLabel)
        self.move_modeEdit = QComboBox(self)
        self.move_modeEdit.addItem("sequential")
        self.move_modeEdit.addItem("random")
        self.move_modeEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Direction of Scan </span>')
        self.row1Layout.addWidget(self.move_modeEdit)
        self.modeComboBox.currentIndexChanged.connect(self.update_movement_mode_options)
        self.strideLabel = QLabel("Stride/Jump/Magnitude:", self)
        self.row1Layout.addWidget(self.strideLabel)
        self.strideLineEdit = QLineEdit("1")
        self.strideLineEdit.setPlaceholderText('10000')
        self.strideLineEdit.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;"> Increment by NUMBER (Not required BSGS Mode both)</span>')
        self.row1Layout.addWidget(self.strideLineEdit)
        self.kLabel = QLabel(" K factor:", self)
        self.kLabel.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;">BSGS Modes only</span>')
        self.row1Layout.addWidget(self.kLabel)
        self.kComboBox = QComboBox()
        self.kComboBox.addItems(['1', '4', '8', '16', '24', '32', '64', '128', '256', '512', '756', '1024', '2048'])
        self.kComboBox.setToolTip('<span style="font-size: 10pt; font-weight: bold; color: black;">1, 32, 64, 128, 256, 512, 1024</span>')
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
    
    def found_prog(self):
        file_path = 'KEYFOUNDKEYFOUND.txt'
        self.read_and_display_file(file_path, "😀😀 Keyhunt File found. Check for Winners 😀😀.", "😞😞No Winners Yet 😞😞")


    def read_and_display_file(self, file_path, success_message, error_message):
        self.consoleWindow.append_output(f"Attempting to read file: {file_path}")
        try:
            if not os.path.exists(file_path):
                self.consoleWindow.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
                return None
                
            with open(file_path, 'r') as file:
                output_from_text = file.read()
                self.consoleWindow.append_output(success_message)
                self.consoleWindow.append_output(output_from_text)
                return output_from_text
        except FileNotFoundError:
            self.consoleWindow.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
            return None
        except Exception as e:
            self.consoleWindow.append_output(f"An error occurred: {str(e)}")
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
                self.consoleWindow.append_output("Progress deleted successfully.")
            else:
                self.consoleWindow.append_output("Progress kept.")
        else:
            self.consoleWindow.append_output("Progress not found.")

    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)

    def run_keyhunt(self):
        command = self.construct_command_key()
        self.execute_command('"' + '" "'.join(command) + '"')

    def construct_command_key(self):
        mode = self.modeComboBox.currentText().strip()
        thread_count_key = int(self.threadComboBox_key.currentText())
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyhunt")

        if platform.system() == "Windows":
            command = [os.path.join(base_path, "keyhunt.exe"), "-m", mode, "-t", str(thread_count_key)]
        elif platform.system() == "Linux":
            command = [os.path.join(base_path, "keyhunt"), "-m", mode, "-t", str(thread_count_key)]
        else:
            raise NotImplementedError(f"Unsupported platform: {platform.system()}")

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

        keyspace = self.keyspaceLineEdit.text().strip()
        if keyspace:
            start_range, end_range = keyspace.split(':')
            start_range_hex = start_range
            end_range_hex = end_range
            command.extend(["-r", f"{start_range_hex}:{end_range_hex}"])

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
            self.move_modeEdit.addItem("sequential")
            self.move_modeEdit.addItem("random")
            self.keyspace_slider.setMinimum(1)

    @pyqtSlot()
    def execute_command(self, command):
        if self.scanning:
            return

        self.scanning = True

        if self.commandThread and self.commandThread.isRunning():
            self.commandThread.terminate()

        self.commandThread = CommandThread(command)
        self.commandThread.commandOutput.connect(self.consoleWindow.append_output)
        self.commandThread.commandFinished.connect(self.command_finished)
        self.commandThread.start()
        self.timer.start(100)

    def stop_hunt(self):
        if self.commandThread and self.commandThread.isRunning():
            self.user_stopped = True
            if platform.system() == "Windows":
                subprocess.Popen(["taskkill", "/F", "/T", "/PID", str(self.commandThread.process.pid)])
            else:
                os.killpg(os.getpgid(self.commandThread.process.pid), signal.SIGTERM)
            
            self.timer.stop()
            self.scanning = False

    @pyqtSlot(int)
    def command_finished(self, returncode):
        self.timer.stop()
        self.scanning = False

        if self.user_stopped:
            self.consoleWindow.append_output("Process has been stopped by the user")
        elif returncode == 0:
            self.consoleWindow.append_output("Command execution finished successfully")
        else:
            self.consoleWindow.append_output("Command execution failed")

        self.user_stopped = False

    def closeEvent(self, event):
        self.stop_hunt()
        event.accept()

def main():
    app = QApplication([])
    window = GUI()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()