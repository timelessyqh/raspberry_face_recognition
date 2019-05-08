# raspiberry_face_recognition
###基于faceplusplus+PyQt5+sqlite+树莓派的人脸识别打卡系统(Python3.6+Windows)
##Let project run
1.初始化database,在project目录下输入python3 init_database.py即创建数据库和数据表（由于sqlite在当前目录建立db文件，务必在project目录执行）
2.安装依赖包，大部分在requirements.txt中，其中或许有少部分依赖包未添加，按需下载，dlib是为了比较人脸识别速度，可以选择性安装，下载包最快速方式：在 https://www.lfd.uci.edu/~gohlke/pythonlibs/#kwant 中找到对应whl文件并在下载目录中 pip install **.whl
3.在https://console.faceplusplus.com.cn/login 网站中注册用户，找到key和secretkey并分别修改在facepp.py文件中的<Your faceplusplus key>和<Your faceplusplus secret key>，完成后在当前命令行中python3 facepp.py，该命令将创建candidate_faces中所有人脸的face_token，这是在facepp网站中的图片标识，这些face_token组成一个faceset，也就是人脸的数据集，当摄像头捕捉到人脸时，则会和faceset中的人脸比较。(可以直接向candidate_faces文件夹中添加一些图片，名称格式为  姓名_学号_班级.jpg，或者也可以python3 fast_recognition_face.py 在人脸录入模块录入)


###Good Luck!  Contact me: timelessyqh@foxmail.com