import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
import numpy as np
from mediapipe.python.solutions.pose import PoseLandmark
from mediapipe.python.solutions.drawing_utils import DrawingSpec
from PIL import ImageFont, ImageDraw, Image
import math
import os
import fnmatch
import random
import string
import pandas as pd



def check_duplicate_file(filepath):
    # 检查文件是否存在
    if os.path.isfile(filepath):
        # 如果文件存在，生成一个随机字符串
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        base, ext = os.path.splitext(filepath)
        new_filepath = f"{base}_{random_str}{ext}"
        # 递归调用函数，直到生成的文件名不重复
        return check_duplicate_file(new_filepath)
    else:
        return filepath



def find_files(directory, extension):
    result = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, '*.' + extension):
                result.append(os.path.join(root, file))
    return result



global line_width
global font_scale



# 初始化MediaPipe Pose组件。
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils
def get_bbox_textOnImage(image,txt,font,fontSize):#获取字符串bbox
    # loc = (textMainX,loc[1])
    # 将OpenCV图像转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 初始化PIL的绘图对象
    draw = ImageDraw.Draw(image_pil)
    # 指定字体和大小
    font = ImageFont.truetype(font, fontSize)

    # 计算文字的边界框
    bbox = font.getbbox(txt)
    
    
    return bbox
def get_fontLen_textOnImage(image,txt,font,fontSize):#获取字符串长度
    # loc = (textMainX,loc[1])
    # 将OpenCV图像转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 初始化PIL的绘图对象
    draw = ImageDraw.Draw(image_pil)
    # 指定字体和大小
    font = ImageFont.truetype(font, fontSize)

    # 计算文字的边界框
    bbox_len = font.getlength(txt)
    
    return bbox_len
def crop_square(a, b, scale,image, output_path):
    '''
    根据传入的a点与b点（肩膀的位置）裁剪出一个正方形图片
    a, b: 两个点的坐标，形式为(x, y)
    image: 原图像
    output_path: 输出图片的路径
    '''

    # 计算a点和b点的中点
    mid_point = np.array([0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1])])
    
    # 计算正方形的左上角和右下角
    top_left = np.array([mid_point[0] - scale, mid_point[1] - scale]).astype(int)
    bottom_right = np.array([mid_point[0] + scale, mid_point[1] + scale]).astype(int)

    # 确保所有坐标都在图像范围内
    top_left = np.clip(top_left, 0, np.array([image.shape[1], image.shape[0]]) - 1)
    bottom_right = np.clip(bottom_right, 0, np.array([image.shape[1], image.shape[0]]) - 1)

    # 截取正方形区域
    cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    cropped_image = textOnImage(cropped_image,' '+output_path+' ',(cropped_image.shape[1]-get_fontLen_textOnImage(cropped_image,' '+output_path+' ','/Library/Fonts/Arial Unicode.ttf',font_scale)-font_scale/6.5,cropped_image.shape[0]-get_bbox_textOnImage(cropped_image,' '+output_path+' ','/Library/Fonts/Arial Unicode.ttf',font_scale)[3]-font_scale/2.5),'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    
    # 保存图片
    cv2.imwrite(output_path, cropped_image)

def draw_extended_line(image, A, B,color,width):
    # 计算线的斜率和截距
    slope = (B[1] - A[1]) / (B[0] - A[0])
    intercept = A[1] - slope * A[0]

    # 计算与图像边缘相交的点的坐标
    x_left = 0
    y_left = intercept

    x_right = image.shape[1]
    y_right = slope * x_right + intercept

    # 将坐标转换为整数
    pt1 = (int(x_left), int(y_left))
    pt2 = (int(x_right), int(y_right))

    # 使用cv2.line()函数绘制线
    cv2.line(image, pt1, pt2, color, width)

    return image
def ellipseOnImage(image,loc,radius,color):#在图上画圆
    # 将OpenCV图像转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 初始化PIL的绘图对象
    draw = ImageDraw.Draw(image_pil)
    #画圆
    draw.ellipse([loc[0]-radius, loc[1]-radius, loc[0]+radius, loc[1]+radius], fill=color)
    # 将PIL图像转回OpenCV图像
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image
def ABporintDistance(point1, point2):#欧氏距离公式
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
def math_midpoint(x1, y1, x2, y2):
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))
def getMidPoint(a,b):#找到中点
    point1 = math_midpoint(a[0],a[1],b[0],b[1])
    return point1
