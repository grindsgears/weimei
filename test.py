import Daifuku_free_api
import pandas as pd
initDF = pd.read_csv('/Users/mkbm/Library/Containers/com.tencent.WeWorkMac/Data/WeDrive/AM Inc./AM健康/Code/streamlitWeb/userData/测试2/AIreport.csv')
AI_fitness_summary,AI_posture_summary,AI_overall_evaluation,AI_recommendation = Daifuku_free_api.talk(initDF)
initDF.loc[len(initDF)-1,'AI_fitness_summary'] = AI_fitness_summary
initDF.loc[len(initDF)-1,'AI_posture_summary'] = AI_posture_summary
initDF.loc[len(initDF)-1,'AI_overall_evaluation'] = AI_overall_evaluation
initDF.loc[len(initDF)-1,'AI_recommendation'] = AI_recommendation