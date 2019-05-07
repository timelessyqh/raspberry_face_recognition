# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import time,json,os,requests
from manage_face import connect_sqlite,disconnect_sqlite


def facetoken_name(face_token):
    conn,cursor = connect_sqlite()
    cursor.execute("select facetoken,name,number,class from people_facetoken")
    res = cursor.fetchall()
    Dict={}
    for i in res:
        Dict[i[0]]=list(i[1:])
    disconnect_sqlite(conn,cursor)
    return Dict[face_token]
def get_facetoken(filepath,key="jiI3N4HcEAnXn-YS0BXUEkOY51dDQgQg",secret="JJu5i4996N4YKlhUYv9xF2o9y-KsX8eQ"):
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)
    fr = open(filepath, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(fr.read())
    fr.close()
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append(
        "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = resp.read()
        # if you want to load as json, you should decode first,
        # for example: json.loads(qrount.decode('utf-8'))
        face_token = json.loads(qrcont.decode('utf-8'))['faces'][0]['face_token']
        return face_token        
    except urllib.error.HTTPError as e:
        print(e.read().decode('utf-8'))

def save_facetoken():   #将人脸数据放入facepp的网站里，得到facetoken，然后将人员信息和facetoken存入sqlite
    faces_folder_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),'candidate-faces/')
    res = [o.strip('.jpg').split('_') for o in os.listdir(faces_folder_path)]
    conn,cursor = connect_sqlite()
    for i in range(len(res)):
        file_path = r'%s' % 'candidate-faces/'+os.listdir(faces_folder_path)[i]
        Name,Number,Class,Facetoken,Time = res[i][0],res[i][1],res[i][2],get_facetoken(file_path),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        cursor.execute('insert into people_facetoken (name,number,class,facetoken,time) values("%s","%s","%s","%s","%s")'%(Name,Number,Class,Facetoken,Time))

        print('OK)%s'%i)
    disconnect_sqlite(conn,cursor)

def create_faceset(key,secret):  #生成人脸识别中的faceset，之后利用face search在faceset中找到对应人
    http_url ='https://api-cn.faceplusplus.com/facepp/v3/faceset/create'
    data = {"api_key":key, "api_secret":secret}

    response = requests.post(http_url, data=data)
    faceset_token = json.loads(response.content.decode('utf-8'))['faceset_token']
    return faceset_token

def add_faceset(key,secret): #在生成的faceset中加入face_token，并返回
    http_url =' https://api-cn.faceplusplus.com/facepp/v3/faceset/addface'
    faceset_token="a27c0202a32d6ee4102563cf9fc005d2"
    conn,cursor = connect_sqlite()
    cursor.execute("select name,number,class,facetoken from people_facetoken")

    res = cursor.fetchall()
    for i in res:
        data = {"api_key":key,"api_secret":secret,"faceset_token":faceset_token,"face_tokens":i[3]}
        response = requests.post(http_url,data=data)
        print(json.loads(response.content.decode('utf-8'))['face_count']) 
    # return res 

def addimage_faceset(filepath,key="jiI3N4HcEAnXn-YS0BXUEkOY51dDQgQg",secret="JJu5i4996N4YKlhUYv9xF2o9y-KsX8eQ"): #在目前有的faceset中加入新录入人脸的facetoken
    Facetoken = get_facetoken(filepath)
    res = filepath.strip('.jpg').split('/')[1].split('_')
    Name,Number,Class,Time = res[0],res[1],res[2],time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    conn,cursor = connect_sqlite()
    cursor.execute('insert into people_facetoken (name,number,class,facetoken,time) values("%s","%s","%s","%s","%s")'%(Name,Number,Class,Facetoken,Time))
    disconnect_sqlite(conn,cursor)

    http_url =' https://api-cn.faceplusplus.com/facepp/v3/faceset/addface'
    faceset_token="a27c0202a32d6ee4102563cf9fc005d2"

    data = {"api_key":key,"api_secret":secret,"faceset_token":faceset_token,"face_tokens":Facetoken}
    response = requests.post(http_url,data=data)
    print(json.loads(response.content.decode('utf-8'))['face_count']) 

def getdetail_faceset(key,secret):  #获取faceset详细信息
    http_url ='https://api-cn.faceplusplus.com/facepp/v3/faceset/getdetail'
    faceset_token="a27c0202a32d6ee4102563cf9fc005d2"

    data = {"api_key":key,"api_secret":secret,"faceset_token":faceset_token}
    response = requests.post(http_url,data=data)
    print(json.loads(response.content.decode('utf-8'))) 

def search_faceset(key,secret,file_path):
    http_url ='https://api-cn.faceplusplus.com/facepp/v3/search'
    faceset_token="a27c0202a32d6ee4102563cf9fc005d2"
    image_file = {"image_file":open(file_path,"rb")}
    # test_token = 'c127a905d2cc29a7f2ac191cdc1bc043'
    data = {"api_key":key,"api_secret":secret,"faceset_token":faceset_token}
    response = requests.post(http_url,data=data,files=image_file)
    res = json.loads(response.content.decode('utf-8')) 
    try:
        threshold,score,face_token = res["thresholds"]["1e-3"],res["results"][0]["confidence"],res["results"][0]["face_token"]
        if score>threshold:
            # print("匹配成功，token：%s"%facetoken_name(face_token))
            return face_token
        else:
            return 0
            print("匹配失败，最像token：%s"%face_token)
    except:
        return 0
if __name__ == '__main__':
    key = "jiI3N4HcEAnXn-YS0BXUEkOY51dDQgQg"
    secret = "JJu5i4996N4YKlhUYv9xF2o9y-KsX8eQ"
    # save_facetoken()
    # create_faceset(key,secret)
    # add_faceset(key,secret)
    # getdetail_faceset(key,secret)
    # search_faceset(key,secret,'test.jpg')
    # facetoken_name(face_token)
    addimage_faceset('candidate-faces/范冰冰_201549865_1544.jpg')