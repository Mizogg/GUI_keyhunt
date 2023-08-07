import sys
import os
import re
import signal
import platform
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import multiprocessing
import subprocess

mizogg = f'''
 Made by Mizogg Version 3.2  © mizogg.co.uk 2018 - 2023      {f"[>] Running with Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"}
'''

class CommandThread(QThread):
    commandOutput = pyqtSignal(str)
    commandFinished = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        self.commandOutput.emit(self.command)
        self.process = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in self.process.stdout:
            output = line.strip()
            self.commandOutput.emit(output)
        self.process.stdout.close()
        self.commandFinished.emit(self.process.wait())

class ConsoleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.consoleOutput = QPlainTextEdit(self)
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setFont(QFont("Courier"))
        self.layout.addWidget(self.consoleOutput)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.consoleOutput.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @pyqtSlot(int)
    def update_console_style(self, index):
        if index == 1:
            self.consoleOutput.setStyleSheet("background-color: white; color: purple; font-size: 18px;")
        elif index == 2:
            self.consoleOutput.setStyleSheet("background-color: black; color: green; font-size: 18px;")
        elif index == 3:
            self.consoleOutput.setStyleSheet("background-color: blue; color: white; font-size: 18px;")
        elif index == 4:
            self.consoleOutput.setStyleSheet("background-color: blue; color: yellow; font-size: 18px;")
        elif index == 5:
            self.consoleOutput.setStyleSheet("background-color: red; color: black; font-size: 18px;")
        elif index == 6:
            self.consoleOutput.setStyleSheet("background-color: black; color: yellow; font-size: 18px;")
        else:
            self.consoleOutput.setStyleSheet("background-color: white; color: red; font-size: 18px;")
            
    @pyqtSlot(str)
    def append_output(self, output):
        self.consoleOutput.appendPlainText(output)

class KnightRiderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.position = 0
        self.direction = 1
        self.lightWidth = 20
        self.lightHeight = 10
        self.lightSpacing = 10
        self.lightColor = QColor(255, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def startAnimation(self):
        self.timer.start(5)

    def stopAnimation(self):
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(12):
            lightX = self.position + i * (self.lightWidth + self.lightSpacing)
            lightRect = QRect(lightX, 0, self.lightWidth, self.lightHeight)
            painter.setBrush(self.lightColor)
            painter.drawRoundedRect(lightRect, 5, 5)

    def update(self):
        self.position += self.direction
        if self.position <= 0 or self.position >= self.width() - self.lightWidth - self.lightSpacing:
            self.direction *= -1
        self.repaint()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyhunt GUI @ github.com/Mizogg")
        self.setGeometry(50, 50, 1700, 500)
        self.process = None
        self.commandThread = None
        self.scanning = False
        self.initUI()
        
    def initUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        cpu_count = multiprocessing.cpu_count()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setStyleSheet(
    """
    QMainWindow {
        background-image: url(rsz_alberto.jpg);
        background-repeat: no-repeat;
        background-position: top left;
    }
    """
)
        main_layout = QVBoxLayout()
        welcome_label = QLabel("Welcome  Alberto's KeyHunt GUI made by Mizogg")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: purple;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)
        line1_label = QLabel('Tool for hunt privatekeys for crypto currencies that use secp256k1 elliptic curve')
        line1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line1_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        main_layout.addWidget(line1_label)
        line2_label = QLabel('Address hunting MENU RMD160 MENU. XPoint Menu')
        line2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line2_label.setStyleSheet("font-size: 14px; color: blue;")
        main_layout.addWidget(line2_label)

        self.threadLayout = QHBoxLayout()
        self.threadGroupBox = QGroupBox(self)
        self.threadGroupBox.setTitle("Thread Configuration Start/Stop or open in new Window")
        self.threadGroupBox.setStyleSheet("QGroupBox { border: 3px solid green; padding: 15px; }")

        self.threadLayout = QHBoxLayout(self.threadGroupBox)
        self.threadLabel = QLabel("Number of CPUs:", self)
        self.threadLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.threadLayout.addWidget(self.threadLabel)
        self.threadComboBox = QComboBox()
        for i in range(1, cpu_count + 1):
            self.threadComboBox.addItem(str(i))
        self.threadComboBox.setCurrentIndex(2)
        self.threadLayout.addWidget(self.threadComboBox)
        self.StartButton = QPushButton("Start KeyHunt", self)
        self.StartButton.setStyleSheet("color: green;")
        self.StartButton.clicked.connect(self.run_keyhunt)
        self.threadLayout.addWidget(self.StartButton)
        self.stopButton = QPushButton("Stop Keyhunt", self)
        self.stopButton.setStyleSheet("color: red;")
        self.stopButton.clicked.connect(self.stop_keyhunt)
        self.threadLayout.addWidget(self.stopButton)
        self.NEWButton = QPushButton("New window", self)
        self.NEWButton.setStyleSheet("color: orange;")
        self.NEWButton.clicked.connect(self.new_window)
        self.threadLayout.addWidget(self.NEWButton)

        self.optionsGroupBox = QGroupBox(self)
        self.optionsGroupBox.setTitle("Crypto Type / Search Mode (address,xpoint,rmd160,bsgs,vanity) / Movement Mode (Sequential/Random) (BSGS Mode all movement options)")
        self.optionsGroupBox.setStyleSheet("QGroupBox { border: 2px solid green; padding: 13px; }")

        self.optionsLayout2 = QHBoxLayout(self.optionsGroupBox)

        options_layout = QHBoxLayout()
        self.cryptoLabel = QLabel("Crypto:", self)
        options_layout.addWidget(self.cryptoLabel)
        self.cryptoComboBox = QComboBox()
        self.cryptoComboBox.addItem("btc")
        self.cryptoComboBox.addItem("eth")
        options_layout.addWidget(self.cryptoComboBox)

        self.modeLabel = QLabel("Mode:", self)
        options_layout.addWidget(self.modeLabel)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("address")
        self.modeComboBox.addItem("rmd160")
        self.modeComboBox.addItem("xpoint")
        self.modeComboBox.addItem("bsgs")
        #self.modeComboBox.addItem("vanity")
        options_layout.addWidget(self.modeComboBox)

        self.lookLabel = QLabel("Look Type:", self)
        options_layout.addWidget(self.lookLabel)
        self.lookComboBox = QComboBox()
        self.lookComboBox.addItem("compress")
        self.lookComboBox.addItem("uncompress")
        self.lookComboBox.addItem("both")
        options_layout.addWidget(self.lookComboBox)

        self.move_modeLabel = QLabel("Movement Mode:", self)
        options_layout.addWidget(self.move_modeLabel)
        self.move_modeEdit = QComboBox(self)
        self.move_modeEdit.addItem("random")
        self.move_modeEdit.addItem("sequential")
        options_layout.addWidget(self.move_modeEdit)
        self.modeComboBox.currentIndexChanged.connect(self.update_movement_mode_options)

        self.strideLabel = QLabel("Stride/Jump/Magnitude:", self)
        options_layout.addWidget(self.strideLabel)
        self.strideLineEdit = QLineEdit(self)
        options_layout.addWidget(self.strideLineEdit)

        self.optionsLayout2.addLayout(options_layout)
        self.optionsGroupBox1 = QGroupBox(self)
        self.optionsGroupBox1.setTitle("Options Range Space")
        self.optionsGroupBox1.setStyleSheet("QGroupBox { border: 2px solid green; padding: 13px; }")

        self.optionsLayout = QHBoxLayout(self.optionsGroupBox1)

        options_layout2 = QHBoxLayout()
        
        self.keyspaceLabel = QLabel("Key Space:", self)
        options_layout2.addWidget(self.keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("20000000000000000:3ffffffffffffffff", self)
        self.keyspaceLineEdit.setPlaceholderText('Example range for 66 = 20000000000000000:3ffffffffffffffff')
        
        
        keyspacerange_layout = QVBoxLayout()
        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)
        keyspacerange_layout.addWidget(self.keyspaceLineEdit)
        keyspacerange_layout.addWidget(self.keyspace_slider)
        options_layout2.addLayout(keyspacerange_layout)
        options_layout2.setStretchFactor(keyspacerange_layout, 5)
        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)

        self.bitsLabel = QLabel("Bits:", self)
        options_layout2.addWidget(self.bitsLabel)
        self.bitsLineEdit = QLineEdit(self)
        options_layout2.addWidget(self.bitsLineEdit)
        options_layout2.setStretchFactor(self.bitsLineEdit, 1)

        self.kValueLabel = QLabel("K Value:", self)
        options_layout2.addWidget(self.kValueLabel)
        self.kValueLineEdit = QLineEdit(self)
        options_layout2.addWidget(self.kValueLineEdit)
        options_layout2.setStretchFactor(self.kValueLineEdit, 1)
        
        self.nValueLabel = QLabel("N Value:", self)
        options_layout2.addWidget(self.nValueLabel)
        self.nValueLineEdit = QLineEdit(self)
        self.nValueLineEdit.setPlaceholderText('0x1000000000000000')
        options_layout2.addWidget(self.nValueLineEdit)
        options_layout2.setStretchFactor(self.nValueLineEdit, 2)

        self.optionsLayout.addLayout(options_layout2)

        self.outputFileGroupBox = QGroupBox(self)
        self.outputFileGroupBox.setTitle("File Configuration")
        self.outputFileGroupBox.setStyleSheet("QGroupBox { border: 2px solid green; padding: 13px; }")

        self.outputFileLayout = QHBoxLayout(self.outputFileGroupBox)
        self.inputFileLabel = QLabel("Specify file name with addresses or xpoints or uncompressed public keys:", self)
        self.outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit('btc.txt', self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your File')
        self.outputFileLayout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.clicked.connect(self.browse_input_file)
        self.outputFileLayout.addWidget(self.inputFileButton)
        self.optionsGroupBox3 = QGroupBox(self)
        self.optionsGroupBox3.setTitle("Additional Options (Only for address, rmd160 and vanity)")
        self.optionsGroupBox3.setStyleSheet("QGroupBox { border: 2px solid green; padding: 13px; }")
        self.optionsLayout3 = QVBoxLayout(self.optionsGroupBox3)
        options_layout3 = QHBoxLayout()
        self.minikeyBaseLabel = QLabel("Minikey Base:", self)
        options_layout3.addWidget(self.minikeyBaseLabel)
        self.minikeyBaseEdit = QLineEdit('SRPqx8QiwnW4WNWnTVa2W5', self)
        options_layout3.addWidget(self.minikeyBaseEdit)
        self.minikeyBasebutton = QCheckBox("Enable Minikey", self)
        self.minikeyBasebutton.setCheckable(True)
        self.minikeyBasebutton.setChecked(False)
        self.minikeyBasebutton.toggled.connect(self.update_mini_search)
        self.minikeyBaseEdit.setEnabled(False)
        options_layout3.addWidget(self.minikeyBasebutton)
        
        self.endomorphismCheckBox = QCheckBox("Enable Endomorphism", self)
        options_layout3.addWidget(self.endomorphismCheckBox)
        options_layout4 = QHBoxLayout()
        self.alphabetLabel = QLabel("Alphabet:", self)
        options_layout4.addWidget(self.alphabetLabel)
        self.alphabetLineEdit = QLineEdit('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', self)
        options_layout4.addWidget(self.alphabetLineEdit)
        self.enablealphabetButton = QCheckBox("Enable Alphabet", self)
        self.enablealphabetButton.setCheckable(True)
        self.enablealphabetButton.setChecked(False)
        self.enablealphabetButton.toggled.connect(self.update_alphabet_search)
        self.alphabetLineEdit.setEnabled(False)
        options_layout4.addWidget(self.enablealphabetButton)
        self.optionsLayout3.addLayout(options_layout3)
        self.optionsLayout3.addLayout(options_layout4)
        vanity_layout = QHBoxLayout()

        self.Vanity_Label = QLabel("Vanity Address to search:", self)
        vanity_layout.addWidget(self.Vanity_Label)
        self.prefixLineEdit = QLineEdit("1Love 1Mizogg 1CatsandDogs", self)
        vanity_layout.addWidget(self.prefixLineEdit)
        self.enableVanityButton = QCheckBox("Enable Vanity Search", self)
        self.enableVanityButton.setCheckable(True)
        self.enableVanityButton.setChecked(False)
        self.enableVanityButton.toggled.connect(self.update_vanity_search)
        self.prefixLineEdit.setEnabled(False)
        vanity_layout.addWidget(self.enableVanityButton)
        
        vanityGroupBox = QGroupBox(self)
        vanityGroupBox.setTitle("Vanity Searching click button to enable")
        vanityGroupBox.setStyleSheet("QGroupBox { border: 2px solid green; padding: 13px; }")
        vanityGroupBox.setLayout(vanity_layout)
        self.colourGroupBox = QGroupBox(self)
        self.colourGroupBox.setStyleSheet("QGroupBox { border: 2px solid purple; padding: 13px; }")
        self.colourWidget = QWidget()
        self.colourLayout = QHBoxLayout(self.colourWidget)
        self.colorlable = QLabel(
            '<html><b><font color="purple" size="2">Pick Console Colour</font></b></html>', self
        )
        self.colorlable.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.colorComboBox = QComboBox(self)
        self.colorComboBox.addItem("Default Colour")
        self.colorComboBox.addItem("Option 1: White Background, Purple Box")
        self.colorComboBox.addItem("Option 2: Black Background, Green Box")
        self.colorComboBox.addItem("Option 3: White Background, Blue Box")
        self.colorComboBox.addItem("Option 4: Yellow Background, Blue Box")
        self.colorComboBox.addItem("Option 5: Red Background, Black Box")
        self.colorComboBox.addItem("Option 6: Black Background, Yellow Box")
        self.colorComboBox.currentIndexChanged.connect(self.update_console_style)
        self.colourLayout.addWidget(self.colorlable)
        self.colourLayout.addWidget(self.colorComboBox)
        self.colourGroupBox.setLayout(self.colourLayout)
        self.matrixCheckBox = QCheckBox("Matrix screen, feel like a h4x0r, but performance will drop", self)
        self.colourLayout.addWidget(self.matrixCheckBox)
        self.quietCheckBox = QCheckBox("Quiet the thread output", self)
        self.colourLayout.addWidget(self.quietCheckBox)

        self.consoleWindow = ConsoleWindow(self)
        self.customLayout = QHBoxLayout()
        self.customLabel = QLabel("Custom CMD here :", self)
        self.customLayout.addWidget(self.customLabel)
        self.inputcustomEdit = QLineEdit(self)
        self.inputcustomEdit.setPlaceholderText('keyhunt -m address -f btc.txt -r 1:FFFFFFFF')
        self.inputcustomEdit.returnPressed.connect(self.custom_start)
        self.customLayout.addWidget(self.inputcustomEdit)
        
        self.customButton = QPushButton("Custom CMD Input", self)
        self.customButton.setStyleSheet("color: green;")
        self.customButton.clicked.connect(self.custom_start)
        self.customLayout.addWidget(self.customButton)

        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setStyleSheet("color: red;")
        self.stopButton.clicked.connect(self.stop_keyhunt)
        self.customLayout.addWidget(self.stopButton)
        
        self.knightRiderWidget = KnightRiderWidget(self)
        self.knightRiderWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.knightRiderWidget.setMinimumHeight(20)
        
        self.knightRiderLayout = QHBoxLayout()
        self.knightRiderLayout.setContentsMargins(0, 15, 0, 0)
        self.knightRiderLayout.addWidget(self.knightRiderWidget)

        self.knightRiderGroupBox = QGroupBox(self)
        self.knightRiderGroupBox.setTitle("Running Process ")
        self.knightRiderGroupBox.setStyleSheet("QGroupBox { border: 2px solid red; padding: 2px; }")
        self.knightRiderGroupBox.setLayout(self.knightRiderLayout)
        mizogg_label = QLabel(mizogg, self)
        mizogg_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        mizogg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.leftLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.leftLayout, stretch=2)
        self.rightLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.rightLayout, stretch=4)
        self.customGroupBox = QGroupBox(self)
        self.customGroupBox.setLayout(self.customLayout)
        self.leftLayout.addWidget(welcome_label)
        self.leftLayout.addWidget(line1_label)
        self.leftLayout.addWidget(line2_label)
        self.leftLayout.addWidget(self.threadGroupBox)
        self.leftLayout.addWidget(self.optionsGroupBox)
        self.leftLayout.addWidget(self.optionsGroupBox1)
        self.leftLayout.addWidget(self.outputFileGroupBox)
        self.leftLayout.addWidget(self.optionsGroupBox3)
        self.leftLayout.addWidget(vanityGroupBox)
        self.leftLayout.addWidget(self.colourGroupBox)

        self.leftLayout.addWidget(self.customGroupBox)

        self.leftLayout.addWidget(self.knightRiderGroupBox)
        self.leftLayout.addWidget(mizogg_label)

        self.rightLayout.addWidget(self.consoleWindow)
        self.mainLayout.setStretchFactor(self.leftLayout, 2)
        self.mainLayout.setStretchFactor(self.rightLayout, 4)
    
    def update_keyspace_range(self, value):
        start_range = hex(2**(value - 1))[2:]
        end_range = hex(2**value - 1)[2:]
        self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
        self.bitsLineEdit.setText(str(value))
        
    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)
            self.prefixLineEdit.clear()

    def run_keyhunt(self):
        command = self.construct_command()
        self.execute_command(command)

    def stop_keyhunt(self):
        if self.commandThread and self.commandThread.isRunning():
            if platform.system() == "Windows":
                subprocess.Popen(["taskkill", "/F", "/T", "/PID", str(self.commandThread.process.pid)])
            else:
                os.killpg(os.getpgid(self.commandThread.process.pid), signal.SIGTERM)
            
            self.timer.stop()
            self.scanning = False
            self.knightRiderWidget.stopAnimation()
            returncode = 'Closed'
            self.command_finished(returncode)

    @pyqtSlot(bool)
    def update_vanity_search(self, enabled):
        self.Vanity_Label.setEnabled(enabled)
        self.prefixLineEdit.setEnabled(enabled)
        
    @pyqtSlot(bool)
    def update_alphabet_search(self, enabled):
        self.alphabetLabel.setEnabled(enabled)
        self.alphabetLineEdit.setEnabled(enabled)
        
    @pyqtSlot(bool)
    def update_mini_search(self, enabled):
        self.minikeyBaseLabel.setEnabled(enabled)
        self.minikeyBaseEdit.setEnabled(enabled)

    def construct_command(self):
        mode = self.modeComboBox.currentText().strip()
        thread_count = int(self.threadComboBox.currentText())
        self.thread_count = thread_count
        command = f"keyhunt -m {mode} -t {self.thread_count}"
        
        file = self.inputFileLineEdit.text().strip()
        if file:
            command += f" -f {file}"

        move_mode = self.move_modeEdit.currentText().strip()
        if move_mode == 'random':
            if mode == 'bsgs':
                command += f" -B {move_mode}"
            else:
                command += f" -R"
        elif move_mode == 'sequential':
            if mode == 'bsgs':
                command += f" -B {move_mode}"
            else:
                command += f" -S"
        elif move_mode == 'backward' and mode == 'bsgs':
            command += f" -B {move_mode}"
        elif move_mode == 'dance' and mode == 'bsgs':
            command += f" -B {move_mode}"
        elif move_mode == 'both' and mode == 'bsgs':
            command += f" -B {move_mode}"
        
        crypto = self.cryptoComboBox.currentText().strip()
        if crypto == "eth":
                command += f" -c {crypto}"
        
        if self.minikeyBasebutton.isChecked() and mode == "address":
            minikey_base = self.minikeyBaseEdit.text().strip()
            command += f" -C {minikey_base}"
            
        if self.enablealphabetButton.isChecked() and mode == "address":
            alphabet = self.alphabetLineEdit.text().strip()
            command += f" -8 {alphabet}"
        
        keyspace = self.keyspaceLineEdit.text().strip()
        if keyspace:
            if mode == 'bsgs':
                pass
            else:
                command += f" -r {keyspace}"
                
        bits = self.bitsLineEdit.text().strip()
        if bits:
            command += f" -b {bits}"
        
        endomorphism = self.endomorphismCheckBox.isChecked()
        if endomorphism:
            command += " -e"

        stride = self.strideLineEdit.text().strip()
        if stride:
            command += f" -I {stride}"

        n_value = self.nValueLineEdit.text().strip()
        if n_value:
            command += f" -n {n_value}"
            
        k_value = self.kValueLineEdit.text().strip()
        if k_value:
            command += f" -k {k_value}"

        look = self.lookComboBox.currentText().strip()
        if look:
            command += f" -l {look}"

        if self.enableVanityButton.isChecked() and mode == "address" or mode == "rmd160" or mode == "xpoint":
            vanity_input = self.prefixLineEdit.text().strip()
            prefixes = [prefix.strip() for prefix in re.split(r"[,\s]+", vanity_input)]
            if prefixes:
                vanity_options = " ".join([f'-v "{prefix}"' for prefix in prefixes])
                command += f" {vanity_options}"
        
        if self.quietCheckBox.isChecked():
            command += " -q"
            
        if self.matrixCheckBox.isChecked():
            command += " -M"
        print(command)
        return command
    
    def update_movement_mode_options(self):
        mode = self.modeComboBox.currentText()
        if mode == "bsgs":
            self.move_modeEdit.clear()
            self.move_modeEdit.addItem("random")
            self.move_modeEdit.addItem("sequential")
            self.move_modeEdit.addItem("backward")
            self.move_modeEdit.addItem("both")
            self.move_modeEdit.addItem("dance")
        else:
            self.move_modeEdit.clear()
            self.move_modeEdit.addItem("random")
            self.move_modeEdit.addItem("sequential")
            
    def custom_start(self):
        command = self.inputcustomEdit.text().strip()
        self.execute_command(command)
        
    def pop_Result(self, message_error):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(message_error)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.exec_()
        
    @pyqtSlot()
    def new_window(self):
        if platform.system() == 'Windows':
            creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            creation_flags = 0

        python_cmd = f'"{sys.executable}" GUI_keyhunt.py'
        subprocess.Popen(python_cmd, creationflags=creation_flags, shell=True)

    @pyqtSlot()
    def execute_command(self, command):
        if self.scanning:
            return

        self.scanning = True
        self.knightRiderWidget.startAnimation()

        if self.commandThread and self.commandThread.isRunning():
            self.commandThread.terminate()

        self.commandThread = CommandThread(command)
        self.commandThread.commandOutput.connect(self.consoleWindow.append_output)
        self.commandThread.commandFinished.connect(self.command_finished)
        self.commandThread.start()

        self.timer.start(100)
    
    @pyqtSlot(int)
    def command_finished(self, returncode):
        self.timer.stop()
        self.scanning = False
        self.knightRiderWidget.stopAnimation()

        if returncode == 0:
            finish_scan = f"\n[+] Command execution finished successfully {returncode}"
            self.consoleWindow.append_output(finish_scan)
        elif returncode == 'Closed':
            finish_scan = f"\n[+] Process has been stopped by the user {returncode}"
            self.consoleWindow.append_output(finish_scan)
        else:
            error_scan = f"\n[+] Command execution failed {returncode}"
            self.consoleWindow.append_output(error_scan)

    @pyqtSlot()
    def update_gui(self):
        if self.commandThread and not self.commandThread.isRunning():
            self.command_finished(self.commandThread.process.returncode)

    @pyqtSlot(int)
    def update_console_style(self, index):
        self.consoleWindow.update_console_style(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
