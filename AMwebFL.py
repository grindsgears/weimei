from filelock import FileLock
import pandas as pd
import os
import time
import streamlit as st
from PIL import Image, ExifTags
import uuid
import shutil
import numpy as np
import datetime
import Daifuku_free_api

def get_greeting():
    current_hour = datetime.datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "早上好"
    elif 12 <= current_hour < 18:
        return "下午好"
    elif 18 <= current_hour < 22:
        return "晚上好"
    else:
        return "夜深了，注意休息"


def delete_AIfiles(path):
    files_to_delete = ['AIreport.csv', 'resultS.jpg', 'resultF.jpg']
    
    for file_name in files_to_delete:
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")
        else:
            print(f"{file_path} does not exist")


def write_to_csv(folder_path, file_name, column_name, text):
    # 创建文件路径
    file_path = folder_path + '/' + file_name
    lock_path = folder_path + '/' + file_name + ".lock"
    
    # 使用 try/finally 来确保文件锁始终会被释放
    try:
        with FileLock(lock_path):
            # 如果文件不存在，创建一个新的 DataFrame，并保存为 csv 文件
            if not os.path.isfile(file_path):
                df = pd.DataFrame(columns=[column_name])
                df.to_csv(file_path, index=False)

            # 读取 csv 文件
            df = pd.read_csv(file_path)

            # 创建一个新的 DataFrame 来保存新的一行数据
            new_row_df = pd.DataFrame({column_name: [text]})
            
            # 使用 pd.concat 添加新的一行数据
            df = pd.concat([df, new_row_df], ignore_index=True)
            
            # 保存 DataFrame 到 csv 文件
            df.to_csv(file_path, index=False)
    finally:
        # 确保文件锁会被释放
        if os.path.exists(lock_path):
            os.remove(lock_path)

# 登录函数
def login(username, password):
    if username == 'a' and password == '1':
        st.session_state['logged_in'] = True
        st.rerun()
    else:
        st.error("用户名或密码错误")

# 登出函数
def logout():
    st.session_state['logged_in'] = False
    for key in st.session_state.keys():
        if key == 'logged_in':
            continue
        del st.session_state[key]

# 处理和保存图片
def save_image_with_correct_orientation(image_file, directory, prefix):
    image = Image.open(image_file)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    new_name = f'{prefix}-{str(uuid.uuid4().hex)}{image_file.name}'
    image.save(os.path.join(directory, new_name))
    return new_name

