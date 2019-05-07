#!/usr/bin/python3
# -*-coding:utf-8-*-
# @Time    : 19-5-3 下午7:01
# @Author  : Horus.Yao
# @FileName: manage_face.py
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
    cursor.execute('create table people_facetoken (id INTEGER PRIMARY key AUTOINCREMENT, name varchar(20), number varchar(20),class varchar(20),facetoken varchar(50),time datetime)')
    cursor.close()
    conn.commit()
    conn.close()

def select_sqlite(dbname='rsipberry.db'):
    import sqlite3
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute('select * from people_facetoken')
    return cursor.fetchall()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.log_click_flag,self.people_click_flag,self.search_click_flag = 0,0,0
        self.set_ui()  # 初始化UI界面
        self.slot_init()  # 初始化信号槽
        # self.dlib_para_init()
        self.btn_flag = 0  # 开关变量
        self.local_data = []
    def set_ui(self):
        # 布局设置
        self.layout_main = QHBoxLayout()  # 整体框架是水平布局
        self.layout_button = QVBoxLayout()

        #欢迎词
        # self.label_welcome = QLabel('欢迎进入课堂考勤界面  Powered by tyut')

        # 按钮设置
        self.btn_attend_log = QPushButton('考勤记录')
        self.btn_people = QPushButton('人员记录')
        self.btn_search = QPushButton('搜索记录')
        self.btn_selfsearch = QPushButton('自助查询')
        self.btn_quit = QPushButton('退出')

        self.setWindowIcon(QIcon('images/logo.jpg'))

        self.show_background = QLabel()
        self.show_background.setFixedSize(460, 400)
        # self.show_background.setAutoFillBackground(False)

        self.background = QPixmap("images/background4.jpg").scaled(self.show_background.width(),self.show_background.height())
        self.show_background.setPixmap(self.background)

        self.button_widget=QWidget()
        self.button_widget.setLayout(self.layout_button)

        # 布局
        self.layout_button.addWidget(self.btn_attend_log)
        self.layout_button.addWidget(self.btn_people)
        self.layout_button.addWidget(self.btn_search)
        self.layout_button.addWidget(self.btn_selfsearch)
        self.layout_button.addWidget(self.btn_quit)

        # self.layout_button.addWidget(self.label_move)
        self.button_widget.setFixedSize(120, 400)


        self.layout_main.addWidget(self.button_widget)
        self.layout_main.addWidget(self.show_background)
        # self.layout_main.setSpacing(0)

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
        # self.layout_main.addWidget(self.label_show_camera)

        
        # self.layout_main.addWidget(self.label_welcome)
        self.setLayout(self.layout_main)
        self.setGeometry(400, 200, 600, 400)
        self.setWindowTitle("课堂考勤系统后台管理 Powered by tyut")
    def slot_init(self):
        self.btn_attend_log.clicked.connect(self.attend_log_click)
        self.btn_people.clicked.connect(self.people_click)
        self.btn_search.clicked.connect(self.search_click)
        self.btn_selfsearch.clicked.connect(self.selfsearch_click)
        
        self.btn_quit.clicked.connect(self.close)

    def attend_log_click(self):
        try:
            self.showTable.hide()
            self.search_widget.hide()
            self.name_line.hide()
            self.number_line.hide()
            self.class_line.hide()
            self.pushButton.hide()
            self.startLabel.hide()        
            self.startDatetime.hide()        
            self.endLabel.hide()        
            self.endDatetime.hide()
        except:
            pass
        try:
            self.show_background.hide()
        except:
            pass
        # self.attend_log_frame =QFrame()
        # self.layout_search = QVBoxLayout(self.attend_log_frame)
        self.layout_search = QVBoxLayout()
        self.layout_main.addLayout(self.layout_search)
        conn,cursor = connect_sqlite()
        cursor.execute('select * from attend_log order by id desc')
        res = cursor.fetchall()
        self.showTable=QTableWidget(len(res),4)
        self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
        for i in range(len(res)):
            # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
            self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
            self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
            self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
            self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
        self.layout_search.addWidget(self.showTable)
        # self.attend_log_frame.setVisible(True)
        # 
        # self.setLayout(self.layout_main)
        # self.btn_attend_log.setText('关闭考勤记录')
        # self.log_click_flag=1

        # else:
        #     self.showTable.hide()
        #     self.btn_attend_log.setText('考勤记录')
        #     self.log_click_flag=0

    def search_click(self):
        try:
            self.showTable.hide()
            self.search_widget.hide()
            self.name_line.hide()
            self.number_line.hide()
            self.class_line.hide()
            self.pushButton.hide()
            self.startLabel.hide()        
            self.startDatetime.hide()        
            self.endLabel.hide()        
            self.endDatetime.hide()
        except:
            pass
        try:
            self.show_background.hide()
        except:
            pass
        self.search_widget=QWidget()
        self.layout_search = QVBoxLayout()
        # self.label_show_camera = QLabel('gadgad')
        # 
        
        self.showTable=QTableWidget(0,4)
        self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])   
    

        self.layout_search_time = QHBoxLayout()
        self.layout_search_info = QHBoxLayout()
        self.search_widget.setLayout(self.layout_search)
        self.search_widget.setFixedSize(460,400)

        self.startLabel = QLabel('开始时间')
        self.startDatetime = QDateTimeEdit(QDateTime.currentDateTime().addDays(-365))

        self.endLabel = QLabel('结束时间')
        self.endDatetime = QDateTimeEdit(QDateTime.currentDateTime())

        self.name_line = QLineEdit()
        self.name_line.setPlaceholderText('输入姓名')
        self.name_line.setFixedSize(110,20)
        self.number_line = QLineEdit()
        self.number_line.setPlaceholderText('输入学号')
        self.number_line.setFixedSize(110,20)
        self.class_line = QLineEdit()
        self.class_line.setPlaceholderText('输入班级')
        self.class_line.setFixedSize(110,20)
        # self.label_move = QLabel()
        # self.label_move.setFixedSize(100, 200)
        # self.label_show_camera.setFixedSize(641, 481)
        self.pushButton = QPushButton()
        self.pushButton.clicked.connect(self.get_search)
        self.pushButton.setText('搜索')
        self.pushButton.setFixedSize(70,20)
        # self.layout_search.addWidget(self.label_show_camera)
        self.layout_search.addLayout(self.layout_search_time)
        self.layout_search_time.addWidget(self.startLabel)        
        self.layout_search_time.addWidget(self.startDatetime)        
        self.layout_search_time.addWidget(self.endLabel)        
        self.layout_search_time.addWidget(self.endDatetime)

        self.layout_search.addLayout(self.layout_search_info)
        self.layout_search_info.addWidget(self.name_line)
        self.layout_search_info.addWidget(self.number_line)
        self.layout_search_info.addWidget(self.class_line)
        self.layout_search_info.addWidget(self.pushButton)
        self.layout_search.addWidget(self.showTable)
        
        # self.search_widget.setStyleSheet('''
        #     QPushButton{
        #         border:none;
        #         font-size:15px;
        #         height:20px;
        #     }
        #     QPushButton:hover{
        #         font-size:18px;
        #         font-family:"黑体"
        #     }            
        # ''')
        self.layout_main.addWidget(self.search_widget)
        



    def get_search(self):
        try:
            self.showTable.hide()
        except:
            pass

        conn,cursor = connect_sqlite()

        Name = self.name_line.text()
        Number = self.number_line.text()
        Class = self.class_line.text()

        start_time = self.startDatetime.dateTime()
        end_time = self.endDatetime.dateTime()
        start_time = start_time.toString(Qt.ISODate).replace('T',' ')
        end_time = end_time.toString(Qt.ISODate).replace('T',' ')
        
        if Name =='' and Number =='' and Class=='':
            # QMessageBox.warning(self,"警告","未输入信息",QMessageBox.Yes)
            cursor.execute('select * from attend_log where time<"%s" and time>"%s"'%(end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)

        elif Name =='' and Number =='' and Class!='':
            cursor.execute('select * from attend_log where class="%s" and time<"%s" and time>"%s"'%(Class,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name =='' and Number!='' and Class!='':
            cursor.execute('select * from attend_log where class="%s" and number="%s" and time<"%s" and time>"%s"'%(Class,Number,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name !='' and Number!='' and Class!='':
            cursor.execute('select * from attend_log where name="%s" and class="%s" and number="%s" and time<"%s" and time>"%s"'%(Name,Class,Number,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name !='' and Number!='' and Class=='':
            cursor.execute('select * from attend_log where name="%s" and number="%s" and time<"%s" and time>"%s"'%(Name,Number,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name !='' and Number=='' and Class!='':
            cursor.execute('select * from attend_log where name="%s" and class="%s"  and time<"%s" and time>"%s"'%(Name,Class,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name =='' and Number!='' and Class=='':
            cursor.execute('select * from attend_log where number="%s" and time<"%s" and time>"%s"'%(Number,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)
        elif Name !='' and Number=='' and Class=='':
            cursor.execute('select * from attend_log where name="%s" and time<"%s" and time>"%s"'%(Name,end_time,start_time))
            res = cursor.fetchall()

            self.showTable=QTableWidget(len(res),4)
            self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','打卡时间'])
            for i in range(len(res)):
                # self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][0])))  #id
                self.showTable.setItem(i,0,QTableWidgetItem(str(res[i][1])))    #姓名
                self.showTable.setItem(i,1,QTableWidgetItem(str(res[i][2])))    #学号
                self.showTable.setItem(i,2,QTableWidgetItem(str(res[i][3])))    #班级
                self.showTable.setItem(i,3,QTableWidgetItem(str(res[i][4])))    #打卡时间
            self.layout_search.addWidget(self.showTable)

    def selfsearch_click(self):
        try:
            self.showTable.hide()
            self.search_widget.hide()
            self.name_line.hide()
            self.number_line.hide()
            self.class_line.hide()
            self.pushButton.hide()
            self.startLabel.hide()        
            self.startDatetime.hide()        
            self.endLabel.hide()        
            self.endDatetime.hide()
        except:
            pass
        try:
            self.show_background.hide()
        except:
            pass
        
        self.search_widget=QWidget()
        self.layout_search = QVBoxLayout()
        self.layout_style = QHBoxLayout()

        self.search_widget.setLayout(self.layout_search)
        self.search_widget.setFixedSize(460,400)

        self.search_sql = QTextEdit()
        self.search_sql.setPlaceholderText('输入您查询的sql语句,表名attend_log,字段分别为id,name(姓名),class(班级),number(学号),time(时间,格式yyyy-mm-dd hh-mm--ss)')
        self.search_sql.setFixedSize(460,65)

        self.empty_label = QLabel()
        self.empty_label.setFixedSize(400,30)

        self.pushButton = QPushButton()
        self.pushButton.clicked.connect(self.get_selfsearch)
        self.pushButton.setText('提交')
        self.pushButton.setFixedSize(50,30)
        self.showTable=QTableWidget(0,4)

      

        self.layout_search.addWidget(self.search_sql)
        self.layout_style.addWidget(self.empty_label)
        self.layout_style.addWidget(self.pushButton)
        self.layout_search.addLayout(self.layout_style)
        self.layout_search.addWidget(self.showTable)

        self.search_widget.setStyleSheet('''
            QTextEdit{
                font-size:15px;
                height:30px;
            }
            QPushButton{
                height:22px;
                width:30px;
                font-size:14px;
                font-weight:700;
                font-family: "宋体", Helvetica, Arial, sans-serif;
            }            
        ''')


        self.layout_main.addWidget(self.search_widget)


     

    def get_selfsearch(self):
        try:
            self.showTable.hide()
        except:
            pass

        conn,cursor = connect_sqlite()
        sql = self.search_sql.toPlainText()
        conn,cursor = connect_sqlite()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()

            if res:
                col_name = [tuple[0] for tuple in cursor.description]
                # print(col_name)
                self.showTable=QTableWidget(len(res),len(res[0]))
                # index_list = [str(i) for i in range(len(res[0]))]
                self.showTable.setHorizontalHeaderLabels(col_name)
                for i in range(len(res)):
                    for j in range(len(res[0])):
                        self.showTable.setItem(i,j,QTableWidgetItem(str(res[i][j]))) 
                self.layout_search.addWidget(self.showTable)
  
            else:
                self.showTable=QTableWidget(4,0)
        except (Exception) as e:
            infoBox = QMessageBox(self)
            infoBox.setText(u"报错信息：%s"%e)
            infoBox.setWindowTitle("Waring")
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.exec_()
            self.selfsearch_click()





    def people_click(self):
        try:
            self.showTable.hide()
            self.search_widget.hide()
            self.name_line.hide()
            self.number_line.hide()
            self.class_line.hide()
            self.pushButton.hide()
            self.startLabel.hide()        
            self.startDatetime.hide()        
            self.endLabel.hide()        
            self.endDatetime.hide()
        except:
            pass
        try:
            self.show_background.hide()
        except:
            pass
        faces_folder_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),'candidate-faces/')
        res = [o.strip('.jpg').split('_') for o in os.listdir(faces_folder_path)]
        self.showTable=QTableWidget(len(res),4)
        self.showTable.setHorizontalHeaderLabels(['姓名','学号','班级','照片'])
        self.showTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.showTable.setIconSize(QSize(100 ,80))
        for i in range(4):   # 让列宽和图片相同
            self.showTable.setColumnWidth(i , 100)
        for i in range(len(res)):   # 让行高和图片相同
            self.showTable.setRowHeight(i , 80)

        for i in range(len(res)):
            self.showTable.setItem(i,0,QTableWidgetItem(res[i][0]))    #姓名
            self.showTable.setItem(i,1,QTableWidgetItem(res[i][1]))    #学号
            self.showTable.setItem(i,2,QTableWidgetItem(res[i][2]))    #班级
            self.peoplePhoto=QTableWidgetItem()
            self.peopleIcon =QIcon(r'%s' % 'candidate-faces/'+os.listdir(faces_folder_path)[i])
            self.peoplePhoto.setIcon(QIcon(self.peopleIcon))
            self.showTable.setItem(i,3,self.peoplePhoto)    #照片
        self.layout_main.addWidget(self.showTable)
        self.setLayout(self.layout_main)
            
    def closeEvent(self, QCloseEvent):

        reply = QMessageBox.question(self,u"Warning", "Are you sure quit ?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            sys.exit(app.exec_())
        else:
            QCloseEvent.ignore()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
