# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, pyqtSlot, QRunnable, QObject
from PyQt5 import QtWidgets,QtGui
import sys

class Signals(QObject):
    return_signal = pyqtSignal(str)

class Thread(QRunnable):
    signal = pyqtSignal(str)
    def __init__(self,URL,Fiyat):
        super(Thread, self).__init__()
        self.signal = Signals()

        self.URL=URL
        self.min_price=float(Fiyat)

    @pyqtSlot()
    def run(self):
        import bookfinder
        bookfinder.urun_ara(self.URL,self.min_price)
        result=""
        self.signal.return_signal.emit(result)


class main_window(QtWidgets.QWidget):
    def __init__(self,):
        super(main_window,self).__init__()
        self.threadpool = QThreadPool()
        self.setStyleSheet("background-color:lemonchiffon")
        self.setWindowTitle("******* LLC")
        self.setGeometry(700,300,400,300)
        self.UserIn()

    def UserIn(self):
        self.label_url=QtWidgets.QLabel("URL:")
        self.label_url.setFont(QtGui.QFont("Arial",14))
        self.label_url.setStyleSheet('color:red')

        self.text_url=QtWidgets.QLineEdit()
        self.text_url.setStyleSheet("color:black;background-color:white")

        self.label_mp=QtWidgets.QLabel("Min Profit:")
        self.label_mp.setFont(QtGui.QFont("Arial",14))
        self.label_mp.setStyleSheet('color:red')

        self.text_mp=QtWidgets.QLineEdit()
        self.text_mp.setStyleSheet("color:black;background-color:white")

        self.button_arastır=QtWidgets.QPushButton("RESEARCH")
        self.button_arastır.setStyleSheet("color:black;background-color:orange")
        self.button_arastır.setFont(QtGui.QFont("Arial",14))

        self.h_box=QtWidgets.QHBoxLayout()
        self.h_box2=QtWidgets.QHBoxLayout()
        self.v_box=QtWidgets.QVBoxLayout()

        self.h_box.addWidget(self.label_url)
        self.h_box.addWidget(self.text_url)

        self.messagebox=QtWidgets.QMessageBox()
        self.messagebox.setWindowTitle("Bookfinder")
        self.messagebox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.h_box2.addWidget(self.label_mp)
        self.h_box2.addWidget(self.text_mp)
        self.h_box2.addWidget(self.button_arastır)
        self.v_box.addLayout(self.h_box)
        self.v_box.addLayout(self.h_box2)
        self.setLayout(self.v_box)
        self.show()
        self.button_arastır.clicked.connect(self.urunu_ara)

    def urunu_ara(self):
        try:
            self.messagebox.setIcon(QtWidgets.QMessageBox.Information)
            self.messagebox.setText("Uygulama başladı. Açılan sekmeleri kapatmayın !")
            self.URL=self.text_url.text()
            self.fiyat=self.text_mp.text()
            thread = Thread(self.URL,self.fiyat)
            thread.signal.return_signal.connect(self.function_thread)
            self.threadpool.start(thread)
            self.messagebox.exec()
        except:
            self.messagebox.setIcon(QtWidgets.QMessageBox.Warning)
            self.messagebox.setText("URL veya Fiyat bilgisi girmediniz !")
            self.messagebox.exec()

    def function_thread(self, signal):
        print(signal)

###############################################################

app=QtWidgets.QApplication(sys.argv)
uyg=main_window()
sys.exit(app.exec_())



