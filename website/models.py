from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class GeoPoints(db.Model):
    __tablename__ = 'geo_points'

    id_p = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text)
    lat = db.Column(db.Numeric, nullable=False)
    lon = db.Column(db.Numeric, nullable=False)
    delivery_freq_per_week = db.Column(db.Numeric)
    pall_avg = db.Column(db.Integer)
    lbs_avg = db.Column(db.Numeric)


class StageGeoPoints(db.Model):
    __tablename__ = 'stage_geo_points'

    id_p = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text)
    lat = db.Column(db.Numeric, nullable=False)
    lon = db.Column(db.Numeric, nullable=False)
    delivery_freq_per_week = db.Column(db.Numeric)
    pall_avg = db.Column(db.Integer)
    lbs_avg = db.Column(db.Numeric)


class GeoPermutations(db.Model):
    __tablename__ = 'geo_permutations'

    perm = db.Column(db.Text, primary_key=True, nullable=False)
    id_1 = db.Column(db.Text, nullable=False)
    id_2 = db.Column(db.Text, nullable=False)
    name_1 = db.Column(db.Text)
    name_2 = db.Column(db.Text)
    lat_id_1 = db.Column(db.Numeric, nullable=False)
    lon_id_1 = db.Column(db.Numeric, nullable=False)
    lat_id_2 = db.Column(db.Numeric, nullable=False)
    lon_id_2 = db.Column(db.Numeric, nullable=False)
    distance = db.Column(db.Numeric)


class StageGeoPermutations(db.Model):
    __tablename__ = 'stage_geo_permutations'

    perm = db.Column(db.Text, primary_key=True, nullable=False)
    id_1 = db.Column(db.Text, nullable=False)
    id_2 = db.Column(db.Text, nullable=False)
    name_1 = db.Column(db.Text)
    name_2 = db.Column(db.Text)
    lat_id_1 = db.Column(db.Numeric, nullable=False)
    lon_id_1 = db.Column(db.Numeric, nullable=False)
    lat_id_2 = db.Column(db.Numeric, nullable=False)
    lon_id_2 = db.Column(db.Numeric, nullable=False)


class ORSCallLog(db.Model):
    __tablename__ = 'ors_call_log'

    utc_date = db.Column(db.Integer, primary_key=True, nullable=False)
    utc_from_timestamp = db.Column(db.Text, nullable=False)
    remaining_quota = db.Column(db.Integer)
    utc_reset = db.Column(db.Integer)
    utc_reset_readable = db.Column(db.Text)
    response_status = db.Column(db.Integer)


class DVRPSet(db.Model):
    __tablename__ = 'dvrp_set'

    id_set = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dvrp_id = db.Column(db.Text, nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    cluster_name = db.Column(db.Text, nullable=False)
    point = db.Column(db.Text, nullable=False)
    sequence = db.Column(db.Integer, nullable=True)

class DVRPOrigin(db.Model):
    __tablename__ = 'dvrp_origin'

    dvrp_id = db.Column(db.Text, primary_key=True, nullable=False)
    dvrp_origin = db.Column(db.Text, nullable=False)

    def __init__(self, dvrp_id, dvrp_origin):
        self.dvrp_id = dvrp_id
        self.dvrp_origin = dvrp_origin