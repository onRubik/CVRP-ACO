CREATE TABLE permutation_distance (
    perm     CHAR    PRIMARY KEY
                     NOT NULL,
    x2       DECIMAL NOT NULL,
    x1       DECIMAL NOT NULL,
    y2       DECIMAL NOT NULL,
    y1       DECIMAL NOT NULL,
    distance DECIMAL NOT NULL
);

CREATE TABLE stage_permutation_distance (
    perm     CHAR    PRIMARY KEY
                     NOT NULL,
    x2       DECIMAL NOT NULL,
    x1       DECIMAL NOT NULL,
    y2       DECIMAL NOT NULL,
    y1       DECIMAL NOT NULL,
    distance DECIMAL NOT NULL
);

CREATE TABLE points (
    point   CHAR    PRIMARY KEY
                    NOT NULL,
    x       DECIMAL NOT NULL,
    y       DECIMAL NOT NULL,
    pallets INTEGER,
    weight  DECIMAL
);

CREATE TABLE stage_points (
    point   CHAR    PRIMARY KEY
                    NOT NULL,
    x       DECIMAL NOT NULL,
    y       DECIMAL NOT NULL,
    pallets INTEGER,
    weight  DECIMAL
);

CREATE TABLE ors_call_log (
    utc_date           INTEGER PRIMARY KEY
                               NOT NULL,
    utc_from_timestamp TEXT    NOT NULL,
    remaining_quota    INTEGER NOT NULL,
    utc_reset          INTEGER NOT NULL,
    utc_reset_readable TEXT    NOT NULL,
    response_status    INTEGER
);

CREATE TABLE geo_permutations (
    perm          TEXT PRIMARY KEY
                       NOT NULL,
    id_1          TEXT NOT NULL,
    id_2          TEXT NOT NULL,
    name_1        TEXT,
    name_2        TEXT,
    coordinates_1 TEXT NOT NULL,
    coordinates_2 TEXT NOT NULL
);

CREATE TABLE stage_geo_permutations (
    perm          TEXT PRIMARY KEY
                       NOT NULL,
    id_1          TEXT NOT NULL,
    id_2          TEXT NOT NULL,
    name_1        TEXT,
    name_2        TEXT,
    coordinates_1 TEXT NOT NULL,
    coordinates_2 TEXT NOT NULL
);

CREATE TABLE geo_permutations_distance (
    perm          TEXT PRIMARY KEY
                       NOT NULL,
    id_1          TEXT NOT NULL,
    id_2          TEXT NOT NULL,
    name_1        TEXT,
    name_2        TEXT,
    coordinates_1 TEXT NOT NULL,
    coordinates_2 TEXT NOT NULL,
    distance      NUMERIC NOT NULL
);