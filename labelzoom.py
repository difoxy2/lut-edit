from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
import sys


class LabelZoom(QtWidgets.QDialog):
    def __init__(self, pimg=None):
        super().__init__()
        uic.loadUi("labelzoom.ui", self)
        self.setWindowTitle('Label Zoom')
        self.scale = 1
        self.pimg = pimg

        self.label = self.findChild(QtWidgets.QLabel,'label')
        self.pixmap = QtGui.QPixmap(self.pimg)
        self.label.resize(self.pixmap.width(), self.pixmap.height())
        #self.label.width =self.pixmap.width()
        #self.label.height = self.pixmap.height()
        self.pixmap2 = self.pixmap.scaled(self.pixmap.width(),self.pixmap.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(self.pixmap2)


        self.btnp = self.findChild(QtWidgets.QPushButton,'pushButton')
        self.btnm = self.findChild(QtWidgets.QPushButton,'pushButton_2')
        self.btnp.clicked.connect(self.zoomin)
        self.btnm.clicked.connect(self.zoomout)

    def zoomin(self):
        self.scale *= 1.2
        self.pixmap2 = self.pixmap.scaled(int(self.pixmap.width() * self.scale),int(self.pixmap.height() * self.scale), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(self.pixmap2)
    def zoomout(self):
        self.scale /= 1.2
        self.pixmap2 = self.pixmap.scaled(int(self.pixmap.width() * self.scale),int(self.pixmap.height() * self.scale), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(self.pixmap2)

# # Initialize the app
# app = QtWidgets.QApplication(sys.argv)
# window = LabelZoom()
# window.show()
# app.exec()