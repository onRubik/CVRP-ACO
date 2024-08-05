import sqlite3
import pandas as pd
import numpy as np
import random
import sys
import csv
import matplotlib.pyplot as plt
from tqdm import trange


def process_command_line_arguments(arguments):
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


class AntColonyOptimization:
    def __init__(self, input_path, db_path, origin, n_ants, n_best, n_iterations, decay, max_pallets, max_weight, alpha=1, beta=1):
        self.input_path = input_path
        self.db_path = db_path
        self.origin = str(origin)
        self.n_ants = int(n_ants)
        self.n_best = int(n_best)
        self.n_iterations = int(n_iterations)
        self.decay = float(decay)
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.max_pallets = int(max_pallets)
        self.max_weight = int(max_weight)

    def load_data(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        
        with open(self.input_path, 'r') as in_file:
            reader = csv.reader(in_file)
            in_arr = []
            for row in reader:
                in_arr.append(row[0])

        cur.execute('create temporary table if not exists temp_items (item Text)')
        cur.execute('delete from temp_items')
        cur.executemany('insert into temp_items (item) values (?)', [(item,) for item in in_arr])
        
        # Load points data
        points_query = '''
            select *
            from geo_points
            where id_p in (select id_p from temp_items)
        '''
        points_df = pd.read_sql_query(points_query, con)
        
        # Load distances data
        distances_query = 'select * from geo_permutations'
        distances_df = pd.read_sql_query(distances_query, con)
        
        con.close()
        return points_df, distances_df

    def prepare_data(self, points_df, distances_df):
        self.desc_points = points_df[['id_p', 'pall_avg', 'lbs_avg']].values
        # print('desc_points:', self.desc_points)
        self.points = self.desc_points.copy()
        self.points[:,0] = np.arange(self.points.shape[0])
        # print('points:', self.points)
        self.origin_index = np.where(self.desc_points[:,0] == str(self.origin))[0][0]
        # print('origin_index:', self.origin_index)
        self.distances = distances_df.pivot(index='id_1', columns='id_2', values='distance').values
        self.coordinates = points_df[['lon', 'lat']].values  # Assuming 'x' and 'y' columns for coordinates
        self.pheromone = np.ones(self.distances.shape) / len(self.points)
        self.all_inds = range(len(self.points))

    def run(self):
        points_df, distances_df = self.load_data()
        self.prepare_data(points_df, distances_df)

        shortest_paths = []
        all_time_shortest_path = ("placeholder", np.inf)
        for i in trange(self.n_iterations):
            all_paths = self.gen_all_paths()
            print(all_paths)
            self.spread_pheromone(all_paths, self.n_best, shortest_paths)
            shortest_path = min(all_paths, key=lambda x: x[1])
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            self.pheromone *= self.decay
        print('all_time_shortest_path[0]:')
        print(all_time_shortest_path[0])
        print('all_time_shortest_path[1]:')
        print(all_time_shortest_path[1])
        # self.store_result(all_time_shortest_path[0], all_time_shortest_path[1])
        # self.visualize_routes(all_time_shortest_path[0])
        return all_time_shortest_path

    def spread_pheromone(self, all_paths, n_best, shortest_paths):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += 1.0 / self.distances[move]

    def gen_path_dist(self, path):
        total_dist = 0
        for ele in path:
            total_dist += self.distances[ele]
        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            paths = self.gen_paths(self.origin_index)
            for path in paths:
                all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_paths(self, start):
        all_paths = []
        path = []
        visited = set()
        visited.add(start)
        prev = start
        current_pallets = 0
        current_weight = 0
        
        for _ in range(len(self.points) - 1):
            if current_pallets >= self.max_pallets or current_weight >= self.max_weight:
                path.append((prev, start))  # Return to origin
                all_paths.append(path)
                path = []
                current_pallets = 0
                current_weight = 0
                prev = start
            
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            if move is None:
                break
            
            current_pallets += self.points[move][1]
            current_weight += self.points[move][2]
            
            path.append((prev, move))
            prev = move
            visited.add(move)
        
        if path:
            path.append((prev, start))  # Return to origin
            all_paths.append(path)
        
        return all_paths

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        # norm_row = row / row.sum()
        norm_row = row / np.nansum(row)
        if norm_row.sum() == 0:
            return None
        norm_row = np.nan_to_num(norm_row, nan=0.0)
        move = np_choice(self.all_inds, 1, p=norm_row)[0]
        return move

    def store_result(self, path, distance):
        con = sqlite3.conect(self.db_path)
        cursor = con.cursor()
        
        # Insert result
        cursor.execute('''
        insert into dvrp_set (path, distance) VALUES (?, ?)
        ''', (str(path), distance))
        
        con.commit()
        con.close()

    def visualize_routes(self, paths):
        colors = plt.cm.get_cmap('hsv', len(paths))

        for idx, path in enumerate(paths):
            x_coords = [self.coordinates[move[0]][0] for move in path] + [self.coordinates[path[-1][1]][0]]
            y_coords = [self.coordinates[move[0]][1] for move in path] + [self.coordinates[path[-1][1]][1]]
            plt.plot(x_coords, y_coords, color=colors(idx))
        
        for point in self.points:
            plt.scatter(self.coordinates[point[0]][0], self.coordinates[point[0]][1], label=f'ID {point[0]}')
        
        plt.legend()
        plt.title('Vehicle Routing Problem - ACO Solution')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.show()


# Utility function
def np_choice(a, size, p):
    return np.random.choice(a, size=size, p=p)


functions = {
    'run_aco': lambda **kwargs: AntColonyOptimization(**kwargs).run()
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
