在我们进一步讨论之前，我们先来讨论一下解决这个问题需要的工具:  

import pytesseract
from PIL import Image
import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.externals import joblib

http://blog.csdn.net/lee20093905/article/details/78201199#%E4%BA%8C%E5%80%BC%E5%8C%96%E5%8E%9F%E5%A7%8B%E5%9B%BE
https://github.com/zjy090/verifyCode

实现思路
1、获取验证码
2、对验证码进行灰度处理。
3、对验证码进行二值化处理。
4、切割验证码。
5、对切割后的数字进行分类。
6、机器学习，提取特征码。
7、保存特征码，以后就可以用了。
8、读取验证码的二进制、和特征码进行对比。
9、得到结果。
