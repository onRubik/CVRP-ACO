# source: https://induraj2020.medium.com/implementation-of-ant-colony-optimization-using-python-solve-traveling-salesman-problem-9c14d3114475
# medium: Implementing Ant colony optimization in python- solving Traveling salesman problem

import sqlite3
import numpy as np
import pandas as pd
from tqdm import trange
import csv


def distance(point1, point2):
    # return np.sqrt(np.sum((point1 - point2)**2))
    pass

# origin = way/1180028681
def ant_colony_optimization(in_file, db_path, origin, max_pall, max_lbs, n_ants, n_iterations, alpha, beta, evaporation_rate, Q):
    points = None
    with open(in_file, 'r') as r:
        reader = csv.reader(r)
        in_points = []
        for row in reader:
            in_points.append(row[0])

    con = sqlite3.connect(db_path)
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

    points_df = pd.read_sql_query(points_query, con)
    print(points_df)

    n_points = len(points_df)
    print('n_points:', n_points)
    pheromone = np.ones((n_points, n_points))
    best_path = None
    best_path_length = np.inf
    
    for iteration in trange(n_iterations):
        paths = []
        path_lengths = []
        
        for ant in range(n_ants):
            visited = [False]*n_points
            current_point = np.random.randint(n_points)
            visited[current_point] = True
            path = [current_point]
            path_length = 0
            
            while False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                probabilities = np.zeros(len(unvisited))
                
                for i, unvisited_point in enumerate(unvisited):
                    probabilities[i] = pheromone[current_point, unvisited_point]**alpha / distance(points[current_point], points[unvisited_point])**beta
                
                probabilities /= np.sum(probabilities)
                
                next_point = np.random.choice(unvisited, p=probabilities)
                path.append(next_point)
                path_length += distance(points[current_point], points[next_point])
                visited[next_point] = True
                current_point = next_point
            
            paths.append(path)
            path_lengths.append(path_length)
            
            if path_length < best_path_length:
                best_path = path
                best_path_length = path_length
        
        pheromone *= evaporation_rate
        
        for path, path_length in zip(paths, path_lengths):
            for i in range(n_points-1):
                pheromone[path[i], path[i+1]] += Q/path_length
            pheromone[path[-1], path[0]] += Q/path_length
    
    print('best path:')
    print(best_path)
    print('best path length:')
    print(best_path_length)

    
# Example usage:
points = np.random.rand(10, 3) # Generate 10 random 3D points
ant_colony_optimization(in_file='input.csv', db_path='instance/vrp_db.db', origin='way/1180028681', max_pall=None, max_lbs=None, n_ants=10, n_iterations=100, alpha=1, beta=1, evaporation_rate=0.5, Q=1)