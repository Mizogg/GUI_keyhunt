"""
@author: Team Mizogg
"""
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSlot

class ConsoleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.consoleOutput = QPlainTextEdit(self)
        self.consoleOutput.setReadOnly(True)
        self.layout.addWidget(self.consoleOutput)

        button_widget = QWidget(self)
        button_layout = QHBoxLayout(button_widget)

        self.clearButton = QPushButton("Clear", self)
        self.clearButton.setStyleSheet(
                "QPushButton { font-size: 12pt; }"
                "QPushButton:hover { font-size: 12pt; }"
            )
        button_layout.addWidget(self.clearButton)

        self.selectAllButton = QPushButton("Select All", self)
        self.selectAllButton.setStyleSheet(
                "QPushButton { font-size: 12pt; }"
                "QPushButton:hover { font-size: 12pt; }"
            )
        button_layout.addWidget(self.selectAllButton)

        self.copyButton = QPushButton("Copy", self)
        self.copyButton.setStyleSheet(
                "QPushButton { font-size: 12pt; }"
                "QPushButton:hover { font-size: 12pt; }"
            )
        button_layout.addWidget(self.copyButton)

        self.thresholdLabel = QLabel("Console Threshold:", self)
        self.thresholdDropdown = QComboBox(self)
        self.thresholdDropdown.addItems(["50", "100", "500", "1000"])
        self.thresholdDropdown.setCurrentIndex(2)
        button_layout.addWidget(self.thresholdLabel)
        button_layout.addWidget(self.thresholdDropdown)
        self.layout.addWidget(button_widget)

        self.clearButton.clicked.connect(self.clear_console)
        self.selectAllButton.clicked.connect(self.select_all)
        self.copyButton.clicked.connect(self.copy_text)
        self.thresholdDropdown.currentIndexChanged.connect(self.update_threshold)
        
        self.threshold = int(self.thresholdDropdown.currentText())

    def set_output(self, output):
        self.consoleOutput.setPlainText(output)

    def append_output(self, output):
        QMetaObject.invokeMethod(self.consoleOutput, "appendPlainText", Qt.ConnectionType.QueuedConnection, Q_ARG(str, output))
        line_count = self.consoleOutput.document().blockCount()
        if line_count > self.threshold:
            QMetaObject.invokeMethod(self.consoleOutput, "clear", Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def clear_console(self):
        self.consoleOutput.clear()

    @pyqtSlot()
    def select_all(self):
        self.consoleOutput.selectAll()

    @pyqtSlot()
    def copy_text(self):
        cursor = self.consoleOutput.textCursor()
        selected_text = cursor.selectedText()
        clipboard = QApplication.clipboard()
        clipboard.setText(selected_text)

    @pyqtSlot()
    def update_threshold(self):
        self.threshold = int(self.thresholdDropdown.currentText())
