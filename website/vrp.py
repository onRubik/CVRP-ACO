import sys
from tqdm import trange
import numpy as np
import pandas as pd
import ast
import matplotlib.pyplot as plt
from utils import init_db, close_db


def process_command_line_arguments(arguments):
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


def dvrp_sql_ants_distance(points, current_point, item, cur, next_point):
    if next_point == False:
        point_state = item
    else:
        point_state = next_point

    query_str = 'select distance from geo_permutations where id_1 = '+"'"+str(points.loc[current_point, 'id'])+"'"+' and id_2 = '+"'"+str(points.loc[point_state, 'id'])+"'"

    for row in cur.execute(query_str):
        segment_distance = row[0]
    
    return segment_distance


def dvrp_sql_ants_return_distance(points_copy, route, cur):
    query_str = 'select distance from geo_permutations where id_1 = '+"'"+str(points_copy.loc[route[-2], ['id']].iloc[0])+"'"+' and id_2 = '+"'"+str(points_copy.loc[route[-1], ['id']].iloc[0])+"'"

    for row in cur.execute(query_str):
        segment_distance = row[0]
    
    return segment_distance


def sql_get_coordinates(point: str, cur):
    sql_table_name = 'geo_points'
    query_str = 'select coordinates from ' + sql_table_name + ' where id = '+"'"+str(point[0])+"'"
    for row in cur.execute(query_str):
        coordinates = row[0]
    return coordinates


def dvrp_ant_colony_algorithm(points, cur, route_output_fix, progress_output_fix, csv_output_fix, ants_iterations, ants_alpha, ants_beta, ants_evaporation_rate, ants_Q):
    points_len = len(points)
    points_copy = points.copy()
    pheromone = np.ones((points_len, points_len))
    best_route = []
    best_route_distance = np.inf

    # cur = con.cursor()
    selected_columns = ['id']
    points = points[selected_columns].values
    points = pd.DataFrame(points, columns=selected_columns)
    # points = points.iloc[:, 3]

    progress = []
    ants_n = points_len

    for i in trange(0, ants_iterations):
        routes = []
        routes_len = []

        for i in range(ants_n):
            visited = [False] * points_len
            current_point = np.random.randint(points_len)
            visited[current_point] = True
            route = [current_point]
            route_len = 0

            while False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                odds = np.zeros(len(unvisited))

                for i, item in enumerate(unvisited):
                    segment_distance = dvrp_sql_ants_distance(points, current_point, item, cur, next_point=False)

                    odds[i] = pheromone[current_point, item] ** ants_alpha / (segment_distance ** ants_beta)

                odds /= np.sum(odds)
                next_point = np.random.choice(unvisited, p=odds)
                route.append(next_point)
                route_len += dvrp_sql_ants_distance(points, current_point, item, cur, next_point)
                    
                visited[next_point] = True
                current_point = next_point

            route = route + [route[0]]
            route_len += dvrp_sql_ants_return_distance(points_copy, route, cur)
            
            routes.append(route)
            routes_len.append(route_len)

            if route_len < best_route_distance:
                best_route = route
                best_route_distance = np.sum(route_len)
            
        progress.append(best_route_distance)

        pheromone *= ants_evaporation_rate

        for route_zip, route_len_zip in zip(routes, routes_len):
            for i in range(points_len-1):
                pheromone[route_zip[i], route_zip[i + 1]] += ants_Q / route_len_zip
            pheromone[route_zip[-1], route_zip[0]] += ants_Q / route_len_zip

    from_df = []
    for i in range(points_len+1):
        from_df.append(points_copy.loc[best_route[i], ['point']])

    x = [] # longitud
    y= [] # latitud
    coordinates = []
    for item in from_df:
        coordinate_str = sql_get_coordinates(item, cur)
        coordinate = ast.literal_eval(coordinate_str.strip())
        x.append(coordinate[0])
        y.append(coordinate[1])
        coordinates.append(coordinate)
    
    df = pd.DataFrame(columns=['x','y'])
    df['x'] = x
    df['y'] = y
    df.to_csv(csv_output_fix, index=False)

    # if plot:
    plt.plot(progress)
    plt.ylabel('Distance')
    plt.xlabel('Iterations')
    plt.savefig(progress_output_fix)
    plt.show()

    # plt.plot(x,y,'o-', label='Cordinates')
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.savefig(route_output_fix)
    # plt.show()
    
    # print("Final distance: " + str(best_route_distance))
    # print('best_route = ', from_df)
    # return best_route_distance, from_df, coordinates
    return from_df, progress


def dvrp_loop_clusters(points=None, file_name=None, db_path=None, con=None) -> None:
    if points is None:
        points = pd.read_csv(file_name, header=None)
        points.columns = ['dvrp_id', 'cluster_id', 'cluster_name', 'point', 'sequence']

    if db_path is not None and con is None:
        con = init_db(db_path)
        cur = con.cursor()
    
    progress_res = []
    updated_points = points.copy()
    for cluster_id, group in points.groupby('cluster_id'):
        reorder_group, progress = dvrp_ant_colony_algorithm(points, cur, route_output_fix, progress_output_fix, csv_output_fix, ants_iterations, ants_alpha, ants_beta, ants_evaporation_rate, ants_Q)
        updated_points.loc[updated_points['cluster_id'] == cluster_id, 'point'] = reorder_group
        progress_res.append([progress])

    updated_points.to_csv(file_name+'dvrp.csv', index=False, header=False)


functions = {
    "dvrp_ant_colony_algorithm": dvrp_ant_colony_algorithm,
    "dvrp_loop_clusters": dvrp_loop_clusters
}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python my_script.py <function_name> key1=value1 key2=value2 ...")
        sys.exit(1)

    func_name = sys.argv[1]
    kwargs = process_command_line_arguments(sys.argv[2:])

    if func_name in functions:
        functions[func_name](**kwargs)
    else:
        print(f"No function named '{func_name}' found.")