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
    point CHAR    PRIMARY KEY
                  NOT NULL,
    x     DECIMAL NOT NULL,
    y     DECIMAL NOT NULL
);

CREATE TABLE stage_points (
    point CHAR    PRIMARY KEY
                  NOT NULL,
    x     DECIMAL NOT NULL,
    y     DECIMAL NOT NULL
);
