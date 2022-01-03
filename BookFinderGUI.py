# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, pyqtSlot, QRunnable, QObject
from PyQt5 import QtWidgets,QtGui
import sys

class Signals(QObject):
    returnSingal = pyqtSignal(str)

class Thread(QRunnable):
    signal = pyqtSignal(str)
    def __init__(self, URL, price):
        super(Thread, self).__init__()
        self.signal = Signals()

        self.URL = URL
        self.minPrice = float(price)

    @pyqtSlot()
    def run(self):
        import bookfinder
        bookfinder.searchProduct(self.URL, self.minPrice)
        result = ""
        self.signal.returnSingal.emit(result)

class mainWindow(QtWidgets.QWidget):
    def __init__(self,):
        super(mainWindow,self).__init__()
        self.threadpool = QThreadPool()
        self.setStyleSheet("background-color:lemonchiffon")
        self.setWindowTitle("******* LLC")
        self.setGeometry(700, 300, 400, 300)
        self.UserInterface()

    def UserInterface(self):
        self.labelUrl = QtWidgets.QLabel("URL:")
        self.labelUrl.setFont(QtGui.QFont("Arial", 14))
        self.labelUrl.setStyleSheet('color:red')

        self.textUrl = QtWidgets.QLineEdit()
        self.textUrl.setStyleSheet("color:black;background-color:white")

        self.labelMp = QtWidgets.QLabel("Min Profit:")
        self.labelMp.setFont(QtGui.QFont("Arial", 14))
        self.labelMp.setStyleSheet('color:red')

        self.textMp = QtWidgets.QLineEdit()
        self.textMp.setStyleSheet("color:black;background-color:white")

        self.searchButton = QtWidgets.QPushButton("RESEARCH")
        self.searchButton.setStyleSheet("color:black;background-color:orange")
        self.searchButton.setFont(QtGui.QFont("Arial", 14))

        self.horizontalBox = QtWidgets.QHBoxLayout()
        self.horizontalBox2 = QtWidgets.QHBoxLayout()
        self.verticalBox = QtWidgets.QVBoxLayout()

        self.horizontalBox.addWidget(self.labelUrl)
        self.horizontalBox.addWidget(self.textUrl)

        self.messagebox = QtWidgets.QMessageBox()
        self.messagebox.setWindowTitle("Bookfinder")
        self.messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.horizontalBox2.addWidget(self.labelMp)
        self.horizontalBox2.addWidget(self.textMp)
        self.horizontalBox2.addWidget(self.searchButton)
        self.verticalBox.addLayout(self.horizontalBox)
        self.verticalBox.addLayout(self.horizontalBox2)
        self.setLayout(self.verticalBox)
        self.show()
        self.searchButton.clicked.connect(self.runSearchProduct)

    def runSearchProduct(self):
        try:
            self.messagebox.setIcon(QtWidgets.QMessageBox.Information)
            self.messagebox.setText("Application started, do not close the window!")
            self.URL = self.textUrl.text()
            self.price = self.textMp.text()
            thread = Thread(self.URL,self.price)
            thread.signal.returnSingal.connect(self.threadFunction)
            self.threadpool.start(thread)
            self.messagebox.exec()
        except:
            self.messagebox.setIcon(QtWidgets.QMessageBox.Warning)
            self.messagebox.setText("Missing URL or price information")
            self.messagebox.exec()

    def threadFunction(self, signal):
        print(signal)

###############################################################

app = QtWidgets.QApplication(sys.argv)
appWidget = mainWindow()
sys.exit(app.exec_())



