import sqlite3
import json
import csv
import pandas as pd
from itertools import permutations
import time
import tqdm
import random
import sys
from os import environ
import urllib3


# When using a Unix/linux OS or linux linke terminal the path for argument "file_name" needs to be as "file_name=~/<complete_path_of_parent_folder>/<your_file_name>"
# When using a Windows OS or Windows linke terminal the path for argument "file_name" needs to be as "file_name=C:\<complete_path_of_parent_folder>\<your_file_name>"


def process_command_line_arguments(arguments):
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


def init_db(db_path):
    con = sqlite3.connect(db_path)
    
    return con


def close_db(con) -> None:
    con.close()


# from raw .geojson data downloaded from overpass-turbo, use resize_geo_points to reduce the bulk data
# NOTICE: points to be kept are choosen with random.shuffle
def resize_geo_points(reduced_size, file_name) -> None:
    reduced_size = int(reduced_size)

    with open(file_name, 'r', encoding='utf-8') as geojson_file:
        data = json.load(geojson_file)

    selected_points = []

    for feature in data.get('features', []):
        if feature.get('geometry', {}).get('type') == 'Point':
            selected_points.append(feature)

    random.shuffle(selected_points)
    selected_points = selected_points[:reduced_size]

    result_geojson = {
        "type": "FeatureCollection",
        "features": selected_points
    }

    with open(file_name+'_reduced.geojson', 'w', encoding='utf-8') as result_file:
        json.dump(result_geojson, result_file, indent=2)


def count_geo_keys(file_name) -> None:
    with open(file_name, 'r') as geojson_file:
        data = json.load(geojson_file)

    unique_ids = set()

    for feature in data.get('features', []):
        id_value = feature.get('id')
        if id_value:
            unique_ids.add(id_value)

    distinct_id_count = len(unique_ids)

    print('Number of unique IDs = ', distinct_id_count)


# converts geojson files (pre-resized) into filered json and csv files
def geojson_to_csv_and_json(file_name) -> None:
    with open(file_name, 'r') as geojson_file:
        geojson_data = json.load(geojson_file)

    point_features = [feature for feature in geojson_data['features'] if feature['geometry']['type'] == 'Point']

    points_csv = []
    points_json = {}

    for point in point_features:
        id_p = point['id']
        name = point['properties'].get('name', '')
        lat = point['geometry']['coordinates'][1]
        lon = point['geometry']['coordinates'][0]
        
        points_csv.append({
            'id_p': id_p,
            'name': name,
            'lat': lat,
            'lon': lon
        })

        points_json[id_p] = {
            'name': name,
            'lat': lat,
            'lon': lon
        }

    with open(file_name+'.csv', 'w', newline='') as csvfile:
        fieldnames = ['id_p', 'name', 'lat', 'lon']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points_csv)

    with open(file_name+'.json', 'w') as jsonfile:
        json.dump(points_json, jsonfile, indent=4)


def geo_points_update(file_name, db_path) -> None:
    con = init_db(db_path)
    cur = con.cursor()
    points = pd.read_csv(file_name)

    for row in cur.execute('''
        select
        case
            when exists (select 1 from stage_geo_points)
            then 1
            else 0
        end
    '''):
        print(int(row[0]))

    if int(row[0]) == 1:
        cur.execute('delete from stage_geo_points')
        con.commit()
        print('stage_geo_points table cleared')

    points = points.drop('index', axis=1)
    points = points.set_index('id')
    points.to_sql('stage_geo_points', con, if_exists='append', index_label='id')
    con.commit()
    print('stage_geo_points table updated')

    cur.execute('''
        insert into geo_points(id, name, coordinates, delivery_freq_per_week, pall_avg, lbs_avg)
        select *
        from stage_geo_points
        where id not in (
            select id
            from geo_points
        )
    ''')
    con.commit()
    print('geo_points table updated')
    close_db(con)


def freq_geo_points(db_path) -> None:
    con = init_db(db_path)
    cur = con.cursor()

    cur.execute('''
            select id
            from geo_points
            where delivery_freq_per_week is null
        ''')
    rows = cur.fetchall()

    if rows is None:
        print('no rows found')
        return None
    
    rows_count = len(rows)

    for row in rows:
        if random.random() <= 0.2:
            delivery_freq_per_week = random.choice([5, 7])
        else:
            delivery_freq_per_week = random.choice([1, 3])
        cur.execute('''
                update geo_points
                set delivery_freq_per_week = ?
                where id = ?     
        ''', (delivery_freq_per_week , row[0]))

    con.commit()
    print('rows updated = ' + str(rows_count))
    close_db(con)


