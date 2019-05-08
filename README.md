# raspiberry_face_recognition  

### 基于Faceplusplus+PyQt5+Sqlite+树莓派的人脸识别打卡系统(Python3.6+Windows)

## Let project run
-   1.**初始化database**   
      
&emsp; 在project目录下输入    
```
    python3 init_database.py
``` 

&emsp; 即创建数据库和数据表（由于sqlite在当前目录建立db文件，务必在project目录执行）    

-   2.**安装依赖包**  
   
&emsp; 大部分在requirements.txt中，其中或许有少部分依赖包未添加，按需下载 
   
&emsp; dlib是为了比较人脸识别速度，可以选择性安装   
   
&emsp; 下载包最快速方式：在 [Python包下载](https://www.lfd.uci.edu/~gohlke/pythonlibs/#kwant) 中找到对应whl文件并在下载目录中 
`pip install **.whl`   

-   3.**初始化Facepp**    

&emsp; 在[facepp](https://console.faceplusplus.com.cn/login) 中注册用户，找到key和secretkey并替换facepp.py和fast_face_recogntion.py文件中的<Your faceplusplus key\>和<Your faceplusplus secret key\> &emsp;  此时需要一些人脸图片作为数据集，可以直接向candidate_faces文件夹中添加一些图片(格式为 姓名_学号_班级.jpg)，也可以输入 
```
    python3 fast_recognition_face.py
```        
&emsp;  在人脸录入模块录入人脸数据，完成后在当前命令行中
```
    python3 facepp.py
```   
&emsp;  该命令将创建candidate_faces中所有人脸的face_token(图片标识)，这些face_token组成一个faceset，也就是人脸的数据集，当摄像头捕捉到人脸时，则会和faceset中的人脸比较。   
     
-   4.**Run**    

&emsp;  fast_face_recogniton为人脸识别的前台和考勤系统，manage_face为用户后台和数据查看
```
    python3 fast_face_recognition.py
    python3 manage_face.py
```   
     
-   5.**运行结果截图**
pic1.png pic2.png



## Some Explanation
-   1.**调整窗口大小和位置**   
      
&emsp; 该版本适用于PC版，而最终要呈现在树莓派中，则需在fast_face_recognition和mange_face中调节窗口大小和位置，其中setFixedSize函数调节控件尺寸，setGeometry函数调节窗口位置    
    
-   2.**人脸识别速率和打卡**  
   
&emsp;  方法一开始采用dlib进行人脸识别，出现了一些问题，第一是当录入新的人脸时需要关闭系统重新训练数据；第二是模型识别占用了大量cpu，树莓派的算力有限。因此为了节省cpu开销，方法改为了网络开销，使用facepp的人脸识别服务，但即便如此，在树莓派3b+实际运行中依然出现卡顿掉帧情况。
    
&emsp; 另外由于掉帧的原因，图像可能卡着不动而人脸识别会每一帧都识别，造成一次打卡，数次写入的现象，通过设置face_flag来实现在不改变人的情况下同一人脸只写入一次数据
        
-   3.**树莓派配置**    

&emsp;  系统采用[官网](https://www.raspberrypi.org/downloads/) 的Raspbian，格式卡使用SD Format，写入使用Win32DiskImager，Python使用默认的3.5(千万不要自己下3.6，大坑)，LCD屏切换[网址](https://trickiknow.com/raspberry-pi-3-complete-tutorial-2018-lets-get-started/) ，三分钟换屏，摄像头插入蓝色边靠网口，注意配置ssh，防止白屏刷机 





### Good Luck! 

### Contact me: timelessyqh@foxmail.com
