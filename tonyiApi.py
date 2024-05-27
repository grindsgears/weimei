import requests
import os

tools = [
            {
                "type": "function",
                "function":{
                    "name": "分析运动数据",
                    "description": "分析会员的健身数据并提供专业建议",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "fitness_summary": {
                            "type": "string",
                            "description": "根据运动能力综合评分的总结"
                        },
                        "posture_summary": {
                            "type": "string",
                            "description": "根据AI视觉识别体态评估结果的总结"
                        },
                        "overall_evaluation": {
                            "type": "string",
                            "description": "总体评价"
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "后续运动计划推荐"
                        }
                    },
                    "required": ["fitness_summary", "posture_summary", "overall_evaluation", "recommendation"]
                }
                    
                }
                
            }
        ]

member_data = """
datetime	name	phone	gender	birthdate	height	weight	pregnant	children	fitnessLevel	injuryPart	disease	currentlyPain	daysOfWeek	timeOfDay	shoulderMobility	activeStraightLegRaise	hurdleStep	deepSquat	rotaryStability	highKnees	aiCheck_hips	aiCheck_shoulders	aiCheck_knee	aiCheck_Body_Alignment	aiCheck_Knee_Angle_right	aiCheck_Knee_Angle_left	aiCheck_Head_pos	aiCheck_Kyphosis	aiCheck_pelvic_tilt	aiCheck_Hyperextended_knee	posture_max	posture_min	posture_mean	height_m	BMI	BMI_score	Strength_score	Flexibility_score	Cardiovascular_score	Stability_score	posture_score	Average_score
2024-05-26 20:26:17.170699	测试	2	女	2024-05-26	120	30	是	是	0	无	无	无	2	上午	2	3	2	3	3	2	0.71	4.49	5.1	1.24	3.26	1.52	0.12	-0.15	5.23	2.63	5.23	-0.15	2.415	1.2	20.833333333333300	3	3	2	2	2	2.195	2.3658333333333300
"""


api_key = 'sk-83152db4ffd94f36bad0832d1f83b8e3'
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
headers = {'Content-Type': 'application/json',
           'Authorization':f'Bearer {api_key}'}
body = {
    'model': 'qwen-plus',
    "input": {
        "messages": [
            {"role": "system", "content": "你是一位健身顾问，擅长分析会员的健身数据并提供专业建议。"},
            {"role": "user", "content": f"以下是会员的详细测试数据：\n{member_data}\n请根据以下四部分提供分析和建议：\n1. 根据“运动能力综合评分”的情况，给出总结。\n2. 根据“AI视觉识别体态评估结果”的情况，给出总结。\n3. 给出该用户的总体评价与后续运动计划推荐。\n注意：因为是后台系统，不要提到任何与具体分数有关的数字。"}
        ]
    },
    "parameters": {
        "result_format": "message",
        "tools": tools
    }
}

response = requests.post(url, headers=headers, json=body)
print(response.json())