def pall_lbs_geo_points(db_path) -> None:
    con = init_db(db_path)
    cur = con.cursor()

    cur.execute('''
            select id
            from geo_points
            where pall_avg is null
            and lbs_avg is null
        ''')
    rows = cur.fetchall()

    if rows is None:
        print('no rows found')
        return None
    
    rows_count = len(rows)

    for row in rows:
        if random.random() <= 0.2:
            pall_avg = random.randint(9, 15)
        else:
            pall_avg = random.randint(1, 8)
        lbs_avg = round(pall_avg * random.uniform(1200, 1700), 6)
        cur.execute('''
                update geo_points
                set pall_avg = ?,
                    lbs_avg = ?
                where id = ?     
        ''', (pall_avg, lbs_avg, row[0]))

    con.commit()
    print('rows updated = ' + str(rows_count))
    close_db(con)


# saves the permutations from geojson file (pre-downsized)
def perm_from_geojson(file_name) -> None:
    with open(file_name, 'r') as geojson_file:
        geojson_data = json.load(geojson_file)

    point_features = [feature for feature in geojson_data['features'] if feature['geometry']['type'] == 'Point']

    perm_csv = []
    perm_json = {}
    index = 1

    for pair in permutations(point_features, 2):
        feature_0, feature_1 = pair
        id_1 = feature_0['id']
        id_2 = feature_1['id']
        name_1 = feature_0['properties'].get('name', '')
        name_2 = feature_1['properties'].get('name', '')
        coordinates_1 = feature_0['geometry']['coordinates']
        coordinates_2 = feature_1['geometry']['coordinates']
        
        perm_csv.append({
            'perm': id_1 + id_2,
            'index': index,
            'id_1': id_1,
            'id_2': id_2,
            'name_1': name_1,
            'name_2': name_2,
            'coordinates_1': coordinates_1,
            'coordinates_2': coordinates_2
        })

        perm_json[index] = {
            'perm': id_1 + id_2,
            'id_1': id_1,
            'id_2': id_2,
            'name_1': name_1,
            'name_2': name_2,
            'coordinates_1': coordinates_1,
            'coordinates_2': coordinates_2
        }

        index += 1

    with open(file_name+'_permutations.csv', 'w', newline='') as csvfile:
        fieldnames = ['index', 'perm', 'id_1', 'id_2', 'name_1', 'name_2', 'coordinates_1', 'coordinates_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(perm_csv)

    with open(file_name+'_permutations.json', 'w') as jsonfile:
        json.dump(perm_json, jsonfile, indent=4)


# updates DB with permutations csv file (pre-downsized)
def geo_perm_update(file_name, db_path) -> None:
    con = init_db(db_path)
    cur = con.cursor()
    points = pd.read_csv(file_name)

    for row in cur.execute('''
        select
        case
            when exists (select 1 from stage_geo_permutations)
            then 1
            else 0
        end
    '''):
        print(int(row[0]))

    if int(row[0]) == 1:
        cur.execute('delete from stage_geo_permutations')
        con.commit()
        print('stage_geo_permutations table cleared')

    points = points.drop('index', axis=1)
    points = points.set_index('perm')
    points.to_sql('stage_geo_permutations', con, if_exists='append', index_label='perm')
    con.commit()
    print('stage_geo_permutations table updated')

    cur.execute('''
        insert into geo_permutations(perm, id_1, id_2, name_1, name_2, coordinates_1, coordinates_2)
        select *
        from stage_geo_permutations
        where perm not in (
            select perm
            from geo_permutations
        )
    ''')
    con.commit()
    print('geo_permutations table updated')
    close_db(con)


# in a unix/linux like OS set the api key like:
# export ORS_API_KEY="your api key"
#
# in a Windows OS set the api key like:
# $env:ORS_API_KEY = "your api key"
def get_ors_rate_limit(ORS_API_KEY=None, db_path=None, con=None, cur=None):
    ad_hoc = False
    if con is None:
        con = init_db(db_path)
        cur = con.cursor()
        ad_hoc = True
    
    if ORS_API_KEY is None:
        api_key = environ.get(ORS_API_KEY)
    else:
        api_key = ORS_API_KEY

    http = urllib3.PoolManager()

    endpoint = 'https://api.openrouteservice.org/v2/directions/driving-hgv'
    
    # within this functions the start and end variables are hardcoded just to be able to use the driving-hgv call
    start = '-96.8100655,32.6949193'
    end = '-96.881694,33.2233456'
    
    url_string = f'{endpoint}?api_key={api_key}&start={start}&end={end}'

    r = http.request('GET', url_string, headers={'Content-Type': 'application/json'})
    
    if r.status == 200:
        # data = json.loads(r.data)
        
        if ('x-ratelimit-remaining' in r.headers) and ('x-ratelimit-reset' in r.headers):
            remaining_quota = int(r.headers['x-ratelimit-remaining'])

            cur.execute('''
                insert into ors_call_log (utc_date, utc_from_timestamp, remaining_quota, response_status)
                VALUES (
                    strftime('%s', 'now', 'utc'),
                    strftime('%Y-%m-%d %H:%M:%f', 'now', 'utc'),
                    ?,
                    ?
                )
            ''', (str(remaining_quota), str(200)))
            con.commit()
            if ad_hoc is True:
                    close_db(con)
            
            return remaining_quota
    else:
        cur.execute('''
            insert into ors_call_log (utc_date, utc_from_timestamp, response_status)
            VALUES (
                strftime('%s', 'now', 'utc'),
                strftime('%Y-%m-%d %H:%M:%f', 'now', 'utc'),
                ?
            )
        ''', (str(r.status)))
        con.commit()
        if ad_hoc is True:
                close_db(con)
        print('error: ', r.status)


def sql_ors_distances(api_var_name, db_path) -> None:
    con = init_db(db_path)
    cur = con.cursor()
    api_key = environ.get(api_var_name)
    remaining_quota = get_ors_rate_limit(ORS_API_KEY=api_key, db_path=None, con=con, cur=cur)
    print('remaining_quota = ' + str(remaining_quota))
    if remaining_quota > 50:
        delay = 60/40
        http = urllib3.PoolManager()
        endpoint = 'https://api.openrouteservice.org/v2/directions/driving-hgv'

        cur = con.cursor()

        for row in cur.execute('''
            select count(*)
            from geo_permutations
            where distance is null
        '''):
            print('rows missing distance = ' + str(int(row[0])))

        missing_distance = int(row[0])
        if missing_distance > 1950:
            max_get = remaining_quota - 50
        elif missing_distance <= 1950:
            max_get =  min(remaining_quota - 50, missing_distance)

        cur.execute('''
            select perm, coordinates_1, coordinates_2
            from geo_permutations 
            where distance is null
        ''')
        rows = cur.fetchall()

        with tqdm.tqdm(total=len(rows)) as pbar:
            counter = 0
            for row in rows:
                perm, coordinates_1, coordinates_2 = row
                coordinates_1 = coordinates_1.strip('[]')
                coordinates_2 = coordinates_2.strip('[]')
                distance = ors_fetch_distance(api_key, http, endpoint, coordinates_1, coordinates_2)
                if distance is not None:
                    cur.execute('''
                            update geo_permutations
                            set distance = ?
                            where perm = ?     
                    ''', (distance, perm))
                time.sleep(delay)
                counter += 1
                pbar.update(1)
                if counter == max_get: break
        
        con.commit()
        get_ors_rate_limit(ORS_API_KEY=api_key, db_path=None, con=con, cur=cur)
        close_db(con)
    else:
        print('remaining quota is too low')
        close_db(con)


def ors_fetch_distance(api_key, http, endpoint, coordinates_1, coordinates_2):
    url_string = f'{endpoint}?api_key={api_key}&start={coordinates_1}&end={coordinates_2}'
    r = http.request('GET', url_string, headers={'Content-Type': 'application/json'})
    if r.status == 200:
        data = json.loads(r.data)
        distance = data['features'][0]['properties']['segments'][0]['distance']
        return distance
    else:
        print('error: ', r.status)
        return None


functions = {
    "resize_geo_points": resize_geo_points,
    "count_geo_keys": count_geo_keys,
    "geojson_to_csv_and_json": geojson_to_csv_and_json,
    "geo_points_update": geo_points_update,
    "freq_geo_points": freq_geo_points,
    "pall_lbs_geo_points": pall_lbs_geo_points,
    "perm_from_geojson": perm_from_geojson,
    "geo_perm_update": geo_perm_update,
    "sql_ors_distances": sql_ors_distances,
    "get_ors_rate_limit": get_ors_rate_limit,
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