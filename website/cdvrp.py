import sys
import sqlite3
import numpy as np
import pandas as pd
from tqdm import trange
import csv


def process_command_line_arguments(arguments):
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


class aco:
    def __init__(self, dvrp_id, in_file, db_path, origin, max_pall, max_lbs, n_ants, n_iterations, alpha=1, beta=1, evaporation_rate=0.5, Q=1):
        self.dvrp_id = dvrp_id
        self.in_file = in_file
        self.db_path = db_path
        self.origin = origin
        self.max_pall = int(max_pall)
        self.max_lbs = int(max_lbs)
        self.n_ants = int(n_ants)
        self.n_iterations = int(n_iterations)
        self.alpha = int(alpha)
        self.beta = int(beta)
        self.evaporation_rate = float(evaporation_rate)
        self.Q = float(Q)

    
    def distance(self, point_a, point_b):
        distance = self.perm_df.loc[point_a, point_b]
        return distance


    def load_best_path_id_p(self):
        points_query = (
            '''
            select max(id_set)
            from dvrp_set
            ;
            '''
        )

        max_id_set = pd.read_sql_query(points_query, self.con)
        if max_id_set.iloc[0, 0] == None:
            max_val = 0
        else:
            max_val = int.from_bytes(max_id_set.iloc[0, 0], 'little') + 1

        cluster_l = []
        cluster_counter = 0
        status = False
        sequence_n = 0
        for item in self.best_path_id_p:
            if status == False:
                sequence_n = 0
            if item == self.origin and status == False:
                cluster_l.append([max_val, self.dvrp_id, cluster_counter, 'tractor_' + str(cluster_counter), item, sequence_n])
                sequence_n += 1
                status = True
            elif item != self.origin and status == True:
                cluster_l.append([max_val, self.dvrp_id, cluster_counter, 'tractor_' + str(cluster_counter), item, sequence_n])
                sequence_n += 1
            elif item != self.origin and status == False:
                status = True
                cluster_l.append([max_val, self.dvrp_id, cluster_counter, 'tractor_' + str(cluster_counter), item, sequence_n])
                sequence_n += 1
            elif item == self.origin and status == True:
                status = False
                cluster_l.append([max_val, self.dvrp_id, cluster_counter, 'tractor_' + str(cluster_counter), item, sequence_n])
                cluster_counter += 1
            
        cluster_l = [x for x in cluster_l if x[4] != self.origin]

        self.cur.executemany('insert into dvrp_set (id_set, dvrp_id, cluster_id, cluster_name, point, sequence) values (?, ?, ?, ?, ?, ?)', cluster_l)
        self.cur.execute('insert into dvrp_origin (dvrp_id, dvrp_origin) values (?, ?)', [self.dvrp_id, self.origin])
        self.con.commit()


    def run(self):
        with open(self.in_file, 'r') as r:
            reader = csv.reader(r)
            in_points = []
            for row in reader:
                in_points.append(row[0])

        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()

        self.cur.execute('create temporary table if not exists temp_items (item Text)')
        self.cur.execute('delete from temp_items')
        self.cur.executemany('insert into temp_items (item) values (?)', [(item,) for item in in_points])
        points_query = (
            '''
            select gp.id_p, gp.pall_avg, gp.lbs_avg
            from geo_points gp, temp_items tp
            where gp.id_p = tp.item
            ;
            '''
        )

        self.points_df = pd.read_sql_query(points_query, self.con)

        perm_query = (
            '''
            select id_1, id_2, distance
            from geo_permutations
            ;
            '''
        )

        perm_df = pd.read_sql_query(perm_query, self.con)
        self.perm_df = perm_df.pivot(index='id_1', columns='id_2', values='distance')

        n_points = len(self.points_df)
        pheromone = np.ones((n_points, n_points))
        best_path = None
        best_path_length = np.inf
        self.origin_index = self.points_df[self.points_df['id_p'] == self.origin].index[0]
        
        for iteration in trange(self.n_iterations):
            paths = []
            path_lengths = []
            
            for ant in range(self.n_ants):
                visited = [False] * n_points
                
                while True:
                    current_point = np.random.randint(n_points)
                    if current_point != self.origin_index:
                        break
                
                visited[current_point] = True
                path = [self.origin_index, current_point]
                point_a = self.points_df.iloc[self.origin_index, 0]
                point_b = self.points_df.iloc[current_point, 0]
                path_length = self.distance(point_a, point_b)
                current_load = self.points_df.iloc[current_point, 1]
                current_weight = self.points_df.iloc[current_point, 2]
                
                while False in visited:
                    unvisited = np.where(np.logical_not(visited))[0]
                    probabilities = np.zeros(len(unvisited))
                    
                    for i, unvisited_point in enumerate(unvisited):
                        point_a = self.points_df.iloc[current_point, 0]
                        point_b = self.points_df.iloc[unvisited_point, 0]
                        dist = self.distance(point_a, point_b)**self.beta
                        pheromone_value = pheromone[current_point, unvisited_point]**self.alpha
                        probabilities[i] = pheromone_value / dist
                    
                    p_sum = np.sum(probabilities)
                    probabilities /= p_sum
                    
                    next_point = np.random.choice(unvisited, p=probabilities)
                    if next_point == self.origin_index:
                        continue
                    next_load = self.points_df.iloc[next_point, 1]
                    next_weight = self.points_df.iloc[next_point, 2]
                    
                    if current_load + next_load > self.max_pall or current_weight + next_weight > self.max_lbs:
                        path.append(self.origin_index)
                        point_a = self.points_df.iloc[current_point, 0]
                        point_b = self.points_df.iloc[self.origin_index, 0]
                        path_length += self.distance(point_a, point_b)
                        visited[self.origin_index] = True
                        current_point = self.origin_index
                        current_load = 0
                        current_weight = 0
                    else:
                        path.append(next_point)
                        current_load += next_load
                        current_weight += next_weight
                        point_a = self.points_df.iloc[current_point, 0]
                        point_b = self.points_df.iloc[next_point, 0]
                        path_length += self.distance(point_a, point_b)
                        visited[next_point] = True
                        current_point = next_point
                
                path.append(self.origin_index)
                paths.append(path)
                point_a = self.points_df.iloc[current_point, 0]
                point_b = self.points_df.iloc[self.origin_index, 0]
                path_length += self.distance(point_a, point_b)
                path_lengths.append(path_length)
                
                if path_length < best_path_length:
                    best_path = path
                    best_path_length = path_length
            
            pheromone *= self.evaporation_rate

            for path, path_length in zip(paths, path_lengths):
                for i in range(n_points-1):
                    pheromone[path[i], path[i + 1]] += self.Q / path_length
                pheromone[path[-1], path[0]] += self.Q / path_length
        
        print('best path index:')
        print(best_path)
        self.best_path_id_p = [self.points_df.iloc[i, 0] for i in best_path]
        print('best path id_p:')
        print(self.best_path_id_p)
        print('best path length:')
        print(best_path_length)

        self.load_best_path_id_p()
        self.con.close()


functions = {
    'run_aco': lambda **kwargs: aco(**kwargs).run()
}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python vrp.py <function_name> key1=value1 key2=value2 ...")
        sys.exit(1)

    func_name = sys.argv[1]
    kwargs = process_command_line_arguments(sys.argv[2:])

    if func_name in functions:
        result = functions[func_name](**kwargs)
        print("Result: ", result)
    else:
        print(f"No function named '{func_name}' found.")