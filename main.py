from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys, os, subprocess, shutil, zipfile, datetime
import icons.resource_rc as resource_rc
from labelzoom import LabelZoom
from importui import ImportUI
from gma_val import return_gma_array, gammadict

class UI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("main.ui", self)
        self.setWindowTitle('LUT Editor')


        # ----------- self.variables ----------- #
        self.imgpaths_scans = []
        self.imgpaths_refs = []
        self.imgpaths_display = []
        self.imgi = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtGui.QPixmap()
        self.lut_array = return_gma_array('test',0,255)
        #self.showlut = False
        self.scale = 1
        self.scale_fit_box = 1


        # ----------- Define Widgets ----------- #
        self.btn_import_1 = self.findChild(QtWidgets.QPushButton,'import_btn_1')
        self.btn_import_1.clicked.connect(self.importfunc1)
        self.btn_import_2 = self.findChild(QtWidgets.QPushButton,'import_btn_2')
        self.btn_import_2.clicked.connect(self.importfunc2)
        self.btn_import_3 = self.findChild(QtWidgets.QPushButton,'import_btn_3')
        self.btn_import_3.clicked.connect(self.importfunc3)

        self.spinBox_in_b = self.findChild(QtWidgets.QSpinBox,'spinBox_in_b')
        self.spinBox_in_b.valueChanged.connect(self.lvValChanged)
        self.doubleSpinBox_in_g = self.findChild(QtWidgets.QDoubleSpinBox,'doubleSpinBox_in_g')
        self.doubleSpinBox_in_g.valueChanged.connect(self.lvValChanged)
        self.spinBox_in_w = self.findChild(QtWidgets.QSpinBox,'spinBox_in_w')
        self.spinBox_in_w.valueChanged.connect(self.lvValChanged)
        self.spinBox_rep_g = self.findChild(QtWidgets.QSpinBox,'spinBox_rep_g')
        self.spinBox_rep_g.valueChanged.connect(self.lvValChanged)
        self.spinBox_rep_w = self.findChild(QtWidgets.QSpinBox,'spinBox_rep_w')
        self.spinBox_rep_w.valueChanged.connect(self.lvValChanged)
        self.spinBox_out_b = self.findChild(QtWidgets.QSpinBox,'spinBox_out_b')
        self.spinBox_out_b.valueChanged.connect(self.lvValChanged)
        self.spinBox_out_w = self.findChild(QtWidgets.QSpinBox,'spinBox_out_w')
        self.spinBox_out_w.valueChanged.connect(self.lvValChanged)
        
        self.lut_checkBox = self.findChild(QtWidgets.QCheckBox,'lut_checkBox')
        self.lut_checkBox.setChecked(True)
        #self.showlut = True
        self.lut_checkBox.stateChanged.connect(self.lut_checkBox_stateChanged)

        self.lutEditorTableWidget = self.findChild(QtWidgets.QTableWidget,'lutEditorTableWidget')
        self.lutEditorTableWidget.setVerticalHeaderLabels([str(x) for x in list(range(0,256))])
        for i in range(256): 
            self.lutEditorTableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(str(''))) # if not initialize col 1, itemChanged will trigger every first mouse click
        self.lutEditorTableWidget.setItem(255,1,QtWidgets.QTableWidgetItem(str('1'))) # initialize col 1
        self.calculate_lut_array_from_table() #initialize self.lut_array
        self.update_lutEditor_column_zero(self.lut_array) # initialize col 0
        self.lutEditorTableWidget.itemChanged.connect(self.itemChanged_override)
        

        self.graphicview = self.findChild(QtWidgets.QGraphicsView,'graphicsView')
        self.graphicview.scene = QtWidgets.QGraphicsScene()

        self.graphicview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicview.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.graphicview.rubberBandChanged.connect(self.rubberBandChanged_override)
        self.graphicview.wheelEvent = self.wheelEvent_override_graphicview
        self.graphicview.keyPressEvent = self.keyPressEvent_override


        self.btn_export_1 = self.findChild(QtWidgets.QPushButton,'export_btn_1')
        self.btn_export_1.clicked.connect(self.exportfunc1)
        self.btn_export_2 = self.findChild(QtWidgets.QPushButton,'export_btn_2')
        self.btn_export_2.clicked.connect(self.exportfunc2)
        self.btn_export_3 = self.findChild(QtWidgets.QPushButton,'export_btn_3')
        self.btn_export_3.clicked.connect(self.exportfunc3)
        

    # ----------- Functions ----------- #

    # ----------- functions for Main UI class ----------- #
    def keyPressEvent_override(self, event):
        keycode = event.key()
        match keycode:
            case 16777234:
                self.imgi -=1
                if self.imgi < 0:
                    self.imgi = len(self.imgpaths_display)-1
                self.setimgPathtoScene(self.imgpaths_display[self.imgi])
            case 16777236:
                self.imgi +=1
                if self.imgi > len(self.imgpaths_display)-1:
                    self.imgi = 0
                self.setimgPathtoScene(self.imgpaths_display[self.imgi])
            case 32: #space, key h is 72
                if self.graphicview.dragMode() == QtWidgets.QGraphicsView.DragMode.ScrollHandDrag:
                    self.graphicview.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
                    self.graphicview.setCursor(QtCore.Qt.CursorShape.CrossCursor)

                else:
                    self.graphicview.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
                


        
    # ----------- functions for import button 1 ----------- #
    def importfunc1(self):
        self.newdialog = ImportUI(self)
        self.newdialog.exec()
        self.imgpaths_display = []
        local_imgpaths_scans = self.imgpaths_scans.copy()
        local_imgpaths_refs = self.imgpaths_refs.copy()
        for i in range(len(local_imgpaths_scans)):
            if len(local_imgpaths_scans) > 0 :
                self.imgpaths_display.append(local_imgpaths_scans.pop(0))
            if len(local_imgpaths_refs) > 0 :
                self.imgpaths_display.append(local_imgpaths_refs.pop(0))
        if len(self.imgpaths_display) >0:
            self.setimgPathtoScene(self.imgpaths_display[0])

    # ----------- functions for import button 2 ----------- # 
    def importfunc2(self):
        self.imgpaths_display = self.imgpaths_display
        self.setimgPathtoScene(self.imgpaths_display[0])

    # ----------- functions for import button 3 ----------- # 
    def importfunc3(self):
        print('importfunc3')

    # ----------- functions for import leveladjustment ----------- #
    def lvValChanged(self):
        # block signal before graphic view is updated
        self.spinBox_in_b.blockSignals(True)
        self.doubleSpinBox_in_g.blockSignals(True)
        self.spinBox_in_w.blockSignals(True)
        self.spinBox_rep_g.blockSignals(True)
        self.spinBox_rep_w.blockSignals(True)
        self.spinBox_out_b.blockSignals(True)
        self.spinBox_out_w.blockSignals(True)

        # fetch spin box values
        input_b = self.spinBox_in_b.value()
        input_g = self.doubleSpinBox_in_g.value()
        input_w = self.spinBox_in_w.value()
        output_b = self.spinBox_out_b.value()
        output_w = self.spinBox_out_w.value()
        rep_g = self.spinBox_rep_g.value()
        rep_w = self.spinBox_rep_w.value()
        # calculate lut array from level adjustment
        #   Photoshop’s Levels adjustment remaps image tones using this math:
        arr = []
        for value in range(256):
            if value > rep_w:
                value = int(round(max(0, min(255 * ((value/255) ** (1/rep_g)), 255))))
            else:
                #   1. Normalize: (pixel - inBlack) / (inWhite - inBlack) — stretches or compresses shadows and highlights.
                value = (value - input_b) / (input_w - input_b)
                value = max(0, min(value, 255))
                #   2. Gamma: pixel = pixel ** (1/gamma) — adjusts midtones (brightness curve).
                value = value ** (1/input_g)
                #   3. Output: pixel = pixel * (outWhite - outBlack) + outBlack — sets new black and white points.
                value = value * (output_w - output_b) + output_b
                value = max(output_b, min(value, output_w))
            arr.append(int(value))
        # update / push level adjustment lut to self.lut_array
        self.update_self_lut_array(arr)
        # display the lut-ed image in graphic view
        if(len(self.imgpaths_display)>0):
            self.setimgPathtoScene(self.imgpaths_display[self.imgi])
        # unblock signal
        self.spinBox_in_b.blockSignals(False)
        self.doubleSpinBox_in_g.blockSignals(False)
        self.spinBox_in_w.blockSignals(False)
        self.spinBox_rep_g.blockSignals(False)
        self.spinBox_rep_w.blockSignals(False)
        self.spinBox_out_b.blockSignals(False)
        self.spinBox_out_w.blockSignals(False)   



        # cwd = os.getcwd()  #
        # imgdir = os.path.dirname(imgpath) #
        # os.chdir(imgdir) # handle cv2 cannot read special character folder name
        # self.mat = cv2.imread(os.path.basename(imgpath),0)
        # os.chdir(cwd) #
        # self.mat = cv2.LUT(self.mat,np.array(self.lut_array,dtype=np.uint8))

    # ----------- functions for lut checkBox ----------- # 
    def lut_checkBox_stateChanged(self):
        #self.showlut = self.lut_checkBox.isChecked()
        if(len(self.imgpaths_display)>0):
            self.setimgPathtoScene(self.imgpaths_display[self.imgi])


    # ----------- functions for lutEditorTableWidget ----------- # 
    def itemChanged_override(self, item):
        self.lutEditorTableWidget.blockSignals(True)
        match item.column():
            case 1:
                if self.lutEditorTableWidget.item(255,1).text() == '':
                    self.lutEditorTableWidget.setItem(255,1,QtWidgets.QTableWidgetItem(str(1)))
                self.calculate_lut_array_from_table()
                self.update_lutEditor_column_zero(self.lut_array)
            case 0:
                arr_col0 = []
                for i in range(256):
                    a = self.lutEditorTableWidget.item(i,0).text()
                    if a.isdigit() and int(a)>=0 and int(a)<=255:
                        arr_col0.append(self.lutEditorTableWidget.item(i,0).text())
                    else:
                        self.lutEditorTableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(self.lut_array[i])))
                self.update_self_lut_array(arr_col0)
        if(len(self.imgpaths_display)>0):
            self.setimgPathtoScene(self.imgpaths_display[self.imgi])
        self.lutEditorTableWidget.blockSignals(False)

    def update_lutEditor_column_zero(self,arr_256):
        if len(arr_256) != 256:
            print('LUT table column need update with array of length 256')
            return
        for i in range(256):
            self.lutEditorTableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(arr_256[i])))
    
    def update_self_lut_array(self,arr_256):
        if len(arr_256) != 256:
            print('self.lutarray need update with array of length 256')
            return
        self.lut_array = arr_256

    def calculate_lut_array_from_table(self):
        arr = []
        stindex = 0
        for i in range(256):
            if self.lutEditorTableWidget.item(i,1).text() != '':
                gma = self.lutEditorTableWidget.item(i,1).text()
                if gma in list(gammadict.keys()):
                    arr.extend(return_gma_array(str(gma),stindex,i))
                    stindex = i+1
        if len(arr) == 256:
            self.lut_array = arr
        else:
            print('lut array is not length 256 something went wrong')
     
    def print_lut_table_as_txt(self,save_path):
        with open(os.path.join(save_path,"how_to_lut.txt"),'a') as f:
            for i in range(256):
                f.write(str(i))
                f.write(' ')
                f.write(self.lutEditorTableWidget.item(i,0).text())
                f.write(' ')
                f.write(self.lutEditorTableWidget.item(i,1).text())
                f.write('\n')


    # ----------- functions for graphicview ----------- # 
       
    def wheelEvent_override_graphicview(self, event):
        delta = event.angleDelta().y()
        if delta < 0:
            #self.graphicview.scale(0.8,0.8)
            self.scale /= 1.2
        else:
            #self.graphicview.scale(1.2,1.2)
            self.scale *= 1.2
        self.setQPixmaptoScene(self.pixmap,self.scale)

    def rubberBandChanged_override(self, rubberBandRect, fromScenePoint, toScenePoint):

        if rubberBandRect.isNull():
            self.x = int( self.fromScenePoint.x() / (self.scale*self.scale_fit_box) )
            self.y = int( self.fromScenePoint.y() / (self.scale*self.scale_fit_box) )
            self.w = int( self.rubberBandRect.width() / (self.scale*self.scale_fit_box) )
            self.h = int( self.rubberBandRect.height() / (self.scale*self.scale_fit_box) )
            self.pixamp_crop = self.pixmap.copy(self.x,self.y,self.w,self.h)
            #self.setQPixmaptoScene(self.img_rubberBandRect)
            hist = cv2.calcHist([self.mat[self.y:self.y+self.h,self.x:self.x+self.w]],[0],None,[256],[0,256])
            self.labelzoom = LabelZoom(self.pixamp_crop)
            self.labelzoom.show()
            plt.figure()
            plt.plot(hist)
            plt.show()
            self.rubberBandRect = rubberBandRect
            self.graphicview.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self.graphicview.unsetCursor()
            
        else:
            self.rubberBandRect = rubberBandRect
            self.fromScenePoint = fromScenePoint

    def setimgPathtoScene(self,imgpath):
        # pimg = QtGui.QPixmap(imgpath)
        # self.setQPixmaptoScene(pimg)
        cwd = os.getcwd()  #
        imgdir = os.path.dirname(imgpath) #
        os.chdir(imgdir) # handle cv2 cannot read special character folder name
        self.mat = cv2.imread(os.path.basename(imgpath),0)
        os.chdir(cwd) #
        if self.lut_checkBox.isChecked() and (imgpath in self.imgpaths_scans):
            self.mat = cv2.LUT(self.mat,np.array(self.lut_array,dtype=np.uint8))
        height, width = self.mat.shape          
        qimg = QtGui.QImage(self.mat, width, height, width, QtGui.QImage.Format.Format_Grayscale8) 
        pimg = QtGui.QPixmap(width,height).fromImage(qimg)
        self.pixmap = pimg
        self.setQPixmaptoScene(pimg,self.scale)

    def setQPixmaptoScene(self,pimg,scale=1):
        self.scale_fit_box = self.graphicview.height() / pimg.height()
        pimg = pimg.scaled(int(pimg.width()*scale*self.scale_fit_box),int(pimg.height()*scale*self.scale_fit_box),QtCore.Qt.AspectRatioMode.KeepAspectRatio,QtCore.Qt.TransformationMode.SmoothTransformation)
        self.scene.setSceneRect(0, 0, pimg.width(),pimg.height())
        self.scene.clear()
        self.scene.addPixmap(pimg)
        self.graphicview.setScene(self.scene)

    # ----------- functions for export button 1 ----------- # 
    def exportfunc1(self):
        # create a temp folder
        cwd = os.getcwd()
        temp_folder = os.path.join(cwd, 'exportfunc1_temps')
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)
            
        # export lut-ed images as .jpg(s)
        for img_path in self.imgpaths_scans:
            imgdir = os.path.dirname(img_path) #
            os.chdir(imgdir) # handle cv2 cannot read special character folder name
            img_mat = cv2.imread(os.path.basename(img_path),0)
            if self.lut_checkBox.isChecked():
                img_mat = cv2.LUT(img_mat, np.array(self.lut_array,dtype=np.uint8))
            cv2.imwrite(temp_folder + '/' + os.path.basename(img_path), img_mat, [cv2.IMWRITE_JPEG_QUALITY , 70]) #for checking quality 80 - 100 too big file size
        # add how_to_lut.txt
        self.print_lut_table_as_txt(temp_folder)

        # zip the .jpg(s)
        os.chdir(temp_folder)
        zfname = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.zip'
        cmd_log1 = subprocess.check_output(['7z', 'a', '-tzip', '-mx0', zfname, '*.*'], text=True) # add argv -pyes for password 'yes'
        os.chdir(cwd)

        # move zip to android sd card with adb
        os.chdir(os.path.join(cwd, 'platform-tools')) # handle cv2 cannot read special character folder name
        try:
            cmd_log2 = subprocess.run(['adb', 'push', os.path.join(temp_folder, zfname), '/storage/3735-3631/Comics/previews'],capture_output=True, 
                       text=True)
        except:
            pass
        os.chdir(cwd) #

        # delete the temp folder
        shutil.rmtree(temp_folder)

        # show a ok message box
        mbox = QtWidgets.QMessageBox(self)
        mbox.setWindowTitle('adb output')
        mbox.setText(cmd_log2.stderr)
        mbox.exec()
        
    # ----------- functions for export button 2 ----------- # 
    def exportfunc2(self):
        for img_path in self.imgpaths_scans:
            img_filename = os.path.basename(img_path)
            imgdir = os.path.dirname(img_path) #
            imgdir_oneup = os.path.dirname(imgdir) #
            imgdir_onedown = imgdir + '/lut'
            if not os.path.exists(imgdir_onedown):
                os.makedirs(imgdir_onedown)
            
            
            cwd = os.getcwd()  #
            
            os.chdir(imgdir) # handle cv2 cannot read special character folder name
            mat = cv2.imread(img_filename,0)
            mat_lut = cv2.LUT(mat,np.array(self.lut_array,dtype=np.uint8))

            os.chdir(imgdir_onedown) # handle cv2 cannot read special character folder name
            cv2.imwrite(img_filename, mat_lut, [cv2.IMWRITE_JPEG_QUALITY , 95])

            os.chdir(cwd) #
            
    # ----------- functions for export button 3 ----------- # 
    def exportfunc3(self):    
        open('C:/Users/ASUS/Documents/new.gma', 'w').close() #erase content in origional .gma
        f = open('C:/Users/ASUS/Documents/new.gma', 'a')
        f.write('256,256,' + repr(self.lut_array).replace("[", "").replace("]", ""))
        f.close()

# Initialize the app
app = QtWidgets.QApplication(sys.argv)
window = UI()
window.showMaximized()
app.exec()