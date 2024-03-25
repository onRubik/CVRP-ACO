from sqlalchemy import event
import json
import random
import sys
from typing import Any, Tuple, Dict


def process_command_line_arguments(arguments):
    """Converts a list of 'key=value' strings into a dictionary."""
    kwargs = {}
    for argument in arguments:
        key_value = argument.split('=')
        if len(key_value) == 2:
            key, value = key_value
            kwargs[key] = value
    return kwargs


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


functions = {
    "resize_geo_points": resize_geo_points
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