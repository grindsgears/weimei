import streamlit as st
import os
# from pages import newClient
from streamlit_option_menu import option_menu
import datetime
import pandas as pd
import uuid
import time
import random
import AMwebFL_poseChecker
import AMwebFL


# 使用 HTML 和 CSS 实现右对齐
right_aligned_text = """
<div style="text-align: right;">
    AM Inc.
</div>
"""



# 初始化会话状态
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'navigate_to' not in st.session_state:
    st.session_state['navigate_to'] = "主页"
if 'selected_folder' not in st.session_state:
    st.session_state['selected_folder'] = ""
if 'choice' not in st.session_state:
    st.session_state['choice'] = 1#只有等于0的时候才会操作

if 'redirect' not in st.session_state:
    st.session_state['redirect'] = False
    
if st.session_state['redirect']:
    st.session_state['redirect'] = False
    
    if st.session_state['navigate_to'] == '主页':
        manual_select = 0
    if st.session_state['navigate_to'] == '会员列表':
        manual_select = 1
    if st.session_state['navigate_to'] == '会员详情':
        manual_select = 2
    if st.session_state['navigate_to'] == '继续录入':
        manual_select = 3  
else:

    manual_select = None

# #返回功能集合
# if 'return_current' not in st.session_state:
#     st.session_state['return_current'] = ""
# if 'return_last' not in st.session_state:
#     st.session_state['return_last'] = ""
# if st.session_state['return_current'] != st.session_state['navigate_to']:
#     st.session_state['return_last'] = st.session_state['return_current']
#     st.session_state['return_current'] = st.session_state['navigate_to']


login = AMwebFL.login

logout = AMwebFL.logout

save_image_with_correct_orientation = AMwebFL.save_image_with_correct_orientation

delete_folder = AMwebFL.delete_folder

check_file_exist = AMwebFL.check_file_exist

find_file = AMwebFL.find_file

delete_AIfiles = AMwebFL.delete_AIfiles

get_greeting = AMwebFL.get_greeting

# 登录页面
# @st.experimental_dialog("登录")
def login_page():
    username = st.text_input("用户名")
    password = st.text_input("密码", type='password')
    if st.button("点击登录"):
        login(username, password)

@st.experimental_dialog("Cast your vote")
def choice(userName):
    st.write(f"确认操作->用户:{userName}?")
    if st.button("确认"):
        st.session_state['choice'] = 0
        st.rerun()
    if st.button("取消"):
        st.session_state['choice'] += 1
        st.rerun()

@st.experimental_dialog("删除AI相关文件")
def dialog_delete_AIfiles(userPath):
    
    if st.button("确认"):
        delete_AIfiles(userPath)
        st.session_state['redirect'] = True
        st.rerun()
    if st.button("取消"):
        st.rerun()

@st.experimental_dialog("删除该会员")
def dialog_delete_folder(userPath):
    
    if st.button("确认"):
        delete_folder(userPath)
        st.session_state['redirect'] = True
        st.session_state['navigate_to'] = '会员列表'
        st.session_state['selected_folder'] = ""
        st.rerun()
    if st.button("取消"):
        st.rerun()




# 设置页面配置
st.set_page_config(page_title="AM Inc.", layout="wide")


if st.button('主页'):
    st.session_state['redirect'] = True
    st.session_state['navigate_to'] = '主页'
    st.rerun()   

# with col3:
#     if st.session_state['return_last'] != "":
#        if st.button('返回'):
#             st.session_state['redirect'] = True
#             st.session_state['navigate_to'] = st.session_state['return_last']
#             st.rerun()
   


st.write("---")
# 检查用户是否登录
if not st.session_state['logged_in']:
    login_page()
