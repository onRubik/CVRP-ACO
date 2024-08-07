# source: https://induraj2020.medium.com/implementation-of-ant-colony-optimization-using-python-solve-traveling-salesman-problem-9c14d3114475
# medium: Implementing Ant colony optimization in python- solving Traveling salesman problem

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


# Example usage:
# points = np.random.rand(10, 3) # Generate 10 random 3D points
# ant_colony_optimization(in_file='input.csv', db_path='instance/vrp_db.db', origin='way/1180028681', max_pall=None, max_lbs=None, n_ants=10, n_iterations=100, alpha=1, beta=1, evaporation_rate=0.5, Q=1)
class aco:
    def __init__(self, in_file, db_path, origin, max_pall, max_lbs, n_ants, n_iterations, alpha=1, beta=1, evaporation_rate=0.5, Q=1):
        self.in_file = in_file
        self.db_path = db_path
        self.origin = origin
        self.max_pall = int(max_pall)
        self.max_lbs = int(max_lbs)
        self.n_ants = int(n_ants)
        self.n_iterations = int(n_iterations)
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.evaporation_rate = float(evaporation_rate)
        self.Q = float(Q)

    
    def distance(self, point_a, point_b):
        distance = self.perm_df.loc[point_a, point_b]
        return distance


    # origin = way/1180028681
    def run(self):
        with open(self.in_file, 'r') as r:
            reader = csv.reader(r)
            in_points = []
            for row in reader:
                in_points.append(row[0])

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        cur.execute('create temporary table if not exists temp_items (item Text)')
        cur.execute('delete from temp_items')
        cur.executemany('insert into temp_items (item) values (?)', [(item,) for item in in_points])
        points_query = (
            '''
            select gp.id_p, gp.pall_avg, gp.lbs_avg
            from geo_points gp, temp_items tp
            where gp.id_p = tp.item
            ;
            '''
            )

        self.points_df = pd.read_sql_query(points_query, con)
        print(self.points_df)

        perm_query = (
            '''
            select id_1, id_2, distance
            from geo_permutations
            ;
            '''
            )

        perm_df = pd.read_sql_query(perm_query, con)
        self.perm_df = perm_df.pivot(index='id_1', columns='id_2', values='distance')
        print(self.perm_df)

        n_points = len(self.points_df)
        print('n_points:', n_points)
        pheromone = np.ones((n_points, n_points))
        best_path = None
        best_path_length = np.inf
        
        for iteration in trange(self.n_iterations):
            paths = []
            path_lengths = []
            
            for ant in range(self.n_ants):
                visited = [False]*n_points
                current_point = np.random.randint(n_points)
                visited[current_point] = True
                path = [current_point]
                path_length = 0
                
                while False in visited:
                    unvisited = np.where(np.logical_not(visited))[0]
                    probabilities = np.zeros(len(unvisited))
                    
                    for i, unvisited_point in enumerate(unvisited):
                        point_a = self.points_df.iloc[current_point, 0]
                        point_b = self.points_df.iloc[unvisited_point, 0]
                        probabilities[i] = pheromone[current_point, unvisited_point]**self.alpha / self.distance(point_a, point_b)**self.beta
                    
                    probabilities /= np.sum(probabilities)
                    
                    next_point = np.random.choice(unvisited, p=probabilities)
                    path.append(next_point)
                    point_a = self.points_df.iloc[current_point, 0]
                    point_b = self.points_df.iloc[next_point, 0]
                    path_length += self.distance(point_a, point_b)
                    visited[next_point] = True
                    current_point = next_point
                
                paths.append(path)
                path_lengths.append(path_length)
                
                if path_length < best_path_length:
                    best_path = path
                    best_path_length = path_length
            
            pheromone *= self.evaporation_rate
            
            for path, path_length in zip(paths, path_lengths):
                for i in range(n_points-1):
                    pheromone[path[i], path[i+1]] += self.Q/path_length
                pheromone[path[-1], path[0]] += self.Q/path_length
        
        print('best path index:')
        print(best_path)
        best_path_id_p = [self.points_df.iloc[i, 0] for i in best_path]
        print('best path id_p:')
        print(best_path_id_p)
        print('best path length:')
        print(best_path_length)


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