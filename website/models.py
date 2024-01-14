from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))


class GeoPermutations(db.Model):
    __tablename__ = 'geo_permutations'

    perm = db.Column(db.Text, primary_key=True, nullable=False)
    id_1 = db.Column(db.Text, nullable=False)
    id_2 = db.Column(db.Text, nullable=False)
    name_1 = db.Column(db.Text)
    name_2 = db.Column(db.Text)
    coordinates_1 = db.Column(db.Text, nullable=False)
    coordinates_2 = db.Column(db.Text, nullable=False)
    distance = db.Column(db.Numeric)


class GeoPoints(db.Model):
    __tablename__ = 'geo_points'

    id = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text)
    coordinates = db.Column(db.Text, nullable=False)
    delivery_freq_per_week = db.Column(db.Numeric)
    pall_avg = db.Column(db.Integer)
    lbs_avg = db.Column(db.Numeric)


class ORSCallLog(db.Model):
    __tablename__ = 'ors_call_log'

    utc_date = db.Column(db.Integer, primary_key=True, nullable=False)
    utc_from_timestamp = db.Column(db.Text, nullable=False)
    remaining_quota = db.Column(db.Integer)
    utc_reset = db.Column(db.Integer)
    utc_reset_readable = db.Column(db.Text)
    response_status = db.Column(db.Integer)


class ORSDirectionsGeoJSONPost(db.Model):
    __tablename__ = 'ors_directions_geojson_post'

    utc_date = db.Column(db.Integer, primary_key=True, nullable=False)
    utc_from_timestamp = db.Column(db.Text, nullable=False)
    batch_identifier = db.Column(db.Text, unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)
    distance_algorithm = db.Column(db.Numeric, nullable=False)
    distance_pre_load = db.Column(db.Numeric, nullable=False)
    distance_after_load = db.Column(db.Numeric)


class StageGeoPermutations(db.Model):
    __tablename__ = 'stage_geo_permutations'

    perm = db.Column(db.Text, primary_key=True, nullable=False)
    id_1 = db.Column(db.Text, nullable=False)
    id_2 = db.Column(db.Text, nullable=False)
    name_1 = db.Column(db.Text)
    name_2 = db.Column(db.Text)
    coordinates_1 = db.Column(db.Text, nullable=False)
    coordinates_2 = db.Column(db.Text, nullable=False)


class StageGeoPoints(db.Model):
    __tablename__ = 'stage_geo_points'

    id = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text)
    coordinates = db.Column(db.Text, nullable=False)
    delivery_freq_per_week = db.Column(db.Numeric)
    pall_avg = db.Column(db.Integer)
    lbs_avg = db.Column(db.Numeric)


class DVRPSet(db.Model):
    __tablename__ = 'dvrp_set'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dvrp_id = db.Column(db.Text, nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    cluster_name = db.Column(db.Text, nullable=False)
    point = db.Column(db.Text, nullable=False)

class DVRPOrigin(db.Model):
    __tablename__ = 'dvrp_origin'

    dvrp_id = db.Column(db.Text, primary_key=True, nullable=False)
    dvrp_origin = db.Column(db.Text, nullable=False)

    def __init__(self, dvrp_id, dvrp_origin):
        self.dvrp_id = dvrp_id
        self.dvrp_origin = dvrp_origin