import cv2
import threading
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(853, 734)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.radioButtonCam = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonCam.setGeometry(QtCore.QRect(140, 540, 121, 31))
        self.radioButtonCam.setObjectName("radioButtonCam")
        self.radioButtonFile = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonFile.setGeometry(QtCore.QRect(140, 580, 121, 31))
        self.radioButtonFile.setObjectName("radioButtonFile")
        self.Open = QtWidgets.QPushButton(self.centralwidget)
        self.Open.setGeometry(QtCore.QRect(350, 560, 121, 41))
        self.Open.setObjectName("Open")
        self.Close = QtWidgets.QPushButton(self.centralwidget)
        self.Close.setGeometry(QtCore.QRect(550, 560, 111, 41))
        self.Close.setObjectName("Close")
        self.DispalyLabel = QtWidgets.QLabel(self.centralwidget)
        self.DispalyLabel.setGeometry(QtCore.QRect(71, 44, 711, 411))
        self.DispalyLabel.setMouseTracking(False)
        self.DispalyLabel.setText("")
        self.DispalyLabel.setObjectName("DispalyLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 853, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.radioButtonCam.setText(_translate("MainWindow", "camera"))
        self.radioButtonFile.setText(_translate("MainWindow", "local file"))
        self.Open.setText(_translate("MainWindow", "Open"))
        self.Close.setText(_translate("MainWindow", "Close"))


class Display:
    def __init__(self, ui, mainWnd):
        self.ui = ui
        self.mainWnd = mainWnd

        # ????????????????????????
        self.ui.radioButtonCam.setChecked(True)
        self.isCamera = True

        # ???????????????
        ui.Open.clicked.connect(self.Open)
        ui.Close.clicked.connect(self.Close)
        ui.radioButtonCam.clicked.connect(self.radioButtonCam)
        ui.radioButtonFile.clicked.connect(self.radioButtonFile)

        # ??????????????????????????????????????????
        self.stopEvent = threading.Event()
        self.stopEvent.clear()

    def radioButtonCam(self):
        self.isCamera = True

    def radioButtonFile(self):
        self.isCamera = False

    def Open(self):
        if not self.isCamera:
            self.fileName, self.fileType = QFileDialog.getOpenFileName(self.mainWnd, 'Choose file', '', '*.mp4')
            self.cap = cv2.VideoCapture(self.fileName)
            self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
        else:
            # ????????????rtsp?????????????????????
            # cap = cv2.VideoCapture("rtsp://admin:Supcon1304@172.20.1.126/main/Channels/1")
            self.cap = cv2.VideoCapture("rtsp://admin:Supcon1304@172.20.1.126:554/h264/ch1/main/av_stream")

        # ????????????????????????
        th = threading.Thread(target=self.Display)
        th.start()

    def Close(self):
        # ?????????????????????????????????????????????
        self.stopEvent.set()

    def Display(self):
        self.ui.Open.setEnabled(False)
        self.ui.Close.setEnabled(True)

        while self.cap.isOpened():
            success, frame = self.cap.read()
            # RGB???BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.ui.DispalyLabel.setPixmap(QPixmap.fromImage(img))

            if self.isCamera:
                cv2.waitKey(1)
            else:
                cv2.waitKey(int(1000 / self.frameRate))

            # ?????????????????????????????????
            if True == self.stopEvent.is_set():
                # ??????????????????????????????????????????label
                self.stopEvent.clear()
                self.ui.DispalyLabel.clear()
                self.ui.Close.setEnabled(False)
                self.ui.Open.setEnabled(True)
                self.cap.release()
                break
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWnd = QMainWindow()
    ui = Ui_MainWindow()

    # ??????????????????????????? ui ?????????????????? mainWnd ???
    ui.setupUi(mainWnd)

    display = Display(ui, mainWnd)

    mainWnd.show()

    sys.exit(app.exec_())