import platform
import os
from pathlib import Path
import random
import pandas as pd
import math
from itertools import permutations
import csv
import sqlite3


class Model:
    def __init__(self, file_name: str, points_name: str, distance_name: str, n: int, multiplier: int, db_name, sql: bool):
        self.file_name = file_name
        self.points_name = points_name
        self.distance_name = distance_name
        self.n = n
        self.multiplier = multiplier
        self.img_path = None
        self.os_type = None
        self.db_name = db_name
        self.con = None
        self.sql = sql


    def imgFolder(self):
        os_type = platform.system()
        if os_type == 'Windows':
            img_path = os.path.dirname(__file__)
        elif os_type == 'Linux':
            img_path = os.path.dirname(os.path.abspath(__file__))

        img_path = Path(img_path)
        img_path = img_path.parent
        self.img_path = img_path
        self.os_type = os_type
    
    
    def createRandomPoints(self):
        if self.os_type == 'Windows':
            comb_input_fix = str(self.img_path) + '\\input\\' + 'ran_' + self.file_name + '.csv'
        if self.os_type == 'Linux':
            comb_input_fix = str(self.img_path) + '/input/' + 'ran_' + self.file_name + '.csv'

        arr = []
        for i in range(0,self.n):
            arr.append([round(random.random() * self.multiplier, 6), round(random.random() * self.multiplier, 6)])
            
        df = pd.DataFrame(arr, columns=['x','y'])

        if self.sql:
            df['point'] = '(' + df['x'].astype(str) + ',' + df['y'].astype(str) + ')'
            column_order = ['point'] + list(df.columns[:-1])
            df = df[column_order]

        return [df, comb_input_fix]

    
    def createRandomPointsWithDistance(self):
        if self.os_type == 'Windows':
            perm_input_fix = str(self.img_path) + '\\input\\' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(self.img_path) + '\\input\\' + 'ran_points_' + self.file_name + '.csv'
        if self.os_type == 'Linux':
            perm_input_fix = str(self.img_path) + '/input/' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(self.img_path) + '/input/' + 'ran_points_' + self.file_name + '.csv'
        
        arr = []
        dist_list = []

        for i in range(0,self.n):
            arr.append([round(random.random() * self.multiplier, 6), round(random.random() * self.multiplier, 6)])
        
        df_points = pd.DataFrame(arr, columns=['x','y'])
        perm = list(permutations(arr, 2))
        for index, item in enumerate(perm):
            distance = float(math.sqrt((item[1][0] - item[0][0])**2 + ((item[1][1] - item[0][1])**2)))
            dist_list.append([item[1][0], item[0][0], item[1][1], item[0][1], distance])
        
        df_perm = pd.DataFrame(dist_list, columns=['x2', 'x1', 'y2', 'y1','distance'])

        if self.sql:
            df_points['point'] = '(' + df_points['x'].astype(str) + ',' + df_points['y'].astype(str) + ')'
            column_order = ['point'] + list(df_points.columns[:-1])
            df_points = df_points[column_order]

            df_perm['perm'] = '(' + df_perm['x2'].astype(str)+','+df_perm['x1'].astype(str)+','+df_perm['y2'].astype(str)+','+df_perm['y1'].astype(str) + ')'
            column_order = ['perm'] + list(df_perm.columns[:-1])
            df_perm = df_perm[column_order]

        return [[df_points, points_input_fix], [df_perm, perm_input_fix]]


    def addDistanceToPoints(self):
        pass


    def saveToCsv(self, items):
        for item in items:
            item[0].to_csv(item[1], index=False)


    def dfInput(self):
        if self.os_type == 'Windows':
            perm_input_fix = str(self.img_path) + '\\input\\' + self.distance_name + '.csv'
            points_input_fix = str(self.img_path) + '\\input\\' + self.points_name + '.csv'
            route_output_fix = str(self.img_path) + '\\output\\' + 'route_' + self.file_name + '.png'
            progress_output_fix = str(self.img_path) + '\\output\\' + 'progress_' + self.file_name + '.png'
            csv_output_fix = str(self.img_path) + '\\output\\' + 'route_' + self.file_name + '.csv'
        if self.os_type == 'Linux':
            perm_input_fix = str(self.img_path) + '/input/' + self.distance_name + '.csv'
            points_input_fix = str(self.img_path) + '/input/' + self.points_name + '.csv'
            route_output_fix = str(self.img_path) + '/output/' + 'route_' + self.file_name + '.png'
            progress_output_fix = str(self.img_path) + '/output/' + 'progress_' + self.file_name + '.png'
            csv_output_fix = str(self.img_path) + '/output/' + 'route_' + self.file_name + '.csv'
        
        if self.sql:
            points = pd.read_csv(points_input_fix)
        if self.sql == False:
            with open(points_input_fix, 'r') as f:
                reader = csv.reader(f)
                points = list(reader)

            points = [[round(float(j), 6) for j in i] for i in points[1:]]

        combination_distance = pd.read_csv(perm_input_fix)

        return points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix
    

    def initDb(self):
        if self.os_type == 'Windows':
            db_path_fix = str(self.img_path) + '\\' + self.db_name
        if self.os_type == 'Linux':
            db_path_fix = str(self.img_path) + '/' + self.db_name

        con = sqlite3.connect(db_path_fix)
        self.con = con
        
        return con
    

    def closeDb(self):
        self.con.close()

    
    def sqlUpdate(self, points, combination_distance):
        cur = self.con.cursor()

        for row in cur.execute('''
            select
            case
                when exists (select 1 from stage_points)
                then 1
                else 0
            end
        '''):
            print(int(row[0]))

        if int(row[0]) == 1:
            cur.execute('delete from stage_points')
            self.con.commit()

        points = points.set_index('point')
        points.to_sql('stage_points', self.con, if_exists='append', index_label='point')
        self.con.commit()

        cur.execute('''
            insert into points(point, x, y, pallets, weight)
            select *
            from stage_points
            where point not in (
                select point
                from points
            )
        ''')
        self.con.commit()

        for row in cur.execute('''
            select
            case
                when exists (select 1 from stage_permutation_distance)
                then 1
                else 0
            end
        '''):
            print(int(row[0]))

        if int(row[0]) == 1:
            cur.execute('delete from stage_permutation_distance')
            self.con.commit()

        combination_distance = combination_distance.set_index('perm')
        combination_distance.to_sql('stage_permutation_distance', self.con, if_exists='append', 
        index_label='perm')
        self.con.commit()

        cur.execute('''
            insert into permutation_distance(perm, x2, x1, y2, y1, distance)
            select *
            from stage_permutation_distance
            where perm not in (
                select perm
                from permutation_distance
            )
        ''')
        self.con.commit()


    def addPallLbtoDf(self, items):
        pall = []
        lbs = []
        sub_arr = False
        
        if type(items[0]) == list: sub_arr = True
        
        if sub_arr == True:
            df = items[0][0]
        elif sub_arr == False:
            df = items[0]

        for i in range(0,self.n):
            # number of pallets are tought as if it were to be more than 8 for a big or hub store
            if random.random() <= 0.2:
                count = random.randint(9, 15)
            else:
                count = random.randint(1, 8)
            pall.append(count)
            weight = count * round(random.uniform(1200, 1700), 6)
            lbs.append(weight)

        df['pallets'] = pall
        df['weight'] = lbs

        if sub_arr:
            items[0][0] = df
            return items
        elif sub_arr == False:
            items[0] = df
            return items