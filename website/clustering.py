import sys
import pandas as pd
import numpy as np
from json import dumps
from utils import init_db, close_db


def process_command_line_arguments(arguments):
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


def cluster_nearest_node(max_pall, max_lbs, origin, points=None, file_name=None, db_path=None, con=None, to_csv=None, set_name=None) -> None:
    if points is None:
        points = pd.read_csv(file_name, header=None)
    
    if db_path is not None and con is None:
        con = init_db(db_path)

    points_chosen = points.iloc[:, 0].values
    flatten_chosen = points_chosen.flatten().astype(str)
    points_chosen_str = ', '.join([f"'{item}'" for item in flatten_chosen])

    cur = con.cursor()
    clusters = []
    discard = set()

    query_str = f"select id_2 from geo_permutations where id_1 = '{origin}' and id_2 in ({points_chosen_str}) order by distance desc"
    cur.execute(query_str)
    perm_rows = [row[0] for row in cur.fetchall()]

    for current_point in perm_rows:
        sum_pall = 0
        sum_lbs = 0
        if current_point in discard:
            continue

        sum_pall, sum_lbs = get_geo_point_volume(current_point, cur)
        cluster = [current_point]
        discard.add(current_point)

        while True:
            nearest = get_geo_nearest(current_point, origin, cluster, clusters, cur)
            if nearest is not None:
                pall, lbs = get_geo_point_volume(nearest, cur)
            sum_pall += pall
            sum_lbs += lbs

            if sum_pall <= int(max_pall) and sum_lbs <= int(max_lbs) and nearest not in discard:
                if nearest is not None:
                    cluster.append(nearest)
                discard.add(nearest)
                current_point = nearest
            else:
                break

        if cluster:
            clusters.append(cluster)

    print('total clusters = ', len(clusters))
    print_clusters = dumps(clusters, indent=4)
    print(print_clusters)
    close_db(con)

    if to_csv == 'True' and file_name is not None and set_name is not None:
        cluster_to_csv(clusters, file_name, set_name)


def get_geo_point_volume(point_id, cur):
    query_str = 'select pall_avg, lbs_avg from geo_points where id = ' + "'" + point_id + "'"
    cur.execute(query_str)
    row = cur.fetchone()
    pall = row[0]
    lbs = row[1]

    return float(pall), float(lbs)


def get_geo_nearest(point_id, origin, cluster, clusters, cur):
    all_points = cluster + [item for sublist in clusters for item in sublist]

    all_points_set = set(all_points)

    points_str = ', '.join([f"'{item}'" for item in all_points_set])

    query_str = f"select id_2 from geo_permutations where id_1 = '{point_id}' " \
                f"and distance = (select min(distance) from geo_permutations " \
                f"where id_1 = '{point_id}' and id_2 not in ({points_str}) and id_2 <> '{origin}')"

    cur.execute(query_str)
    row = cur.fetchone()
    nearest = row[0] if row else None

    return nearest


def cluster_to_csv(clusters, file_name, set_name) -> None:
    rows = []
    for cluster_id, subarray in enumerate(clusters, start=1):
        for point in subarray:
            row = {
                'dvrp_id': set_name,
                'cluster_id': cluster_id,
                'cluster_name': f'Tractor{cluster_id}',
                'point': point,
                'sequence': np.nan
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(file_name+'clusters.csv', index=False, header=False, na_rep='')


functions = {
    "cluster_nearest_node": cluster_nearest_node,
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