def calculate_angle(a, b, c):# 计算两点之间的角度。
    a = np.array(a)  # 第一个点
    b = np.array(b)  # 第二个点（顶点）
    c = np.array(c)  # 第三个点

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle
    if angle == 180.0:
        angle = 0

    return angle
def which_higher_3d(a,b):#找出高点3d坐标系
    if a.y < b.y:
        return a
    else:
        return b
def which_lower_3d(a,b):#找出低点3d坐标系
    if a.y > b.y:
        return a
    else:
        return b
def which_higher(a,b):#找出高点cv2坐标系
    if a[1] < b[1]:
        return a
    else:
        return b
def which_lower(a,b):#找出低点cv2坐标系

    if a[1] > b[1]:
        return a
    else:
        return b
def checkSideFacing(landmarks):#检查侧身时的朝向
    if landmarks[23].z > landmarks[24].z:
        print('人物面向右边',landmarks[23].z,landmarks[24].z)
        return False
    elif landmarks[23].z < landmarks[24].z:
        print('人物面向左边',landmarks[23].z,landmarks[24].z)            
        return True
    else:
        print('人物朝向检测失败',landmarks[23].z,landmarks[24].z)
        return '人物朝向检测失败'
def getPoint(cv2_landmarks):#获取点(x,x)
    return (cv2_landmarks[0],cv2_landmarks[1])
