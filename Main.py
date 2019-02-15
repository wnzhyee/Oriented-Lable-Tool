#coding=utf-8

import sys
import os
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainUI(QMainWindow):

    def __init__(self):
        super().__init__()

        self._count = -1
        self._filelist = []
        self._labellist = []
        self._cur_label = []
        self._openfirstimage = False
        self._width = 0
        self._height = 0
        self._firstopen = True
        self._imagearea_rect = QRect()

        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('LabelIt')
        
        self.desktop = QApplication.desktop()
        self._width = self.desktop.width()
        self._height = self.desktop.height()

        # Toolbar
        # self.toolbar = self.addToolBar('toolbar')
        self.toolbar = QToolBar('toolbar')
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        self.initToolbarButtons()

        # Workbar
        self.workbar = QWidget()
        self.setCentralWidget(self.workbar)
        self.workbar_layout = QHBoxLayout()

        self.createImageArea()
        self.workbar_layout.addWidget(self.image_area)
        self.func_area_layout = QVBoxLayout()
        self.createAnnoShowArea()
        self.createLabelEditArea()
        self.func_area_layout.addWidget(self.anno_groupbox)
        self.func_area_layout.addWidget(self.labeledit_groupbox)
        self.workbar_layout.addLayout(self.func_area_layout)
        self.workbar.setLayout(self.workbar_layout)

        self.showMaximized()
    
    def createImageArea(self):
        self.image_area = Canvas()
        self.image_area.setFixedSize(QSize(int(self._width*0.8),int(self._height*0.9)))
        # self.image_area.setGeometry(0, 0, int(self._width*0.8),int(self._height*0.9))
        self._imagearea_rect = QRect(self.image_area.pos(),
                                     self.image_area.size())
    
    def createAnnoShowArea(self):
        self.anno_groupbox = QGroupBox('Annotations')
        self.anno_groupbox.setFixedSize(QSize(int(self._width*0.18),int(self._height*0.55)))

        self.anno_groupbox_layout = QGridLayout()
        self.anno_groupbox_layout.setAlignment(Qt.AlignTop | Qt.AlignVCenter)
        # self.anno_groupbox_layout.setSpacing(10)

        idx_col = QLabel('Idx')
        label_col = QLabel('Label')
        point1_col = QLabel('point1')
        point2_col = QLabel('point2')
        point3_col = QLabel('point3')
        point4_col = QLabel('point4')

        self.anno_groupbox_layout.addWidget(idx_col, 0, 0)
        self.anno_groupbox_layout.addWidget(label_col, 0, 1)
        self.anno_groupbox_layout.addWidget(point1_col, 0, 2)
        self.anno_groupbox_layout.addWidget(point2_col, 0, 3)
        self.anno_groupbox_layout.addWidget(point3_col, 0, 4)
        self.anno_groupbox_layout.addWidget(point4_col, 0, 5)

        self.anno_groupbox_layout.setColumnStretch(0,1)
        self.anno_groupbox_layout.setColumnStretch(1,1)
        for i in range(2,6):
            self.anno_groupbox_layout.setColumnStretch(i,3)
        self.anno_groupbox.setLayout(self.anno_groupbox_layout)
    
    def createLabelEditArea(self):
        self.labeledit_groupbox = QGroupBox('Edit')
        self.labeledit_groupbox.setFixedSize(QSize(int(self._width*0.18),int(self._height*0.35)))
        self.labeledit_groupbox_layout = QGridLayout()

        self.labeledit_groupbox_layout.setAlignment(Qt.AlignTop)
        self.label_num = 1

        button = QPushButton('Class 1')
        button.setShortcut('1')
        button.setFixedSize(QSize(int(self._width*0.16),30))
        button.clicked.connect(lambda: self.getClickedLabel(button.text()))
        self.labeledit_groupbox_layout.addWidget(button, 1, 0)

        button_add = QPushButton('Add')
        button_add.setShortcut(Qt.Key_Equal)
        
        button_add.setFixedSize(QSize(int(self._width*0.079),30))
        button_add.clicked.connect(lambda: self.addLabelButton())
        self.labeledit_groupbox_layout.addWidget(button_add, 0, 0)

        button_del = QPushButton('Delete')
        button_del.setShortcut(Qt.Key_Minus)
        button_del.setFixedSize(QSize(int(self._width*0.079),30))
        button_del.clicked.connect(lambda: self.delLabelButton())
        self.labeledit_groupbox_layout.addWidget(button_del, 0, 1)

        self.labeledit_groupbox.setLayout(self.labeledit_groupbox_layout)

    def initToolbarButtons(self):
        openFileAction = QAction('Open', self)
        openFileAction.setShortcut(Qt.Key_O)
        openFileAction.setStatusTip('Open a dir')
        openFileAction.triggered.connect(self.showDialog)
        self.toolbar.addAction(openFileAction)

        quitAction = QAction('Quit', self)
        quitAction.setShortcut(Qt.Key_Q)
        quitAction.setStatusTip('Quit')
        quitAction.triggered.connect(QApplication.quit)
        self.toolbar.addAction(quitAction)

        saveAction = QAction('Save', self)
        saveAction.setShortcut(Qt.Key_S)
        saveAction.setStatusTip('Save')
        saveAction.triggered.connect(lambda: self.saveLabelfile(True))
        self.toolbar.addAction(saveAction)

        lastFileAction = QAction('Last', self)
        lastFileAction.setShortcut(Qt.Key_L)
        lastFileAction.setStatusTip('Last image')
        lastFileAction.triggered.connect(self.lastImage)
        self.toolbar.addAction(lastFileAction)

        nextFileAction = QAction('Next', self)
        nextFileAction.setShortcut(Qt.Key_N)
        nextFileAction.setStatusTip('Next image')
        nextFileAction.triggered.connect(self.nextImage)
        self.toolbar.addAction(nextFileAction)
    
    # get images list and show first image
    def showDialog(self):
        self._filelist = []
        self._openfirstimage = False
        self._fname = QFileDialog.getExistingDirectory(self, 'Open') 

        if self._fname:
            for _, _, filenames in os.walk(self._fname):
                for each in filenames:
                    if each[-3:] in ['png', 'jpg'] or each[-4:] == 'jpeg':
                        self._filelist.append(each)
        
        if len(self._filelist) > 0:
            self._count = 0
            self.showOneImage()
            self._openfirstimage = True
        else:
            QMessageBox.information(self,'警告','未找到图片！')
    
    def lastImage(self):
        if self._openfirstimage:
            if self._count == 0:
                QMessageBox.information(self,'警告','这已经是第一张了！')
            else:
                self.saveLabelfile()
                self._count -= 1
                self.showOneImage()

    def nextImage(self):
        if self._openfirstimage:
            if self._count == len(self._filelist)-1:
                QMessageBox.information(self,'警告','这已经是最后一张了！')
            else:
                self.saveLabelfile()
                self._count += 1
                self.showOneImage()
    
    def showOneImage(self):
        filename = self._fname + '/' + self._filelist[self._count]
        ori_img = cv2.imread(filename)
        pixmap = QPixmap(filename)
        temp_pixmap = pixmap.scaled(QSize(int(self._width*0.8),int(self._height*0.8)),
                                    Qt.KeepAspectRatio)
        self.image_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.image_area.setAlignment(Qt.AlignJustify)
        self.image_area.setPixmap(temp_pixmap)
        self.image_area.move(0,0)
        self.image_area.scale_x = ori_img.shape[1] * 1.0 / temp_pixmap.width()
        self.image_area.scale_y = ori_img.shape[0] * 1.0 / temp_pixmap.height()
        print(ori_img.shape[1], temp_pixmap.width())

        labelfile = self._fname + '/' + self._filelist[self._count].split('.')[0] + '.txt'
        if not os.path.exists(labelfile):
            open(labelfile,'w').close()
        label_read = open(labelfile, 'r')
        self._labellist = label_read.readlines()
        self.image_area.points = []
        if len(self._labellist) > 0:
            for i in range(len(self._labellist)):
                items = self._labellist[i].split(' ')
                idx = QLabel(str(i+1))
                label = QLabel(items[1])
                point1 = QLabel(items[2])
                self.image_area.points.append(QPoint(int(int(items[2].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(items[2].split(',')[1].split(')')[0])/self.image_area.scale_y)))
                point2 = QLabel(items[3])
                self.image_area.points.append(QPoint(int(int(items[3].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(items[3].split(',')[1].split(')')[0])/self.image_area.scale_y)))
                point3 = QLabel(items[4])
                self.image_area.points.append(QPoint(int(int(items[4].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(items[4].split(',')[1].split(')')[0])/self.image_area.scale_y)))
                point4 = QLabel(items[5].split('\n')[0])
                self.image_area.points.append(QPoint(int(int(items[5].split('\n')[0].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(items[5].split('\n')[0].split(',')[1].split(')')[0])/self.image_area.scale_y)))

                self.anno_groupbox_layout.addWidget(idx, i+1, 0)
                self.anno_groupbox_layout.addWidget(label, i+1, 1)
                self.anno_groupbox_layout.addWidget(point1, i+1, 2)
                self.anno_groupbox_layout.addWidget(point2, i+1, 3)
                self.anno_groupbox_layout.addWidget(point3, i+1, 4)
                self.anno_groupbox_layout.addWidget(point4, i+1, 5)
        self.image_area.repaint()
        label_read.close()
    
    def saveLabelfile(self, save_pressed = False):
        labelfile = self._fname + '/' + self._filelist[self._count].split('.')[0] + '.txt'
        label_write = open(labelfile, 'w')
        if (not save_pressed) and (len(self._labellist) > 0):
            for i in range(len(self._labellist)):
                for j in range(6):
                    item = self.anno_groupbox_layout.itemAtPosition(i+1, j)
                    item.widget().setParent(None)
        label_write.writelines(self._labellist)
        label_write.close()
    
    def addLabelButton(self):
        self.label_num += 1
        button = QPushButton('Class %d' % self.label_num)
        button.setShortcut('%d' % self.label_num)
        button.setFixedSize(QSize(int(self._width*0.16),30))
        button.clicked.connect(lambda: self.getClickedLabel(button.text()))
        self.labeledit_groupbox_layout.addWidget(button, self.label_num, 0)
    
    def delLabelButton(self):
        if self.label_num > 1:
            item = self.labeledit_groupbox_layout.itemAtPosition(self.label_num, 0)
            item.widget().setParent(None)
            self.label_num -= 1
        else:
            QMessageBox.information(self, '警告', '最少应有1个标签！')
    
    def getClickedLabel(self, labeltext):
        if len(self._cur_label) == 3:
            x = 0
            y = 0
            for i in range(3):
                x += pow(-1,i)*int(self._cur_label[i].split(',')[0].split('(')[1])
                y += pow(-1,i)*int(self._cur_label[i].split(',')[1].split(')')[0])
            self._cur_label.append('('+str(x)+','+str(y)+')')
        if len(self._cur_label) == 4:
            # self.refineRect()
            label = QLabel(labeltext.split(' ')[1])
            self._labellist.append(self._filelist[self._count]+' '+labeltext.split(' ')[1]+' '+' '.join(self._cur_label)+'\n')
            length = len(self._labellist)
            idx = QLabel(str(length))
            point1 = QLabel(self._cur_label[0])
            point2 = QLabel(self._cur_label[1])
            point3 = QLabel(self._cur_label[2])
            point4 = QLabel(self._cur_label[3])

            self.anno_groupbox_layout.addWidget(idx, length, 0)
            self.anno_groupbox_layout.addWidget(label, length, 1)
            self.anno_groupbox_layout.addWidget(point1, length, 2)
            self.anno_groupbox_layout.addWidget(point2, length, 3)
            self.anno_groupbox_layout.addWidget(point3, length, 4)
            self.anno_groupbox_layout.addWidget(point4, length, 5)
            for i in range(4):
                self.image_area.points.append(QPoint(int(int(self._cur_label[i].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(self._cur_label[i].split(',')[1].split(')')[0])/self.image_area.scale_y)))
            self.image_area.repaint()
            self._cur_label = []

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and event.buttons() == Qt.NoButton:
            pos = event.pos()
            # if len(self._cur_label) < 4:
            #     self.image_area.drawing.append(pos)
            #     self.image_area.repaint()
            if len(self._cur_label) == 1:
                self.image_area.temp_points.append(QPoint(int(int(self._cur_label[0].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                                     int(int(self._cur_label[0].split(',')[1].split(')')[0])/self.image_area.scale_y)))
                self.image_area.temp_points.append(pos)
                self.image_area.repaint()
                self.image_area.temp_points = []
            if len(self._cur_label) == 2:
                point1 = QPoint(int(int(self._cur_label[0].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                int(int(self._cur_label[0].split(',')[1].split(')')[0])/self.image_area.scale_y))
                point2 = QPoint(int(int(self._cur_label[1].split(',')[0].split('(')[1])/self.image_area.scale_x),
                                int(int(self._cur_label[1].split(',')[1].split(')')[0])/self.image_area.scale_y))
                self.image_area.temp_points.append(point1)
                self.image_area.temp_points.append(point2)                                    
                #self.image_area.temp_points.append(pos)
                if self.isVertical(point1,point2,pos):
                    self.image_area.temp_points.append(pos)
                self.image_area.repaint()
                self.image_area.temp_points = []
        else:
            pass
        return QMainWindow.eventFilter(self,source,event)
    
    def isVertical(self, point1, point2, pos):
        if point1.x() == point2.x():
            if point2.y() == pos.y() or abs((pos.y()-point2.y()))/(abs(pos.x()-point2.x())+0.1) < 0.05:
                return True
            else:
                return False
        elif point1.y() == point2.y():
            if point2.x() == pos.x() or abs((pos.x()-point2.x()))/(abs(pos.y()-point2.y())+0.1) < 0.05:
                return True
            else:
                return False
        else:
            if pos.x() == point2.x() or pos.y() == point2.y():
                return False
            grad_1_2 = (point2.y()-point1.y())/(point2.x()-point1.x())
            grad_2_3 = (pos.y()-point2.y())/(pos.x()-point2.x())
            if grad_1_2*grad_2_3 < -0.9 and grad_1_2*grad_2_3 > -1.1:
                return True
            else:
                return False

    def mousePressEvent(self, event):
        # if self._imagearea_rect.contains(event.pos()):
        if True:
            if event.button() == Qt.LeftButton:
                x = max(int((event.x()-self.image_area.delta_x)*self.image_area.scale_x), 0)
                y = max(int((event.y()-self.image_area.delta_y)*self.image_area.scale_y), 0)
                self._cur_label.append('('+str(x)+','+str(y)+')')

            if event.button() == Qt.RightButton:
                if len(self._cur_label) > 0:
                    self._cur_label.pop()
            
            if len(self._cur_label) > 4:
                QMessageBox.information(self, '警告', '未检测到输入标签(Label)，请重新输入！')
                del self._cur_label[-1]

class Canvas(QLabel):
    def __init__(self, drawing = []):
        super().__init__()
        self.points = []
        self.temp_points = []
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.delta_x = 0
        self.delta_y = 0
        # self.drawing = drawing

    def paintEvent(self, event):
        super().paintEvent(event)

        if len(self.points) % 4 == 0 and self.points:
            painter = QPainter(self)
            painter.begin(self)

            for i in range(int(len(self.points)/4)):
                path = QPainterPath()
                path.moveTo(self.points[i*4])
                path.lineTo(self.points[i*4+1])
                path.lineTo(self.points[i*4+2])
                path.lineTo(self.points[i*4+3])
                path.closeSubpath()

                painter.setPen(QPen(QColor(255,0,0),2,Qt.SolidLine))
                painter.drawPath(path)
            
            painter.end()

        if len(self.temp_points) == 2:
            painter = QPainter(self)
            painter.begin(self)

            path = QPainterPath()
            path.moveTo(self.temp_points[0])
            path.lineTo(self.temp_points[1])
            path.closeSubpath()

            painter.setPen(QPen(QColor(255,0,0),2,Qt.DashLine))
            painter.drawPath(path)
            
            painter.end()
            self.temp_points = []

        if len(self.temp_points) == 3:
            painter = QPainter(self)
            painter.begin(self)

            path = QPainterPath()
            path.moveTo(self.temp_points[0])
            path.lineTo(self.temp_points[1])
            path.moveTo(self.temp_points[1])
            path.lineTo(self.temp_points[2])
            path.closeSubpath()           

            painter.setPen(QPen(QColor(255,0,0),2,Qt.DashLine))
            painter.drawPath(path)
            
            painter.end()
            self.temp_points = []
        
        # if len(self.drawing) == 1:
        #     painter = QPainter(self)
        #     painter.begin(self)

        #     x = self.drawing[0].x()
        #     y = self.drawing[0].y()
        #     path = QPainterPath()
        #     path.moveTo( QPoint(max(0,x-50), y) )
        #     path.lineTo( QPoint(x+50, y) )
        #     path.moveTo( QPoint(x, max(0,y-50)) )
        #     path.lineTo( QPoint(x, y+50) )
        #     path.closeSubpath()
        #     self.drawing = []
        #     painter.end()

if __name__ == '__main__':
    app = QApplication(sys.argv) 
    mainui = MainUI()
    mainui.show()
    app.installEventFilter(mainui)
    sys.exit(app.exec_())
