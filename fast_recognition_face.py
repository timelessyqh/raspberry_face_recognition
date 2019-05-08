#!/usr/bin/python36
# -*-coding:utf-8-*-
# @Time    : 19-5-3 下午7:01
# @Author  : Horus.Yao
# @FileName: fast_recognition_face.py
import sys
import os
import dlib,time,sqlite3
import glob
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from skimage import io
from datetime import datetime
import threading
from facepp import search_faceset,facetoken_name,addimage_faceset


def connect_sqlite(dbname='rsipberry.db'):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    return conn,cursor
def disconnect_sqlite(conn,cursor):
    cursor.close()
    conn.commit()
    conn.close()

def create_table():     ##需要先创建表
    conn,cursor=connect_sqlite()
    cursor.execute('create table attend_log (id INTEGER PRIMARY key AUTOINCREMENT, name varchar(20), number varchar(20),class varchar(20),time datetime)')
    cursor.close()
    conn.commit()
    conn.close()

def select_sqlite(dbname='rsipberry.db'):
    import sqlite3
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute('select * from attend_log')
    return cursor.fetchall()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer_camera = QTimer()  # 需要定时器刷新摄像头界面
        self.cap = cv2.VideoCapture()
        self.cap_num = 0
        self.set_ui()  # 初始化UI界面
        self.slot_init()  # 初始化信号槽
        self.btn_flag = 0  # 开关变量
        self.local_data = []
        self.face_flag=''
    def set_ui(self):
        # 布局设置
        self.layout_main = QHBoxLayout()  # 整体框架是水平布局
        self.layout_button = QVBoxLayout()

        #欢迎词
        # self.label_welcome = QLabel('欢迎进入课堂考勤界面  Powered by tyut')

        # 按钮设置
        self.btn_open_cam = QPushButton('打开相机')
        self.btn_photo = QPushButton('录入数据')
        self.btn_detection_face = QPushButton('人脸检测')
        self.btn_recognition_face = QPushButton('人脸识别')

        self.btn_quit = QPushButton('退出')

        # 显示视频
        self.label_show_camera = QLabel()

        self.setWindowIcon(QIcon('images/logo.jpg'))
        self.label_move = QLabel()
        self.label_move.setFixedSize(100, 50)

        self.label_show_camera.setFixedSize(641, 481)
        self.label_show_camera.setAutoFillBackground(False)

        self.background = QPixmap("images/background6.jpg").scaled(self.label_show_camera.width(),self.label_show_camera.height())
        self.label_show_camera.setPixmap(self.background)

        self.button_widget=QWidget()
        self.button_widget.setLayout(self.layout_button)

        # 布局
        self.layout_button.addWidget(self.btn_open_cam)
        self.layout_button.addWidget(self.btn_photo)
        self.layout_button.addWidget(self.btn_detection_face)
        self.layout_button.addWidget(self.btn_recognition_face)
        self.layout_button.addWidget(self.btn_quit)
        self.layout_button.addWidget(self.label_move)


        self.layout_main.addWidget(self.button_widget)

        self.layout_main.addWidget(self.label_show_camera)

        # self.setWindowFlag(Qt.FramelessWindowHint) # 隐藏边框

        self.layout_main.setSpacing(0)

        self.button_widget.setStyleSheet('''
            QPushButton{border:none;color:white;}
            QPushButton{
                height:22px;
                width:30px;
                border:none;
                font-size:14px;
                font-weight:700;
                font-family: "宋体", Helvetica, Arial, sans-serif;
            }
            QPushButton:hover{
                font-size:18px;
                border-bottom:2px solid white;
            }
            QWidget{
                background:gray;
            }
        ''')

        # self.button_widget.setStyleSheet('''
        #  border-top:1px solid white;
            # border-bottom:1px solid white;
            # border-left:1px solid white;
            # border-right:1px solid white;
            # border-top-left-radius:50px;
            # border-bottom-left-radius:50px;
        #     QPushButton{
        #         border:none;
        #         color:gray;
        #         font-size:12px;
        #         height:40px;
        #         padding-left:5px;
        #         padding-right:10px;
        #         text-align:center;
        #     }
        #     QPushButton:hover{
        #         color:black;
        #         border:1px solid #F3F3F5;
        #         border-radius:10px;
        #         background:LightGray;
        #     }
        # ''')
         
         
        # self.layout_main.addWidget(self.label_welcome)
        self.setLayout(self.layout_main)
        self.setGeometry(300, 200, 600, 400)
        self.setWindowTitle("课堂考勤系统 Powered by tyut")

    # 信号槽设置
    def slot_init(self):
        self.btn_open_cam.clicked.connect(self.btn_open_cam_click)
        self.btn_photo.clicked.connect(self.photo_face)
        self.btn_detection_face.clicked.connect(self.detect_face)
        self.btn_recognition_face.clicked.connect(self.recognize_face)
        self.timer_camera.timeout.connect(self.show_camera)
        self.btn_quit.clicked.connect(self.close)

    def btn_open_cam_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.cap_num)
            if flag == False:
                msg = QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QMessageBox.Ok,
                                          defaultButton=QMessageBox.Ok)
            # if msg==QtGui.QMessageBox.Cancel:
            #                     pass
            else:
                self.timer_camera.start(30)

                # self.layout_main.hideWidget(self.label_welcome)

                self.btn_open_cam.setText(u'关闭相机')
        else:
            self.timer_camera.stop()
            self.cap.release()
            # self.label_show_camera.clear()
            self.label_show_camera.setPixmap(self.background)
            self.btn_open_cam.setText(u'打开相机')

    def show_camera(self):
        harr_filepath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # 系统安装的是opencv-contrib-python
        classifier = cv2.CascadeClassifier(harr_filepath)  # 加载人脸特征分类器
        if self.btn_flag == 0:
            ret, self.image = self.cap.read()
            show = cv2.resize(self.image, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
            # int height, Format format, QImageCleanupFunction cleanupFunction = 0, void *cleanupInfo = 0)
            self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(self.showImage))
        elif self.btn_flag == 1:  # 人脸检测
            ret_1, self.image_1 = self.cap.read()
            show_0 = cv2.resize(self.image_1, (640, 480))
            show_1 = cv2.cvtColor(show_0, cv2.COLOR_BGR2RGB)
            gray_image = cv2.cvtColor(show_0, cv2.COLOR_BGR2GRAY)
            faces = classifier.detectMultiScale(gray_image, 1.3, 5)  # 1.3和5是特征的最小、最大检测窗口，它改变检测结果也会改变
            for (x, y, w, h) in faces:
                cv2.rectangle(show_1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 画出人脸
            detect_image = QImage(show_1.data, show_1.shape[1], show_1.shape[0],
                                  QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(detect_image))

        elif self.btn_flag == 2:  # 人脸识别
            ret_1, self.image_2 = self.cap.read()  ##这四行的目的是为了让摄像头的图像移动，如果没有为图片
            show = cv2.resize(self.image_2, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(self.showImage))
            
            now_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                       'now.jpg')
            self.showImage.save(now_save_path)         ##截图，当前摄像头的图像保存为now()
            
            key = "<your faceplusplus key>"
            secret = "<your faceplusplus secretkey>"
            if search_faceset(key,secret,'now.jpg') != 0:
                res = facetoken_name(search_faceset(key,secret,'now.jpg'))
                if self.face_flag=='' or self.face_flag!=res:
                    print("匹配成功，data：%s"%res)
                    Time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    conn,cursor=connect_sqlite()
                    cursor.execute('insert into attend_log (name,number,class,time) values ("%s","%s","%s","%s")'%(res[0],res[1],res[2],Time))
                    disconnect_sqlite(conn,cursor)
                    infoBox = QMessageBox(self)
                    infoBox.setText(u"打卡成功！\n姓名：%s\n学号：%s\n班级：%s\n时间：%s\n\n3秒后自动退出"%(res[0],res[1],res[2],Time))
                    infoBox.setWindowTitle("Success")
                    infoBox.setStandardButtons(QMessageBox.Ok)
                    infoBox.button(QMessageBox.Ok).animateClick(3 * 1000)
                    infoBox.exec_()
                    self.face_flag=res
            # print("打卡成功，信息%s"%res)
            # time.sleep(10)

    def detect_face(self):
        if self.timer_camera.isActive() == False:            
            infoBox = QMessageBox(self)
            infoBox.setText(u"请您确保已经打开相机!")
            infoBox.setWindowTitle("Info")
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.exec_()
        else:
            if self.btn_flag == 0:
                self.btn_flag = 1
                self.btn_detection_face.setText(u'关闭人脸检测')
            elif self.btn_flag == 1:
                self.btn_flag = 0
                self.btn_detection_face.setText(u'人脸检测')

    def recognize_face(self):
        if self.timer_camera.isActive() == False:            
            infoBox = QMessageBox(self)
            infoBox.setText(u"请您确保已经打开相机!")
            infoBox.setWindowTitle("Info")
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.exec_()
        else:
            if self.btn_flag == 0:
                self.btn_flag = 2
                self.btn_recognition_face.setText(u'关闭人脸识别')
            elif self.btn_flag == 2:
                self.btn_flag = 0
                self.btn_recognition_face.setText(u'人脸识别')

    def photo_face(self):
        if self.timer_camera.isActive() == False:            
            infoBox = QMessageBox(self)
            infoBox.setText(u"请您确保已经打开相机!")
            infoBox.setWindowTitle("Info")
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.exec_()

        else:
            name,ok = QInputDialog.getText(self,u"录入人脸",u"输入(姓名_学号_班级):")
            if ok and (len(name)>5):

                photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                           'candidate-faces/')
                infoBox = QMessageBox(self)
                infoBox.setText(u"2秒后自动截取人脸图像！")
                infoBox.setWindowTitle("Attention")
                infoBox.setStandardButtons(QMessageBox.Ok)
                infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)
                infoBox.exec_()

                filepath = photo_save_path + name + ".jpg"
                self.showImage.save(filepath)

                infoBox = QMessageBox(self)
                infoBox.setText(u"录入信息成功！\n姓名：%s\n学号：%s\n班级：%s\n\n2秒后自动退出"%(name.split('_')[0],name.split('_')[1],name.split('_')[2]))
                infoBox.setWindowTitle("Success")
                infoBox.setStandardButtons(QMessageBox.Ok)
                infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)
                infoBox.exec_()
                addimage_faceset(filepath)
            elif ok and len(name)<=5:
                QMessageBox.information(self,u"警告",u"输入长度过小",QMessageBox.Yes)


    def closeEvent(self, QCloseEvent):

        reply = QMessageBox.question(self,u"Warning", "Are you sure quit ?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cap.release()
            self.timer_camera.stop()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
