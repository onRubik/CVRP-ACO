import platform
from pathlib import Path
import os
import pandas as pd


os_type = platform.system()
if os_type == 'Windows':
    project_path = os.path.dirname(__file__)
elif os_type == 'Linux':
    project_path = os.path.dirname(os.path.abspath(__file__))

# return project_path, os_type
img_path = project_path
img_path = Path(img_path)
img_path = img_path.parent

if os_type == 'Windows':
    comb_input_fix = str(img_path) + '\\input\\' + 'ran_dis_' + 'ran1' + '.csv'
if os_type == 'Linux':
    comb_input_fix = str(img_path) + '/input/' + 'ran_dis_' + 'ran1' + '.csv'

combination_distance = pd.read_csv(comb_input_fix)

# 51.309696,78.138793,27.227887,178.556843
segment_distance = combination_distance.where((combination_distance['x1']==78.138793) & (combination_distance['y1']==178.556843) & (combination_distance['x2']==51.309696) & (combination_distance['y2']==27.227887))
segment_distance = segment_distance.dropna()
print(segment_distance)
segment_distance = segment_distance.iloc[0, 2]
print(segment_distance)