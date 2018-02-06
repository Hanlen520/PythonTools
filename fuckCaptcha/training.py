# -*- coding:utf-8 -*-
'''
时间：2018-01-27
作者：Jin
备注：机器学习识别验证码，并生成特征码
'''
import os
import cv2
import requests
import pytesseract
from os import listdir
from PIL import Image
from sklearn.svm import SVC
from sklearn.externals import joblib


# 获取验证码的地址
hurl = 'http://xxxxxx/apis'
# 当前路径
path = os.path.dirname(__file__)


def getCaptcha(username):
    '''
    调用接口请求验证码，保存到本地
    '''
    filename = username + '.png'  # 定义的验证码的名字
    url = hurl + "/file/getCaptcha1"  # 获取验证码的接口地址
    headers = {  # 接口所需参数
        'content-type': "application/json;charset=utf-8",
        'fr': "6"
        }
    hcode = 'b0a3dc8f-c0d4-475d-9c1a-eb41370bf4bf'  # 获取验证码需要的参数
    # print(hcode)
    querystring = {"w": "100", "h": "38", "code": hcode}  # 传入对于的headers数据
    response = requests.request("GET", url, headers=headers, params=querystring)  # 发送请求
    # print(response.text)
    img = response.content  # 二进制保存验证码
    with open(path+'/images/'+filename, 'wb') as f:  # 保存到上面定义的路径
        f.write(img)
        f.close()
    print(response.status_code)


def proceImg(filename):
    '''将训练集所有原始图进行灰度->二值化处理'''
    image = Image.open(path+'/images/%s' % filename)
    Lim = image.convert('L')  # 灰度处理
    Lim.save(path+'/images/%s' % filename)
    threshold = 140  # 设置二值化的阈值
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    bim = Lim.point(table, '1')  # 二值化
    bim.save(path+'/images/%s' % filename)
    print(filename)


def vertical(filename):
    ''' 进行垂直投影，返回的坐标数组，并切割验证码'''
    img = Image.open(path+'/images/%s' % filename)
    pixdata = img.load()
    w, h = img.size
    height = img.size[1]
    ver_list = []
    # 开始投影
    for x in range(w):
        black = 0
        for y in range(h):
            if pixdata[x, y] == 0:
                black += 1
        ver_list.append(black)
    # 判断边界
    l, r = 0, 0
    flag = False
    cuts = []
    for i, count in enumerate(ver_list):
        # 阈值这里为0
        if flag is False and count > 0:
            l = i
            flag = True
        if flag and count == 0:
            r = i - 1
            flag = False
            # 这里没有用水平投影，偷懒用的0和高度
            cuts.append((l - 2, 0, r + 3, height))
    # 根据返回的坐标，切割图片
    imgs = []
    for i, n in enumerate(cuts, 1):
        temp = img.crop(n)  # 调用crop函数进行切割
        imgs.append(temp)
        temp.save(path+"/images/%s_%s.png" % (filename, i))


def ocrImgAndSave(filename):
    '''将切割好的图片，调用tesseract进行识别，然后保存到识别的目录里'''
    img = Image.open(path+'/images/%s' % filename)
    recNum = pytesseract.image_to_string(img)
    print(recNum)
    if (recNum.isdigit() and len(recNum) == 1):
        recdString = filename + "_%s.png" % recNum
        paths = path + '/temp/' + recNum + "/"
        if not os.path.exists(paths):
            os.mkdir(paths)
        imgPath = paths + recdString
        img.save(imgPath)
    else:
        print("???")


def getletter(fn):
    '''提取SVM用的特征值, 提取字母特征值'''
    fnimg = cv2.imread(fn)  # 读取图像
    img = cv2.resize(fnimg, (8, 8))  # 将图像大小调整为8*8
    alltz = []
    for now_h in range(0, 8):
        xtz = []
        for now_w in range(0, 8):
            b = img[now_h, now_w, 0]
            g = img[now_h, now_w, 1]
            r = img[now_h, now_w, 2]
            btz = 255 - b
            gtz = 255 - g
            rtz = 255 - r
            if btz > 0 or gtz > 0 or rtz > 0:
                nowtz = 1
            else:
                nowtz = 0
            xtz.append(nowtz)
        alltz += xtz
    return alltz


def extractLetters(path):
    '''提取特征值'''
    x = []
    y = []
    # 遍历文件夹 获取下面的目录
    for root, sub_dirs, files in os.walk(path):
        for dirs in sub_dirs:
            # 获得每个文件夹的图片
            for fileName in os.listdir(path + '/' + dirs):
                print(fileName)
                # 打开图片
                x.append(getletter(path + '/' + dirs + '/' + fileName))
                y.append(dirs)
    return x, y


def trainSVM():
    '''进行向量机的训练SVM'''
    array = extractLetters(path + '/temp')
    # 使用向量机SVM进行机器学习
    letterSVM = SVC(kernel="linear", C=1).fit(array[0], array[1])
    # 生成训练结果
    joblib.dump(letterSVM, path + '/data/letter.pkl')


if __name__ == '__main__':
    # 第一步获取验证码到本地
    ulist = ["test01", "test02", "test03", "test04", "test05", "test06"]
    for username in ulist:
        getCaptcha(username)
    file_list = listdir(path + '/images/')
    for filename in file_list:
        proceImg(filename)
        vertical(filename)
    # # 第二步 删除获取的验证码，并对分割的图片进行分类
    # file_list = listdir(path + '/images/')
    # for filename in file_list:
    #     ocrImgAndSave(filename)
    # 第三步，学习训练识别
    # trainSVM()
