from .models import db, DVRPSet
from sqlalchemy import event


def generate_unique_point(mapper, connection, target):
    existing_points = set()
    query = connection.execute(f"SELECT point FROM dvrp_set WHERE dvrp_id = '{target.dvrp_id}'")
    for row in query:
        existing_points.add(row[0])

    point = target.point
    i = 1
    while point in existing_points:
        point = f"{i}.{target.point}"
        i += 1

    target.point = point

@event.listens_for(DVRPSet, 'before_insert')
def before_insert_generate_unique_point(mapper, connection, target):
    generate_unique_point(mapper, connection, target)