def delete_folder(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Deleted folder: {path}")
    else:
        print(f"Folder {path} does not exist or is not a directory")


def check_file_exist(path, filename):
    file_path = os.path.join(path, filename)
    return os.path.isfile(file_path)

def find_file(path, prefix):
    # 遍历指定路径下的所有文件
    for root, dirs, files in os.walk(path):
        # 对每个文件进行处理
        for file in files:
            # 如果文件名以指定的前缀开始，则返回文件名
            if file.startswith(prefix):
                return file
    # 如果没有找到符合条件的文件，则返回None
    return None


# 根据BMI计算BMI_score
def calculate_bmi_score(bmi):
    if 18.5 <= bmi <= 23.9:
        return 3
    elif 24.0 <= bmi <= 27.9 or bmi < 18.5:
        return 2
    elif bmi >= 28.0:
        return 1
    else:
        return None
    
# 定义一个函数，通过DeepSquat列的数值决定力量评分
def calculate_strength_score(deep_squat):
    return deep_squat

# 定义一个函数，通过ShoulderMobility和ActiveStraightLegRaise列的数值决定柔韧性评分
def calculate_flexibility_score(shoulder_mobility, active_straight_leg_raise):
    return round((shoulder_mobility + active_straight_leg_raise) / 2)

# 定义一个函数，通过Highknees列的数值决定心肺功能评分
def calculate_cardiovascular_score(highknees):
    return highknees

# 定义一个函数，通过HurdleStep和RotaryStability列的数值决定稳定性评分
def calculate_stability_score(hurdle_step, rotary_stability):
    return round((hurdle_step + rotary_stability) / 2)


# 自定义转换函数
def fitness_level_to_numeric(level):
    if level == '小白':
        return 0
    elif level == '基础':
        return 1
    elif level == '中度':
        return 2
    elif level == '资深':
        return 3
    else:
        return None
    
# 自定义转换函数
def shoulder_mobility_to_numeric(mobility):
    if mobility == '请选择':
        return None
    elif mobility == '手指轻松接触':
        return 3
    elif mobility == '手指接触，但有困难':
        return 2
    elif mobility == '手指无法接触。或出现疼痛':
        return 1
    else:
        return None

# 自定义转换函数
def active_straight_leg_raise_to_numeric(raise_level):
    if raise_level == '请选择':
        return None
    elif raise_level == '腿部抬高超过对侧大腿的中点':
        return 3
    elif raise_level == '腿部抬高刚刚到达对侧大腿的中点':
        return 2
    elif raise_level == '腿部抬高未达到对侧大腿的中点，或出现疼痛':
        return 1
    else:
        return None

# 自定义转换函数
def hurdle_step_to_numeric(step):
    if step == '请选择':
        return None
    elif step == '身体控制良好，动作流畅':
        return 3
    elif step == '动作完成，但控制不佳':
        return 2
    elif step == '无法完成动作，或出现疼痛':
        return 1
    else:
        return None

# 自定义转换函数
def deep_squat_to_numeric(squat):
    if squat == '请选择':
        return None
    elif squat == '无需协助，完成深蹲，大腿低于膝盖':
        return 3
    elif squat == '需要协助（如脚下垫物）完成深蹲':
        return 2
    elif squat == '无法完成深蹲，即使有协助，或出现疼痛':
        return 1
    else:
        return None
    
# 自定义转换函数
def rotary_stability_to_numeric(stability):
    if stability == '请选择':
        return None
    elif stability == '流畅完成动作':
        return 3
    elif stability == '完成动作，但不流畅':
        return 2
    elif stability == '无法完成动作，或出现疼痛':
        return 1
    else:
        return None

# 自定义转换函数
def high_knees_to_numeric(knees):
    if knees == '请选择':
        return None
    elif knees == '超过120次，特别是接近或超过150次':
        return 3
    elif knees == '80-120次':
        return 2
    elif knees == '30-60次，或出现疼痛':
        return 1
    else:
        return None
    
# 定义一个函数找出所有以_score为结尾的列，并计算这些列的平均值
def calculate_average_score(df):
    # 找出所有以_score为结尾的列名
    score_columns = [col for col in df.columns if col.endswith('_score')]
    
    # 计算这些列的平均值，添加到一个新的列中
    df['Average_score'] = df[score_columns].mean(axis=1)
    
    return df

def posture_score(value):
    """
    根据给定的浮点数（0-100），返回对应的分数（59-89）。
    浮点数越小，分数越高。0-3 的浮点数占据 65-85 分数范围。
    
    参数:
    value (float): 输入的浮点数，范围是 0-100。
    
    返回:
    float: 对应的分数，范围是 59-89。
    """
    if value < 0 or value > 180:
        raise ValueError("输入的浮点数必须在 0 到 180 之间。")
    
    # 定义分段插值点
    x_points = [0, 3, 100]
    y_points = [3, 2, 1]
    
    # 使用 NumPy 的插值函数进行分段线性插值
    score_value = np.interp(value, x_points, y_points)
    
    return score_value

def AIreport(initDFpath,fileName,poseFileName_F,poseFileName_S):
    initDF = pd.read_csv(initDFpath+fileName)
    poseDF_F = pd.read_csv(initDFpath+poseFileName_F)
    poseDF_S = pd.read_csv(initDFpath+poseFileName_S)
    

    # 删除 'index' 和 'name' 列
    poseDF_F = poseDF_F.drop(columns=['name'])
    poseDF_S = poseDF_S.drop(columns=['name'])

    # 横向拼接两个 DataFrame
    poseDF_combined = pd.concat([poseDF_F, poseDF_S], axis=1)

    # 将 DataFrame 转换为 NumPy 数组
    values = poseDF_combined.to_numpy()

    # 计算整体最大值、最小值和平均数
    postureGlobal_max = np.max(values)
    postureGlobal_min = np.min(values)
    postureGlobal_mean = np.mean(values)

    # 打印结果
    # print("整体最大值:", global_max)
    # print("整体最小值:", global_min)
    # print("整体平均数:", global_mean)





    #数字化
    initDF['height'] = initDF['height'].replace('cm', '', regex=True).astype(int)
    initDF['weight'] = initDF['weight'].replace('kg', '', regex=True).astype(int)
    initDF['fitnessLevel'] = initDF['fitnessLevel'].apply(fitness_level_to_numeric)
    initDF['daysOfWeek'] = initDF['daysOfWeek'].replace('天', '', regex=True).astype(int)
    initDF['shoulderMobility'] = initDF['shoulderMobility'].apply(shoulder_mobility_to_numeric)
    initDF['activeStraightLegRaise'] = initDF['activeStraightLegRaise'].apply(active_straight_leg_raise_to_numeric)
    initDF['hurdleStep'] = initDF['hurdleStep'].apply(hurdle_step_to_numeric)
    initDF['deepSquat'] = initDF['deepSquat'].apply(deep_squat_to_numeric)
    initDF['rotaryStability'] = initDF['rotaryStability'].apply(rotary_stability_to_numeric)
    initDF['highKnees'] = initDF['highKnees'].apply(high_knees_to_numeric)
    initDF = pd.concat([initDF, poseDF_combined], axis=1)
    initDF['posture_max'] = postureGlobal_max#注意这里改变了整列的数据！！！！！
    initDF['posture_min'] = postureGlobal_min#注意这里改变了整列的数据！！！！！
    initDF['posture_mean'] = postureGlobal_mean#注意这里改变了整列的数据！！！！！

    # 将 height 从厘米转换为米

    initDF['height_m'] = initDF['height'] / 100

    # 计算BMI

    initDF['BMI'] = initDF['weight'] / (initDF['height_m'] ** 2)

    # 应用BMI评分函数
    initDF['BMI_score'] = initDF['BMI'].apply(calculate_bmi_score)

    # 应用力量评分函数
    initDF['Strength_score'] = initDF['deepSquat'].apply(calculate_strength_score)

    # 应用柔韧性评分函数
    initDF['Flexibility_score'] = initDF.apply(
        lambda row: calculate_flexibility_score(row['shoulderMobility'], row['activeStraightLegRaise']),
        axis=1
    )

    # 应用心肺功能评分函数
    initDF['Cardiovascular_score'] = initDF['highKnees'].apply(calculate_cardiovascular_score)

    # 应用稳定性评分函数
    initDF['Stability_score'] = initDF.apply(
        lambda row: calculate_stability_score(row['hurdleStep'], row['rotaryStability']),
        axis=1
    )

    initDF['posture_score'] = initDF['posture_mean'].apply(posture_score)

    # 应用函数计算平均得分
    initDF = calculate_average_score(initDF)

    try:
        AI_fitness_summary,AI_posture_summary,AI_overall_evaluation,AI_recommendation = Daifuku_free_api.talk(initDF)
        initDF.loc[len(initDF)-1,'AI_fitness_summary'] = AI_fitness_summary
        initDF.loc[len(initDF)-1,'AI_posture_summary'] = AI_posture_summary
        initDF.loc[len(initDF)-1,'AI_overall_evaluation'] = AI_overall_evaluation
        initDF.loc[len(initDF)-1,'AI_recommendation'] = AI_recommendation
    except BaseException as e:
        print("An error occurred:",e)
        


    initDF.to_csv(initDFpath+'AIreport.csv',index=False) 
    # initDF.to_csv('initDF.csv')

    # bulkSheet.loc[len(bulkSheet),'日期'] = initDF.loc[0,'datetime']
    # bulkSheet.loc[len(bulkSheet)-1,'姓名'] = initDF.loc[0,'name']
    # bulkSheet.loc[len(bulkSheet)-1,'p3综合数据打败（0%-80%）'] = '代办'
    # bulkSheet.loc[len(bulkSheet)-1,'p4体态打分（1-3）'] = '代办'
    # bulkSheet.loc[len(bulkSheet)-1,'p4综合健康体测评分（5-9）'] = '代办'
    print(initDF.columns)