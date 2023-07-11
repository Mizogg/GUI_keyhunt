import sys
import os
import signal
import platform
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QCheckBox, QTextEdit, QFileDialog
from PyQt5.QtGui import QColor, QFont, QPixmap
import multiprocessing
import subprocess

mizogg = f'''

 Made by Mizogg Version 1.0  © mizogg.co.uk 2018 - 2023      {f"[>] Running with Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"}

'''

class CommandThread(QThread):
    commandOutput = pyqtSignal(str)
    commandFinished = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        self.process = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True
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
        self.consoleOutput = QTextEdit(self)
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setFixedHeight(350)
        self.layout.addWidget(self.consoleOutput)

        self.matrixCheckBox = parent.matrixCheckBox
        self.matrixCheckBox.stateChanged.connect(self.update_console_style)

        self.update_console_style(self.matrixCheckBox.checkState())

    @pyqtSlot(int)
    def update_console_style(self, state):
        if state == Qt.Checked:
            self.consoleOutput.setStyleSheet("background-color: black; color: green; font-size: 14px;")
        else:
            self.consoleOutput.setStyleSheet("background-color: white; color: purple; font-size: 14px;")

    @pyqtSlot(str)
    def append_output(self, output):
        self.consoleOutput.append(output)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        cpu_count = multiprocessing.cpu_count()
        self.setWindowTitle("Keyhunt GUI @ github.com/Mizogg")

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
        welcome_label = QLabel("<html><b><center><font color='purple' size='10'>Welcome  Alberto's KeyHunt GUI made by Mizogg</font></center></b></html>")
        main_layout.addWidget(welcome_label)
        line1_label = QLabel('<html><b><center><font color="red" size="5"> Tool for hunt privatekeys for crypto currencies that use secp256k1 elliptic curve </font></center></b></html>')
        main_layout.addWidget(line1_label)
        line2_label = QLabel('<html><b><center><font color="blue" size="3"> Address hunting MENU RMD160 MENU. XPoint Menu </font></center></b></html>')
        main_layout.addWidget(line2_label)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)
        self.threadLayout = QHBoxLayout()
        self.GPU_layout = QHBoxLayout()
        self.layout.addLayout(main_layout)
        self.layout.addLayout(self.threadLayout)
        self.layout.addLayout(self.GPU_layout)
        self.threadLabel = QLabel(
            '<html><b><left><font color="blue" size="2">Number of CPUS : </font></left></b></html>', self
        )
        self.threadLayout.addWidget(self.threadLabel)
        self.threadComboBox = QComboBox()
        for i in range(1, cpu_count + 1):
            self.threadComboBox.addItem(str(i))
        self.threadComboBox.setCurrentIndex(2)
        self.threadLayout.addWidget(self.threadComboBox)
        self.startButton = QPushButton("Start scanning", self)
        self.startButton.clicked.connect(self.run_keyhunt)
        self.threadLayout.addWidget(self.startButton)

        self.stopButton = QPushButton("Stop scanning", self)
        self.stopButton.clicked.connect(self.stop_keyhunt)
        self.threadLayout.addWidget(self.stopButton)

        self.NEWButton = QPushButton("New window", self)
        self.NEWButton.clicked.connect(self.new_window)
        self.threadLayout.addWidget(self.NEWButton)

        options_layout = QHBoxLayout()
        
        self.modeLabel = QLabel("Mode:", self)
        options_layout.addWidget(self.modeLabel)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("address")
        self.modeComboBox.addItem("xpoint")
        self.modeComboBox.addItem("rmd160")
        self.modeComboBox.addItem("bsgs")
        self.modeComboBox.addItem("vanity")
        options_layout.addWidget(self.modeComboBox)
        self.lookLabel = QLabel("Look:", self)
        options_layout.addWidget(self.lookLabel)
        self.lookComboBox = QComboBox()
        self.lookComboBox.addItem("compress")
        self.lookComboBox.addItem("uncompress")
        self.lookComboBox.addItem("both")
        options_layout.addWidget(self.lookComboBox)
        self.move_modeLabel = QLabel("Move Mode:", self)
        options_layout.addWidget(self.move_modeLabel)
        self.move_modeEdit = QComboBox(self)
        self.move_modeEdit.addItem("sequential")
        self.move_modeEdit.addItem("backward")
        self.move_modeEdit.addItem("both")
        self.move_modeEdit.addItem("random")
        self.move_modeEdit.addItem("dance")
        options_layout.addWidget(self.move_modeEdit)

        self.strideLabel = QLabel("Stride:", self)
        options_layout.addWidget(self.strideLabel)
        self.strideLineEdit = QLineEdit(self)
        options_layout.addWidget(self.strideLineEdit)

        self.kValueLabel = QLabel("K Value:", self)
        options_layout.addWidget(self.kValueLabel)
        self.kValueLineEdit = QLineEdit(self)
        options_layout.addWidget(self.kValueLineEdit)
        self.layout.addLayout(options_layout)

        self.inputFileLabel = QLabel("Specify file name with addresses or xpoints or uncompressed public keys:", self)
        self.layout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit('1to32.txt', self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your File')
        self.layout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.clicked.connect(self.browse_input_file)
        self.layout.addWidget(self.inputFileButton)
        
        options_layout2 = QHBoxLayout()
        self.keyspaceLabel = QLabel("Key Space:", self)
        options_layout2.addWidget(self.keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("20000000000000000:3ffffffffffffffff", self)
        self.keyspaceLineEdit.setPlaceholderText('Example range for 66 = 20000000000000000:3ffffffffffffffff')
        options_layout2.addWidget(self.keyspaceLineEdit)

        self.bitsLabel = QLabel("Bits:", self)
        options_layout2.addWidget(self.bitsLabel)
        self.bitsLineEdit = QLineEdit(self)
        options_layout2.addWidget(self.bitsLineEdit)
        self.layout.addLayout(options_layout2)

        options_layout3 = QHBoxLayout()
        self.cryptoLabel = QLabel("Crypto:", self)
        options_layout3.addWidget(self.cryptoLabel)
        self.cryptoComboBox = QComboBox()
        self.cryptoComboBox.addItem("btc")
        self.cryptoComboBox.addItem("eth")
        options_layout3.addWidget(self.cryptoComboBox)

        self.minikeyBaseLabel = QLabel("Minikey Base:", self)
        options_layout3.addWidget(self.minikeyBaseLabel)
        self.minikeyBaseComboBox = QComboBox()
        self.minikeyBaseComboBox.addItem("default")
        self.minikeyBaseComboBox.addItem("SRPqx8QiwnW4WNWnTVa2W5")
        options_layout3.addWidget(self.minikeyBaseComboBox)

        self.alphabetLabel = QLabel("Alphabet:", self)
        options_layout3.addWidget(self.alphabetLabel)
        self.alphabetLineEdit = QLineEdit(self)
        options_layout3.addWidget(self.alphabetLineEdit)

        self.endomorphismCheckBox = QCheckBox("Enable Endomorphism Search (Only for address, rmd160 and vanity) ", self)
        options_layout3.addWidget(self.endomorphismCheckBox)

        self.layout.addLayout(options_layout3)

        vanity_layout = QHBoxLayout()

        self.Vanity_Label = QLabel("Vanity Address to search:", self)
        vanity_layout.addWidget(self.Vanity_Label)
        self.prefixLineEdit = QLineEdit("13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so", self)
        vanity_layout.addWidget(self.prefixLineEdit)

        self.enableVanityButton = QPushButton("Enable Vanity Search", self)
        self.enableVanityButton.setCheckable(True)
        self.enableVanityButton.setChecked(False)
        self.enableVanityButton.toggled.connect(self.update_vanity_search)
        vanity_layout.addWidget(self.enableVanityButton)

        self.layout.addLayout(vanity_layout)
        
        self.matrixCheckBox = QCheckBox("Matrix screen, feel like a h4x0r, but performance will drop", self)
        self.layout.addWidget(self.matrixCheckBox)
        
        self.consoleWindow = ConsoleWindow(self)
        self.layout.addWidget(self.consoleWindow)

        self.process = None
        self.commandThread = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.scanning = False
        
        mizogg_label = QLabel(mizogg, self)
        mizogg_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(mizogg_label)

    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec_():
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
            returncode = 'Closed'
            self.command_finished(returncode)


    @pyqtSlot(bool)
    def update_vanity_search(self, enabled):
        self.Vanity_Label.setEnabled(enabled)
        self.prefixLineEdit.setEnabled(enabled)

    def construct_command(self):
        mode = self.modeComboBox.currentText().strip()
        thread_count = int(self.threadComboBox.currentText())
        self.thread_count = thread_count
        command = f"keyhunt -m {mode} -t {self.thread_count}"

        keyspace = self.keyspaceLineEdit.text().strip()
        if keyspace:
            command += f" -r {keyspace}"

        move_mode = self.move_modeEdit.currentText().strip()
        if move_mode:
            command += f" -B {move_mode}"

        if mode == "eth":
            crypto = self.cryptoComboBox.currentText().strip()
            if crypto:
                command += f" -c {crypto}"
        
        #minikey_base = self.minikeyBaseComboBox.currentText().strip()
        #if minikey_base:
        #    command += f" -C {minikey_base}"
        #
        #alphabet = self.alphabetLineEdit.text().strip()
        #if alphabet:
        #    command += f" -8 {alphabet}"
        #
        #bits = self.bitsLineEdit.text().strip()
        #if bits:
        #    command += f" -b {bits}"
        #
        #endomorphism = self.endomorphismCheckBox.isChecked()
        #if endomorphism:
        #    command += " -e"

        file = self.inputFileLineEdit.text().strip()
        if file:
            command += f" -f {file}"

        stride = self.strideLineEdit.text().strip()
        if stride:
            command += f" -I {stride}"

        k_value = self.kValueLineEdit.text().strip()
        if k_value:
            command += f" -k {k_value}"

        look = self.lookComboBox.currentText().strip()
        if look:
            command += f" -l {look}"

        if self.enableVanityButton.isChecked() and mode == "address":

            vanity = self.prefixLineEdit.text().strip()
            command += f' -v "{vanity}"'
        
        if self.matrixCheckBox.isChecked():
            command += " -M"
               
        return command

    @pyqtSlot()
    def new_window(self):
        python_cmd = f'start cmd /c "{sys.executable}" GUI_keyhunt.py'
        subprocess.Popen(python_cmd, shell=True)

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

    @pyqtSlot(int)
    def command_finished(self, returncode):
        self.timer.stop()
        self.scanning = False

        if returncode == 0:
            finish_scan = "Command execution finished successfully"
            self.consoleWindow.append_output(finish_scan)
        if returncode == 'Closed':
            finish_scan = "Process has been stopped by the user"
            self.consoleWindow.append_output(finish_scan)
        else:
            error_scan = "Command execution failed"
            self.consoleWindow.append_output(error_scan)

    def update_gui(self):
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