def textOnImage(image,txt,loc,font,fontSize,color):#在图片上写字
    # loc = (textMainX,loc[1])
    # 将OpenCV图像转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 初始化PIL的绘图对象
    draw = ImageDraw.Draw(image_pil)
    # 指定字体和大小
    font = ImageFont.truetype(font, fontSize)

    # 计算文字的边界框
    bbox = font.getbbox(txt)

    # radius = line_width*10
    # p1 = loc[0]+bbox_len,loc[1]
    # draw.ellipse([p1[0]-radius, p1[1]-radius, p1[0]+radius, p1[1]+radius], fill=(255,0,0))
    
    # 绘制填充的矩形
    draw.rectangle([loc, (loc[0]+bbox[2], loc[1]+bbox[3]+fontSize/3.5)], fill=(255,255,255,0),outline=(130,130,130),width=int(line_width/1.5))

    # 在图像上添加文字
    draw.text((loc), txt, font=font, fill=color)
    # 将PIL图像转回OpenCV图像
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image
def textOnImage_center(image,txt,loc,font,fontSize,color):#居中在图片上写字
    # loc = (textMainX,loc[1])
    # 将OpenCV图像转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 初始化PIL的绘图对象
    draw = ImageDraw.Draw(image_pil)
    # 指定字体和大小
    font = ImageFont.truetype(font, fontSize)

    # 计算文字的边界框
    bbox = font.getbbox(txt)
    bbox_len = font.getlength(txt)
    
    
    midPoint = (loc[0]+bbox_len + loc[0])/2,loc[1]
    loc = loc[0] - bbox_len/2,loc[1]-bbox[3]/2-fontSize/3.5/2
    
    # radius = line_width*10
    # draw.ellipse([midPoint[0]-radius, midPoint[1]-radius, midPoint[0]+radius, midPoint[1]+radius], fill=(255,0,0))
    
    # 绘制填充的矩形
    draw.rectangle([loc, (loc[0]+bbox[2], loc[1]+bbox[3]+fontSize/3.5)], fill=(255,255,255,0),outline=(130,130,130),width=int(line_width/1.5))

    # 在图像上添加文字
    draw.text((loc), txt, font=font, fill=color)
    # 将PIL图像转回OpenCV图像
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image
def aiCheck_hips(a,b,image,poseDF):#高低胯
    '''
    2.高低胯：
    a.24 、 23 的y点不同
    '''
    cv2.line(image, a, b, (45, 157, 212), line_width)
    higherPoint = which_higher(a,b)
    lowerPoint = which_lower(a,b)
    image = ellipseOnImage(image,a,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,a,line_width*3,(255, 255, 255, 255))
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    

    if higherPoint[0] < lowerPoint[0]:#左边高
        print('左边高')
        a1 = (image.shape[0],higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        print('高低胯角度为：',calculate_angle(a1, a2, a3))
        loc = textMainX,higherPoint[1]
        cv2.line(image, loc, higherPoint, (255, 255, 255), line_width)
        image = textOnImage_center(image,"高低胯 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    else:#右边高
        print('右边高')
        a1 = (0,higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        print('高低胯角度为：',calculate_angle(a1, a2, a3))
        loc = textMainX,higherPoint[1]
        cv2.line(image, loc, higherPoint, (255, 255, 255), line_width)
        image = textOnImage_center(image,"高低胯 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_hips'] = round(calculate_angle(a1, a2, a3),2)
    return image
def aiCheck_shoulders(a,b,image,poseDF):#高低肩
    '''
    1.高低肩：
    a.12 、 11 的y点不同
    '''
    cv2.line(image, a, b, (45, 157, 212), line_width)
    higherPoint = which_higher(a,b)
    lowerPoint = which_lower(a,b)
    image = ellipseOnImage(image,a,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,a,line_width*3,(255, 255, 255, 255))
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    
    
    if higherPoint[0] < lowerPoint[0]:#左边高
        print('左边高')
        a1 = (image.shape[0],higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        print('高低肩角度为：',calculate_angle(a1, a2, a3))
        loc = textMainX,higherPoint[1]
        cv2.line(image, loc, higherPoint, (255, 255, 255), line_width)
        image = textOnImage_center(image,"高低肩 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    else:#右边高
        print('右边高')
        a1 = (0,higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        print('高低肩角度为：',calculate_angle(a1, a2, a3))
        loc = textMainX,higherPoint[1]
        cv2.line(image, loc, lowerPoint, (255, 255, 255), line_width)
        image = textOnImage_center(image,"高低肩 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    poseDF.loc[len(poseDF)-1,'aiCheck_shoulders'] = round(calculate_angle(a1, a2, a3),2)
    return image
def aiCheck_knee(a,b,image,poseDF):#长短腿
    '''
    4.长短腿:Knee Alignment
    a.26 、 25 的y点不同
    '''
    cv2.line(image, a, b, (45, 157, 212), line_width)
    higherPoint = which_higher(a,b)
    lowerPoint = which_lower(a,b)

    loc = textMainX,a[1]+font_scale*5
    print(loc)
    if higherPoint[0] < lowerPoint[0]:#左边高
        print('长短腿左边高')
        a1 = (image.shape[0],higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        # cv2.line(image, a1, a2, (255, 0, 0), line_width)
        # cv2.line(image, a2, a3, (255, 0, 0), line_width)
        print('长短腿角度为：',calculate_angle(a1, a2, a3))
        image = textOnImage_center(image,"长短腿 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    else:#右边高
        print('长短腿右边高')
        a1 = (0,higherPoint[1])
        a2 = (int(higherPoint[0]),int(higherPoint[1]))
        a3 = (int(lowerPoint[0]),int(lowerPoint[1]))
        # cv2.line(image, a1, a2, (255, 0, 0), line_width)
        # cv2.line(image, a2, a3, (255, 0, 0), line_width)
        print('长短腿角度为：',calculate_angle(a1, a2, a3))
        image = textOnImage_center(image,"长短腿 "+str(round(calculate_angle(a1, a2, a3),2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    poseDF.loc[len(poseDF)-1,'aiCheck_knee'] = round(calculate_angle(a1, a2, a3),2)
    return image
def aiCheck_Body_Alignment(a,b,c,image,poseDF):#身体侧倾

    # cv2.line(image, a, b, (45, 157, 212), line_width)
    # cv2.line(image, b, c, (45, 157, 212), line_width)
    v1 = calculate_angle(a, b, c)
    loc = a[0],a[1]-font_scale*5
    # image = draw_extended_line(image,a,b,(45, 157, 212),line_width)
    if v1 < 180:
        v2 = 180-v1
        print('身体向右侧倾：',v2)
        image = textOnImage(image,"身体向右侧倾 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    if v1 > 180:
        v2 = v1-180
        print('身体向左侧倾：',v2)
        image = textOnImage(image,"身体向左侧倾 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_Body_Alignment'] = round(v2,2)
    return image
def aiCheck_Knee_Angle_left(a,b,c,image,poseDF):#膝盖角度（左）

    cv2.line(image, a, b, (45, 157, 212), line_width)
    cv2.line(image, b, c, (45, 157, 212), line_width)
    v1 = calculate_angle(a, b, c)

    loc = int((b[0] + image.shape[1])/2),b[1]
    cv2.line(image, b, loc, (255, 255, 255), line_width)
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    image = ellipseOnImage(image,c,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,c,line_width*3,(255, 255, 255, 255))

    if v1 < 180:
        v2 = 180-v1
        print('左侧膝盖外翻：',v2)
        image = textOnImage_center(image,"左侧膝盖外翻 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    if v1 > 180:
        v2 = v1-180
        print('左侧膝盖内翻：',v2)
        image = textOnImage_center(image,"左侧膝盖内翻 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_Knee_Angle_left'] = round(v2,2)
    return image
def aiCheck_Knee_Angle_right(a,b,c,image,poseDF):#膝盖角度（右）

    cv2.line(image, a, b, (45, 157, 212), line_width)
    cv2.line(image, b, c, (45, 157, 212), line_width)
    v1 = calculate_angle(a, b, c)
    
    loc = int((b[0] + 0)/2),b[1]
    cv2.line(image, b, loc, (255, 255, 255), line_width)
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    image = ellipseOnImage(image,c,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,c,line_width*3,(255, 255, 255, 255))

    if v1 < 180:
        v2 = 180-v1
        print('右侧膝盖外翻：',v2)
        
        image = textOnImage_center(image,"右侧膝盖外翻 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    if v1 > 180:
        v2 = v1-180
        print('右侧膝盖内翻：',v2)
        image = textOnImage_center(image,"右侧膝盖内翻 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_Knee_Angle_right'] = round(v2,2)
    return image
def aiCheck_Head_pos(a,b,c,image,poseDF):#头部前倾

    cv2.line(image, a, b, (45, 157, 212), line_width)
    cv2.line(image, b, c, (45, 157, 212), line_width)

    v1 = calculate_angle(a, b, c)
    v2 = 166-v1
    print('头部位置：',v1)
    loc = textMainX,a[1]
    cv2.line(image, a, loc, (255, 255, 255), line_width)
    image = textOnImage_center(image,"头部前倾 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    image = ellipseOnImage(image,a,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,a,line_width*3,(255, 255, 255, 255))


    # image = textOnImage(image,"头部前倾 "+str(round(v2,2))+'°',a,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    # if v1 < 175:
        

    #     image = textOnImage(image,"头部前倾 "+str(round(v2,2))+'°',c,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_Head_pos'] = round(v2,2)
    return image
def aiCheck_Kyphosis(a,b,image,poseDF):#含胸弓背

    # cv2.line(image, a, b, (45, 157, 212), line_width)
    v1 = a[1]-b[1]*1.01
    v2 = v1/image.shape[1]
    # if a[1] < b[1]*1.01:
    #     print('含胸弓背')
    loc = textMainX,b[1]
    cv2.line(image, b, loc, (255, 255, 255), line_width)
    image = textOnImage_center(image,"含胸弓背 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    # image = textOnImage(image,"含胸弓背 "+str(round(v2,2))+'°',b,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    # if v1 < 175:
        

    #     image = textOnImage(image,"头部前倾 "+str(round(v2,2))+'°',c,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_Kyphosis'] = round(v2,2)
    return image
def aiCheck_pelvic_tilt(a,b,c,image,poseDF):#骨盆前倾

    cv2.line(image, a, b, (45, 157, 212), line_width)
    cv2.line(image, b, c, (45, 157, 212), line_width)

    v1 = calculate_angle(a, b, c)
    
    print('骨盆角度：',v1)
    
    loc = textMainX,b[1]
    cv2.line(image, b, loc, (255, 255, 255), line_width)

    if v1 < 178:
        v2 = 178-v1
        image = textOnImage_center(image,"骨盆前倾 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
        image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
        image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
        # image = textOnImage(image,"骨盆前倾 "+str(round(v2,2))+'°',b,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    if v1 > 178:
        v2 = v1-178
        image = textOnImage_center(image,"骨盆后倾 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
        image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
        image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
        # image = textOnImage(image,"骨盆后倾 "+str(round(v2,2))+'°',b,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    # if v1 < 175:
        

    #     image = textOnImage(image,"头部前倾 "+str(round(v2,2))+'°',c,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    
    poseDF.loc[len(poseDF)-1,'aiCheck_pelvic_tilt'] = round(v2,2)
    return image
def aiCheck_Hyperextended_knee(a,b,c,image,poseDF):#膝盖超伸

    cv2.line(image, a, b, (45, 157, 212), line_width)
    cv2.line(image, b, c, (45, 157, 212), line_width)

    v1 = calculate_angle(a, b, c)
    
    print('膝盖超伸角度：',v1)
    
    v2 = 180-v1
    
    loc = loc = textMainX,b[1]
    cv2.line(image, b, loc, (255, 255, 255), line_width)
    image = textOnImage_center(image,"膝盖超伸 "+str(round(v2,2))+'°',loc,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
    image = ellipseOnImage(image,b,line_width*4.5,(62, 160, 241, 0))
    image = ellipseOnImage(image,b,line_width*3,(255, 255, 255, 255))
    # image = textOnImage(image,"膝盖超伸 "+str(round(v2,2))+'°',b,'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))

    
    poseDF.loc[len(poseDF)-1,'aiCheck_Hyperextended_knee'] = round(v2,2)
    return image





def main(image_path,direction,ouput_path):
    """
    image_path = 文件的路径
    direction = true/正面，false/侧面
    ouput_path = 导出文件的路径
    """
    # 从文件中读取图片。
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    #通用线宽
    global line_width
    line_width = max(int(image.shape[1] / 380), 1)
    #通用字大小
    global font_scale
    font_scale = max(int(image.shape[0] / 40), 1)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        
        #把归一化的数值转换成cv2操作坐标
        # NOSE = 0
        # LEFT_EYE_INNER = 1
        # LEFT_EYE = 2
        # LEFT_EYE_OUTER = 3
        # RIGHT_EYE_INNER = 4
        # RIGHT_EYE = 5
        # RIGHT_EYE_OUTER = 6
        # LEFT_EAR = 7
        # RIGHT_EAR = 8
        # MOUTH_LEFT = 9
        # MOUTH_RIGHT = 10
        # LEFT_SHOULDER = 11
        # RIGHT_SHOULDER = 12
        # LEFT_ELBOW = 13
        # RIGHT_ELBOW = 14
        # LEFT_WRIST = 15
        # RIGHT_WRIST = 16
        # LEFT_PINKY = 17
        # RIGHT_PINKY = 18
        # LEFT_INDEX = 19
        # RIGHT_INDEX = 20
        # LEFT_THUMB = 21
        # RIGHT_THUMB = 22
        # LEFT_HIP = 23
        # RIGHT_HIP = 24
        # LEFT_KNEE = 25
        # RIGHT_KNEE = 26
        # LEFT_ANKLE = 27
        # RIGHT_ANKLE = 28
        # LEFT_HEEL = 29
        # RIGHT_HEEL = 30
        # LEFT_FOOT_INDEX = 31
        # RIGHT_FOOT_INDEX = 32
        cv2_landmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
                cv2_landmarks.append((x, y))

        #标记数据点
        # for i, point in enumerate(cv2_landmarks):
        #     cv2.putText(image, str(i), (point[0] + 10, point[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        



        #侧身检查朝向
        # checkSideFacing(landmarks)



        global body_lenth
        body_lenth = cv2_landmarks[28][1] - cv2_landmarks[12][1]
        global body_width
        body_width = cv2_landmarks[11][0] - cv2_landmarks[12][0]


        
        # 绘制关键点和骨架用于可视化。
        # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        findXmin = 9999999999
        findXmax = 0
        findYmin = 9999999999
        findYmax = 0
        for i in cv2_landmarks:
            if i[0] < findXmin:findXmin = i[0]
            if i[0] > findXmax:findXmax = i[0]
            if i[1] < findYmin:findYmin = i[1]
            if i[1] > findYmax:findYmax = i[1]
        
        #人物盒子
        upLeft = (findXmin,findYmin)
        upRight = (findXmax,findYmin)
        downLeft = (findXmin,findYmax)
        downRight = (findXmax,findYmax)
        # cv2.line(image, upLeft, upRight, (0, 0, 0), line_width)
        # cv2.line(image, upRight, downRight, (0, 0, 0), line_width)
        # cv2.line(image, downRight, downLeft, (0, 0, 0), line_width)
        # cv2.line(image, downLeft, upLeft, (0, 0, 0), line_width)

        #中间线
        upMid = (int((upRight[0]+upLeft[0])/2),upLeft[1])
        downMid = (int((downRight[0]+downLeft[0])/2),downLeft[1])
        # cv2.line(image, upMid, downMid, (0, 0, 0), line_width)
        


        #人物右侧盒子
        box1UpLeft = upRight
        box1UpRight = image.shape[1],box1UpLeft[1]
        box1DownLeft = downRight
        box1DownRight = image.shape[1],box1DownLeft[1]
        global box1textMainX
        box1textMainX = int((box1UpLeft[0]+box1UpRight[0])/2)

        # cv2.line(image, box1UpLeft, box1UpRight, (0, 0, 0), line_width)
        # cv2.line(image, box1UpRight, box1DownRight, (0, 0, 0), line_width)
        # cv2.line(image, box1DownRight, box1DownLeft, (0, 0, 0), line_width)
        # cv2.line(image, box1DownLeft, box1UpLeft, (0, 0, 0), line_width)



        #人物左侧盒子
        box2UpLeft = (0,upRight[1])
        box2UpRight = upLeft
        box2DownLeft = (0,downLeft[1])
        box2DownRight = downLeft
        global box2textMainX
        box2textMainX = int((box2UpLeft[0]+box2UpRight[0])/2)
        print('左侧盒子中点',box2textMainX)
        # cv2.line(image, box2UpLeft, box2UpRight, (0, 0, 0), line_width)
        # cv2.line(image, box2UpRight, box2DownRight, (0, 0, 0), line_width)
        # cv2.line(image, box2DownRight, box2DownLeft, (0, 0, 0), line_width)
        # cv2.line(image, box2DownLeft, box2UpLeft, (0, 0, 0), line_width)

     

        #确定主要盒子（背后）
        if checkSideFacing(landmarks):#人物朝左，右边盒子
            mainBoxUpLeft = box1UpLeft
            mainBoxUpRight = box1UpRight
            mainBoxDownLeft = box1DownLeft
            mainBoxDownRight = box1DownRight
        elif not checkSideFacing(landmarks):#人物朝右，左边盒子
            mainBoxUpLeft = box2UpLeft
            mainBoxUpRight = box2UpRight
            mainBoxDownLeft = box2DownLeft
            mainBoxDownRight = box2DownRight
        global textMainX
        textMainX = int((mainBoxUpLeft[0]+mainBoxUpRight[0])/2)
        print('textMainX',textMainX)
        # cv2.line(image, mainBoxUpLeft, mainBoxUpRight, (0, 0, 0), line_width)
        # cv2.line(image, mainBoxUpRight, mainBoxDownRight, (0, 0, 0), line_width)
        # cv2.line(image, mainBoxDownRight, mainBoxDownLeft, (0, 0, 0), line_width)
        # cv2.line(image, mainBoxDownLeft, mainBoxUpLeft, (0, 0, 0), line_width)

        
        poseDF = pd.DataFrame()
        poseDF.loc[len(poseDF),'name'] = ouput_path



        if (direction):
            print('正面')
            image = textOnImage(image," AM posture™检测 正面视图 ",(0+font_scale/2,+font_scale/2),'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
            image = aiCheck_hips(cv2_landmarks[23],cv2_landmarks[24],image,poseDF)
            image = aiCheck_shoulders(cv2_landmarks[12],cv2_landmarks[11],image,poseDF)
            image = aiCheck_knee(cv2_landmarks[26],cv2_landmarks[25],image,poseDF)
            image = aiCheck_Body_Alignment(cv2_landmarks[0],getMidPoint(cv2_landmarks[24],cv2_landmarks[23]),getMidPoint(cv2_landmarks[30],cv2_landmarks[29]),image,poseDF)
            image = aiCheck_Knee_Angle_right(cv2_landmarks[24],cv2_landmarks[26],cv2_landmarks[28],image,poseDF)
            image = aiCheck_Knee_Angle_left(cv2_landmarks[23],cv2_landmarks[25],cv2_landmarks[27],image,poseDF)
            #截图
            crop_square(cv2_landmarks[12],cv2_landmarks[11],body_width/1.5,image,ouput_path+'肩部.jpg')
            crop_square(cv2_landmarks[24],cv2_landmarks[23],body_width/1.5,image,ouput_path+'胯部.jpg')
            crop_square(cv2_landmarks[26],cv2_landmarks[25],body_width/1.5,image,ouput_path+'膝盖.jpg')
            crop_square(cv2_landmarks[28],cv2_landmarks[27],body_width/1.5,image,ouput_path+'足部.jpg')
            filepath = ouput_path+'resultF.jpg'
            # filepath = check_duplicate_file(filepath)

            cv2.imwrite(filepath, image)
            poseDF.to_csv(ouput_path+'poseDF_F.csv',index=False)
            
            

        else:
            
            print('侧面')
            image = textOnImage(image," AM posture™检测 侧面视图 ",(0+font_scale/2,0+font_scale/2),'/Library/Fonts/Arial Unicode.ttf',font_scale,(0, 0, 0, 0))
            if checkSideFacing(landmarks):#朝左
                image = aiCheck_Head_pos(cv2_landmarks[7],cv2_landmarks[11],cv2_landmarks[23],image,poseDF)

                image = aiCheck_Kyphosis(cv2_landmarks[7],cv2_landmarks[11],image,poseDF)

                image = aiCheck_pelvic_tilt(cv2_landmarks[11],cv2_landmarks[23],cv2_landmarks[27],image,poseDF)

                image = aiCheck_Hyperextended_knee(cv2_landmarks[23],cv2_landmarks[25],cv2_landmarks[27],image,poseDF)

            elif not checkSideFacing(landmarks):#朝右
                image = aiCheck_Head_pos(cv2_landmarks[8],cv2_landmarks[12],cv2_landmarks[24],image,poseDF)

                image = aiCheck_Kyphosis(cv2_landmarks[8],cv2_landmarks[12],image,poseDF)

                image = aiCheck_pelvic_tilt(cv2_landmarks[12],cv2_landmarks[24],cv2_landmarks[28],image,poseDF)

                image = aiCheck_Hyperextended_knee(cv2_landmarks[24],cv2_landmarks[26],cv2_landmarks[28],image,poseDF)

            else:
                print(checkSideFacing(landmarks))
            #截图
            crop_square(cv2_landmarks[24],cv2_landmarks[23],body_lenth/6,image,ouput_path+'骨盆.jpg')
            crop_square(getMidPoint(cv2_landmarks[7],cv2_landmarks[8]),getMidPoint(cv2_landmarks[11],cv2_landmarks[12]),body_lenth/6,image,ouput_path+'脊椎.jpg')
            filepath = ouput_path+'resultS.jpg'
            # filepath = check_duplicate_file(filepath)

            cv2.imwrite(filepath, image)
            poseDF.to_csv(ouput_path+'poseDF_S.csv',index=False)
        
        

        return filepath


       


        
        
        
        
        



        

        # cv2.imshow("AM posture™️ Detection", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        print("未检测到人体姿态")