else:
    # 创建侧边栏菜单
    with st.sidebar:
        selected = option_menu(
            "AM Inc.",
            ["主页", "会员列表", "会员详情", "继续录入", "咨询"],
            icons=["house", "folder-check", "person", "ui-checks-grid", "chat-square-dots"],
            menu_icon="person-workspace",
            manual_select=manual_select,
            default_index=0,
            key='menu_4'
        )
        st.session_state['navigate_to'] = selected
        st.write('---')
        if st.session_state.selected_folder != "":
            st.write(f'{get_greeting()},当前会员 > {st.session_state.selected_folder}')
        else:
            st.write(f'{get_greeting()}')
        if st.button('登出'):
            logout()
            st.rerun()
            
        


    # 根据菜单选项显示不同的页面内容
    navigate_to = st.session_state['navigate_to']
    if navigate_to == "主页":
        st.title("主页")
        st.write("欢迎来到主页！这是您的欢迎页面。")
        if st.button('新会员录入'):
            for key in st.session_state.keys():
                if key == 'logged_in':
                    continue
                if key == 'navigate_to':
                    continue
                del st.session_state[key]
            st.session_state['redirect'] = True
            st.session_state['navigate_to'] = '继续录入'
            st.rerun()
        if st.button('会员管理'):
            st.session_state['redirect'] = True
            st.session_state['navigate_to'] = '会员列表'
            st.rerun()    
            

    elif navigate_to == "会员列表":

        st.title("Clients")
        st.write("用户列表")
        directory = f'./userData/'
        folders = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
        for f in folders:
            if st.button(f):
                st.session_state['selected_folder'] = f
                st.session_state['redirect'] = True
                st.session_state['navigate_to'] = '会员详情'
                st.rerun()



    elif navigate_to == '会员详情':
        st.title('会员详情')
        if st.session_state['selected_folder'] == "":
            st.error('未选择会员')
            if st.button('去选择'):
                st.session_state['redirect'] = True
                st.session_state['navigate_to'] = '会员列表'
                st.rerun()
        else:
            userPath = f'./userData/'+st.session_state['selected_folder']+'/'
            if st.button('删除AI关联文件'):
                dialog_delete_AIfiles(userPath)
            if st.button('删除该会员'):
                
                dialog_delete_folder(userPath)
            # st.write(f'这里展示 | {st.session_state.selected_folder} | 的信息')
            initDF = pd.read_csv(userPath+'init.csv')
            col1, col2 = st.columns(2)
            with col1:

                st.write(f'会员姓名 : {initDF.name[0]}')
            with col2:

                st.write(f'联系方式 : {initDF.phone[0]}')
            


            tab1, tab2 = st.tabs(["AI体态识别", "AI分析报告"])
            with tab1:
                st.title('AI体态识别')
                st.write('---')
                
                if check_file_exist(userPath, 'resultF.jpg'):
                    st.write('正面视图')
                    st.image(userPath+"resultF.jpg", caption="", use_column_width=True)
                    st.write('正面部位细节')
                    container = st.container()
                    with container:
                        
                        cols = st.columns(2)  # Create 2 columns instead of 4
                        cols[0].image(userPath + "胯部.jpg", caption="胯部", use_column_width=True)
                        cols[1].image(userPath + "足部.jpg", caption="足部", use_column_width=True)
                        
                        cols = st.columns(2)  # Create another set of 2 columns
                        cols[0].image(userPath + "肩部.jpg", caption="肩部", use_column_width=True)
                        cols[1].image(userPath + "膝盖.jpg", caption="膝盖", use_column_width=True)


                        



                else:
                    if st.button('开始生成正面'):
                        with st.spinner('正在与云端数据同步...'):
                            time.sleep(random.randint(4, 8))
                            try:
                                imageF = find_file(userPath, 'imageF')
                                print('获取正面照片:',find_file(userPath, 'imageF'))
                                AMwebFL_poseChecker.main(userPath+imageF,True,userPath)
                                print('生成成功！')
                                st.success('生成成功！')
                            except BaseException:
                                print('生成失败')
                                st.error('生成失败!')
                            if st.button('加载报告'):
                                st.session_state['redirect'] = True
                                st.rerun()
                if check_file_exist(userPath, 'resultS.jpg'):
                    st.write('侧面视图')
                    st.image(userPath+"resultS.jpg", caption="", use_column_width=True)
                    st.write('侧面位细节')
                    container = st.container()
                    with container:
                        cols = st.columns(2)
                        cols[0].image(userPath + "骨盆.jpg", caption="骨盆", use_column_width=True)
                        cols[1].image(userPath + "脊椎.jpg", caption="脊椎", use_column_width=True)
                else:
                    if st.button('开始生成侧面'):
                        with st.spinner('正在与云端数据同步...'):
                            time.sleep(random.randint(4, 8))
                            try:
                                imageS = find_file(userPath, 'imageS')
                                print('获取侧面照片:',find_file(userPath, 'imageS'))
                                AMwebFL_poseChecker.main(userPath+imageS,False,userPath)
                                print('生成成功！')
                                st.success('生成成功！')
                            except BaseException:
                                print('生成失败')
                                st.error('生成失败!')
                            if st.button('加载报告'):
                                st.session_state['redirect'] = True
                                st.rerun()
            with tab2:
                st.title('AI分析报告')
                
                if check_file_exist(userPath, 'AIreport.csv'):
                    AIreport = pd.read_csv(userPath+'AIreport.csv')
                    if 'AI_overall_evaluation' in AIreport.columns:
                        quote_text = AIreport.AI_overall_evaluation[0]
                        quote = f"""
                        > “{quote_text}”  
                        """
                        st.markdown(quote)
                    if 'AI_recommendation' in AIreport.columns:
                        quote_text = AIreport.AI_recommendation[0]
                        quote = f"""
                        > “{quote_text}”  
                        """
                        st.markdown(quote)
                    st.write('---')

                    # 示例数据字典
                    posture_scores = {
                        '头部前倾': AIreport.aiCheck_Head_pos[0],
                        '含胸弓背': AIreport.aiCheck_Kyphosis[0],
                        '骨盆前倾': AIreport.aiCheck_pelvic_tilt[0],
                        '膝盖超伸': AIreport.aiCheck_Hyperextended_knee[0],
                        '高低胯': AIreport.aiCheck_hips[0],
                        '高低肩': AIreport.aiCheck_shoulders[0],
                        '长短腿': AIreport.aiCheck_knee[0],
                        '身体侧倾': AIreport.aiCheck_Body_Alignment[0],
                        '膝盖角度（左）': AIreport.aiCheck_Knee_Angle_left[0],
                        '膝盖角度（右）': AIreport.aiCheck_Knee_Angle_right[0]
                    }

                    # 根据角度范围映射分数和描述
                    def get_posture_description(angle):
                        if angle < 2:
                            return '正常'
                        elif 2 <= angle < 4:
                            return '轻度不均'
                        elif 4 <= angle < 8:
                            return '中度偏移'
                        else:
                            return '严重失衡'

                    # 相关害处数据库
                    posture_hazards = {
                        '头部前倾': "头部前倾会导致颈部和肩部疼痛，影响脊柱健康。",
                        '含胸弓背': "含胸弓背会导致背部疼痛，影响呼吸和消化功能。",
                        '骨盆前倾': "骨盆前倾会导致下背痛，影响腰部健康和姿势稳定性。",
                        '膝盖超伸': "膝盖超伸会增加膝盖受伤的风险，影响运动表现。",
                        '高低胯': "高低胯会导致骨盆不对称，影响步态和运动协调。",
                        '高低肩': "高低肩会导致肩部和背部疼痛，影响上肢功能。",
                        '长短腿': "长短腿会导致身体不对称，影响步态和整体平衡。",
                        '身体侧倾': "身体侧倾会导致脊柱侧弯和肌肉不平衡，影响整体姿势。",
                        '膝盖角度（左）': "膝盖角度异常会导致膝盖压力不均，增加受伤风险。",
                        '膝盖角度（右）': "膝盖角度异常会导致膝盖压力不均，增加受伤风险。"
                    }

                    # 创建推荐解决方案数据库
                    posture_recommendations = {
                        '头部前倾': "颈部拉伸和强化训练，纠正坐姿。",
                        '含胸弓背': "背部拉伸和强化训练，改善站姿和坐姿。",
                        '骨盆前倾': "核心肌群训练，骨盆倾斜矫正练习。",
                        '膝盖超伸': "膝盖稳定性训练，避免长时间站立。",
                        '高低胯': "骨盆平衡练习，髋部拉伸和强化训练。",
                        '高低肩': "肩部平衡练习，改善姿势和肩部稳定性。",
                        '长短腿': "步态训练，力量和拉伸练习。",
                        '身体侧倾': "脊柱侧弯矫正练习，核心稳定性训练。",
                        '膝盖角度（左）': "膝盖稳定性训练，改善腿部力量平衡。",
                        '膝盖角度（右）': "膝盖稳定性训练，改善腿部力量平衡。"
                    }

                    # 展示每个评分的进度条
                    st.markdown("### 体态总览")
                    if 'AI_posture_summary' in AIreport.columns:
                        quote_text = AIreport.AI_posture_summary[0]
                        quote = f"""
                        > “{quote_text}”  
                        """
                        st.markdown(quote)
                        # st.markdown(f"*AI:* :blue-background[***{AIreport.AI_posture_summary[0]}***]")

                    for metric, score in posture_scores.items():
                        # 获取分数对应的描述
                        description = get_posture_description(score)
                        st.markdown(f"**{metric} : {description} ({score} °)**")
                        st.progress(min(int(score / 20 * 100), 100))  # 假设最大角度为20度

                    # 找出三个分数最高的项目
                    highest_posture_scores = sorted(posture_scores.items(), key=lambda item: item[1], reverse=True)[:3]

                    # 展示最高评分的三个项目及其相关害处和推荐解决方案
                    st.markdown("### 信息和推荐解决方案")
                    for metric, score in highest_posture_scores:
                        description = get_posture_description(score)
                        hazard = posture_hazards.get(metric, "无相关信息")
                        recommendation = posture_recommendations.get(metric, "无推荐解决方案")
                        st.markdown(f"**{metric} : <span style='font-size:20px'>{description}</span>**", unsafe_allow_html=True)
                        st.markdown(f"**信息:** {hazard}")
                        st.markdown(f"*推荐课程:* :blue-background[***{recommendation}***]")




                    # 创建一个示例数据字典
                    scores = {
                        'BMI评分': AIreport.BMI_score[0],
                        '肌肉力量评分': AIreport.Strength_score[0],
                        '柔韧性评分': AIreport.Flexibility_score[0],
                        '心肺功能评分': AIreport.Cardiovascular_score[0],
                        '核心稳定性评分': AIreport.Stability_score[0],
                    }
                    # 分数和描述的映射
                    score_map = {
                        1: '较差',
                        2: '中等',
                        3: '较好'
                    }

                    hazards_database = {
                        'BMI评分': "高BMI会增加心脏病、糖尿病和某些癌症的风险。",
                        '肌肉力量评分': "肌肉力量不足会增加受伤的风险，影响日常活动和生活质量。",
                        '柔韧性评分': "柔韧性不足会导致关节和肌肉僵硬，限制运动范围，增加受伤风险。",
                        '心肺功能评分': "心肺功能不足会导致疲劳、呼吸困难，增加心脏病和高血压的风险。",
                        '核心稳定性评分': "核心稳定性不足会导致姿势问题、下背痛和运动能力下降。",
                    }

                    # 创建推荐课程数据库
                    course_recommendations = {
                        'BMI评分': "瑜伽、普拉提、有氧舞蹈。",
                        '肌肉力量评分': "阻力训练、力量训练、HIIT。",
                        '柔韧性评分': "瑜伽、伸展运动、普拉提。",
                        '心肺功能评分': "跑步、游泳、动感单车。",
                        '核心稳定性评分': "普拉提、核心训练、平衡训练。",
                    }




                    # 展示每个评分的进度条
                    st.markdown("### 运动能力总览")
                    if 'AI_fitness_summary' in AIreport.columns:
                        quote_text = AIreport.AI_fitness_summary[0]
                        quote = f"""
                        > “{quote_text}”  
                        """
                        st.markdown(quote)
                    for metric, score in scores.items():
                        # 获取分数对应的描述
                        description = score_map.get(int(score), '未知')  # 使用int(score)如果score是浮点数
                        st.markdown(f"**{metric} : {description}**")
                        st.progress(int(score / 4 * 100))  # 假设最高分为3

                    # 排除综合评分
                    filtered_scores = {k: v for k, v in scores.items() if k != '综合评分'}

                    # 找出三个分数最低的项目
                    lowest_scores = sorted(filtered_scores.items(), key=lambda item: item[1])[:3]

                    # 展示最低评分的三个项目及其相关害处和推荐课程
                    st.markdown("### 信息和推荐课程")
                    for metric, score in lowest_scores:
                        description = score_map.get(int(score), '未知')
                        hazard = hazards_database.get(metric, "无相关信息")
                        course = course_recommendations.get(metric, "无推荐课程")
                        st.markdown(f"**{metric} : <span style='font-size:20px'>{description}</span>**", unsafe_allow_html=True)
                        st.markdown(f"**信息:** {hazard}")
                        st.markdown(f"*推荐课程:* :blue-background[***{course}***]")

                    




                                
                else:
                    st.write('---')
                    if st.button('开始生成报告'):
                        with st.spinner('正在与云端数据同步...'):
                            time.sleep(random.randint(1,3))
                            try:
                                AMwebFL.AIreport(userPath,'init.csv','poseDF_F.csv','poseDF_S.csv')
                                print('生成成功！')
                                st.success('生成成功！')
                                
                            except BaseException:
                                print('生成失败')
                                st.error('生成失败!')
                            if st.button('加载报告'):
                                st.session_state['redirect'] = True
                                st.rerun()
                st.write("")
                st.write("")
                if st.button('返回会员列表'):
                    st.session_state['redirect'] = True
                    st.session_state['navigate_to'] = '会员列表'
                    st.rerun()
            
            

    elif navigate_to == "继续录入":

        def check_mandatory_fields(fields):
            missing_fields = []
            for field, value in fields.items():
                if not value or value == "请选择":
                    missing_fields.append(field)
            return missing_fields

        if st.button('重置选项'):
            for key in st.session_state.keys():
                if key == 'logged_in':
                    continue
                if key == 'navigate_to':
                    continue
                del st.session_state[key]
            st.session_state['redirect'] = True
            st.session_state['navigate_to'] = '继续录入'
            st.rerun()

        # 设置标题
        st.title("数据录入")
        st.subheader("静态数据（问询）")

        # 姓名/昵称
        name = st.text_input("姓名/昵称:")

        # 电话
        phone = st.text_input("电话:")

        # 性别
        st.write("性别:")

        if 'gender' not in st.session_state:
            st.session_state.gender = ""
        if st.session_state.gender == "":
            if st.button("女", key="gender_female"):
                st.session_state.gender = "女"
                st.rerun()
            if st.button("男", key="gender_male"):
                st.session_state.gender = "男"
                st.rerun()
        else:
            if st.button(st.session_state.gender, key="genderRemove"):
                st.session_state.gender = ""
                st.rerun()
        gender = st.session_state.gender

        # 出生日期
        birthdate = st.date_input("出生日期:")

        # 身高
        height = st.selectbox("身高(cm):", ["请选择"] + [f"{i}cm" for i in range(120, 201)])

        # 体重
        weight = st.selectbox("体重(kg):", ["请选择"] + [f"{i}kg" for i in range(30, 101)])

        # 是否怀孕
        st.write("是否怀孕:")

        if 'pregnant' not in st.session_state:
            st.session_state.pregnant = ""
        if st.session_state.pregnant == "":
            if st.button("是", key="pregnant_yes"):
                st.session_state.pregnant = "是"
                st.rerun()
            if st.button("否", key="pregnant_no"):
                st.session_state.pregnant = "否"
                st.rerun()
        else:
            if st.button(st.session_state.pregnant, key="pregnantRemove"):
                st.session_state.pregnant = ""
                st.rerun()
        pregnant = st.session_state.pregnant

        # 是否有小孩
        st.write("是否有小孩:")

        if 'children' not in st.session_state:
            st.session_state.children = ""
        if st.session_state.children == "":
            if st.button("是", key="children_yes"):
                st.session_state.children = "是"
                st.rerun()
            if st.button("否", key="children_no"):
                st.session_state.children = "否"
                st.rerun()
        else:
            if st.button(st.session_state.children, key="childrenRemove"):
                st.session_state.children = ""
                st.rerun()
        children = st.session_state.children

        # 之前是否有过运动历史
        st.write("之前是否有过运动历史:")

        if 'fitnessLevel' not in st.session_state:
            st.session_state.fitnessLevel = ""
        if st.session_state.fitnessLevel == "":
            if st.button("小白", key="fitness_novice"):
                st.session_state.fitnessLevel = "小白"
                st.rerun()
            if st.button("基础", key="fitness_basic"):
                st.session_state.fitnessLevel = "基础"
                st.rerun()
            if st.button("中度", key="fitness_intermediate"):
                st.session_state.fitnessLevel = "中度"
                st.rerun()
            if st.button("资深", key="fitness_advanced"):
                st.session_state.fitnessLevel = "资深"
                st.rerun()
        else:
            if st.button(st.session_state.fitnessLevel, key="fitnessRemove"):
                st.session_state.fitnessLevel = ""
                st.rerun()
        fitnessLevel = st.session_state.fitnessLevel

        # 医学史
        st.write("医学史(可选):")
        injuryPart = '无'
        disease = '无'
        currentlyPain = '无'

        if st.checkbox("之前有受过伤(部位)"):
            injuryPart = st.text_input("之前有受过伤(部位)")

        if st.checkbox("急/慢性病报告"):
            disease = st.text_input("急/慢性病报告")

        if st.checkbox("目前正在疼痛(部位)"):
            currentlyPain = st.text_input("目前正在疼痛(部位)")

        # 每周可以运动的次数
        daysOfWeek = st.selectbox("每周可以运动的次数:", ["请选择"] + [f"{i}天" for i in range(1, 8)])

        # 每天可以在什么时候运动
        timeOfDay = st.selectbox("每天可以在什么时候运动:", ["请选择", "清晨", "上午", "下午", "晚上"])

        st.subheader("动态数据/功能性筛查（运动）（注意：按顺序测试）")

        # 各类测试
        shoulderMobility = st.selectbox("肩部灵活性测试:", ["请选择", "手指轻松接触", "手指接触，但有困难", "手指无法接触。或出现疼痛"])
        activeStraightLegRaise = st.selectbox("主动直腿抬高:", ["请选择", "腿部抬高超过对侧大腿的中点", "腿部抬高刚刚到达对侧大腿的中点", "腿部抬高未达到对侧大腿的中点，或出现疼痛"])
        hurdleStep = st.selectbox("站立式臀桥:", ["请选择", "身体控制良好，动作流畅", "动作完成，但控制不佳", "无法完成动作，或出现疼痛"])
        deepSquat = st.selectbox("深蹲:", ["请选择", "无需协助，完成深蹲，大腿低于膝盖", "需要协助（如脚下垫物）完成深蹲", "无法完成深蹲，即使有协助，或出现疼痛"])
        rotaryStability = st.selectbox("旋转稳定性:", ["请选择", "流畅完成动作", "完成动作，但不流畅", "无法完成动作，或出现疼痛"])
        highKnees = st.selectbox("原地高抬腿:", ["请选择", "超过120次，特别是接近或超过150次", "80-120次", "30-60次，或出现疼痛"])

        # 上传文件
        front_view = st.file_uploader("正面拍照:", type=["jpg", "jpeg", "png"])
        side_view = st.file_uploader("侧面拍照:", type=["jpg", "jpeg", "png"])

        # 提交按钮
        if st.button("提交", key="submit"):
            mandatory_fields = {
                "姓名/昵称": name,
                "电话": phone,
                "性别": gender,
                "出生日期": birthdate,
                "身高": height,
                "体重": weight,
                "是否怀孕": pregnant,
                "是否有小孩": children,
                "之前是否有过运动历史": fitnessLevel,
                "每周可以运动的次数": daysOfWeek,
                "每天可以在什么时候运动": timeOfDay,
                "肩部灵活性测试": shoulderMobility,
                "主动直腿抬高": activeStraightLegRaise,
                "站立式臀桥": hurdleStep,
                "深蹲": deepSquat,
                "旋转稳定性": rotaryStability,
                "原地高抬腿": highKnees,
                "正面拍照": front_view,
                "侧面拍照": side_view
            }

            missing_fields = check_mandatory_fields(mandatory_fields)
            if missing_fields:
                st.error(f"请填写以下必填项: {', '.join(missing_fields)}")
            else:
                st.success("所有必填项已填写！开始上传...")
                with st.spinner('正在与云端数据同步...'):

                    time.sleep(random.randint(2, 4))
                    initDF = pd.DataFrame()
                    initDF.loc[len(initDF),'datetime'] = datetime.datetime.now()
                    initDF.loc[len(initDF)-1,'name'] = name
                    initDF.loc[len(initDF)-1,'phone'] = phone
                    initDF.loc[len(initDF)-1,'gender'] = gender
                    initDF.loc[len(initDF)-1,'birthdate'] = birthdate
                    initDF.loc[len(initDF)-1,'height'] = height
                    initDF.loc[len(initDF)-1,'weight'] = weight
                    initDF.loc[len(initDF)-1,'pregnant'] = pregnant
                    initDF.loc[len(initDF)-1,'children'] = children
                    initDF.loc[len(initDF)-1,'fitnessLevel'] = fitnessLevel
                    initDF.loc[len(initDF)-1,'injuryPart'] = injuryPart
                    initDF.loc[len(initDF)-1,'disease'] = disease
                    initDF.loc[len(initDF)-1,'currentlyPain'] = currentlyPain
                    initDF.loc[len(initDF)-1,'daysOfWeek'] = daysOfWeek
                    initDF.loc[len(initDF)-1,'timeOfDay'] = timeOfDay
                    initDF.loc[len(initDF)-1,'shoulderMobility'] = shoulderMobility
                    initDF.loc[len(initDF)-1,'activeStraightLegRaise'] = activeStraightLegRaise
                    initDF.loc[len(initDF)-1,'hurdleStep'] = hurdleStep
                    initDF.loc[len(initDF)-1,'deepSquat'] = deepSquat
                    initDF.loc[len(initDF)-1,'rotaryStability'] = rotaryStability
                    initDF.loc[len(initDF)-1,'highKnees'] = highKnees
                    # 创建目录
                    directory = './userData/' + name + phone
                    if os.path.exists(directory):
                        directory += '-' + str(uuid.uuid4().hex)
                        
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                                
                    file_path = os.path.join(directory, 'init.csv')
                    initDF.to_csv(file_path, index=False)
                    save_image_with_correct_orientation(front_view, directory, 'imageF')
                    save_image_with_correct_orientation(side_view, directory, 'imageS')
                    # 保存图片到目录
                    # imageF = Image.open(front_view)
                    # imageS = Image.open(side_view)
                    # newName1 = ''
                    # newName2 = ''
                    # while newName1 == newName2:
                    #     newName1 = 'imageF-' + str(uuid.uuid4().hex) + front_view.name
                    #     newName2 = 'imageS-' + str(uuid.uuid4().hex) + side_view.name

                    # imageF.save(os.path.join(directory,newName1))
                    # imageS.save(os.path.join(directory,newName2))
                    st.success('上传完成！')
                
            
            
            


            # if front_view:
            #     st.image(front_view, caption="正面拍照", use_column_width=True)
            # if side_view:
            #     st.image(side_view, caption="侧面拍照", use_column_width=True)



    elif selected == "咨询":
        pass






    # 主页面内容
    st.write("---")
    st.markdown(right_aligned_text, unsafe_allow_html=True)

        

# print(navigate_to)