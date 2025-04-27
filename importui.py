from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

class ImportUI(QtWidgets.QDialog):
    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("importui.ui", self)
        self.setWindowTitle('Import Images')

        # ----------- self.variables ----------- #
        self.mainwindow = mainwindow
        self.filepaths_refs = []
        self.filepaths_scans = []
        self.list_last_clicked = QtWidgets.QListWidget()

        # ----------- Define Widgets ----------- #   
        self.btn_cancel = self.findChild(QtWidgets.QPushButton,'btn_cancel')
        self.btn_cancel.clicked.connect(self.func_btn_cancel)
        self.btn_ok = self.findChild(QtWidgets.QPushButton,'btn_ok')
        self.btn_ok.clicked.connect(self.func_btn_ok)
        self.btn_up = self.findChild(QtWidgets.QPushButton,'btn_up')
        self.btn_up.clicked.connect(self.func_btn_up)
        self.btn_down = self.findChild(QtWidgets.QPushButton,'btn_down')
        self.btn_down.clicked.connect(self.func_btn_down)
        self.btn_open_refs = self.findChild(QtWidgets.QPushButton,'btn_open_refs')
        self.btn_open_refs.clicked.connect(self.func_btn_open_refs)
        self.btn_open_scans = self.findChild(QtWidgets.QPushButton,'btn_open_scans')
        self.btn_open_scans.clicked.connect(self.func_btn_open_scans)
        self.label = self.findChild(QtWidgets.QLabel,'label')
        self.list_refs = self.findChild(QtWidgets.QListWidget,'list_refs')
        self.list_refs.itemClicked.connect(self.update_list_last_clicked)
        self.list_scans = self.findChild(QtWidgets.QListWidget,'list_scans')
        self.list_scans.itemClicked.connect(self.update_list_last_clicked)

    def func_btn_open_refs(self):
        self.filepaths_refs = QtWidgets.QFileDialog.getOpenFileNames(self,'Open Ref Images','C:\\Users\\ASUS\\Desktop\\ScanSnap', 'Images (*.jpg *jpeg *.png)')
        self.list_refs.clear()
        self.list_refs.addItems(self.filepaths_refs[0])

    def func_btn_open_scans(self):
        self.filepaths_scans = QtWidgets.QFileDialog.getOpenFileNames(self,'Open Scan Images','C:\\Users\\ASUS\\Desktop\\ScanSnap', 'Images (*.jpg *jpeg *.png)')
        self.list_scans.clear()
        self.list_scans.addItems(self.filepaths_scans[0])

    def func_btn_cancel(self):
        self.close()

    def func_btn_ok(self):
        self.mainwindow.imgpaths_refs = [self.list_refs.item(x).text() for x in range(self.list_refs.count())]
        self.mainwindow.imgpaths_scans = [self.list_scans.item(x).text() for x in range(self.list_scans.count())]
        self.close()

    def func_btn_up(self):
        index = self.list_last_clicked.currentRow()
        if index >= 1:
            item = self.list_last_clicked.takeItem(index)
            self.list_last_clicked.insertItem(index-1,item)
            self.list_last_clicked.setCurrentItem(item)

    def func_btn_down(self):
        index = self.list_last_clicked.currentRow()
        if index < self.list_last_clicked.count()-1:
            item = self.list_last_clicked.takeItem(index)
            self.list_last_clicked.insertItem(index+1,item)
            self.list_last_clicked.setCurrentItem(item)

    def update_list_last_clicked(self):
        self.list_last_clicked = self.sender()
        pixmap = QtGui.QPixmap(self.list_last_clicked.currentItem().text())
        pixmap = pixmap.scaled(self.label.width(), self.label.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(pixmap)