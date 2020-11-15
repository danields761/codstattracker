CREATE TABLE players (
    db_id INTEGER NOT NULL,
    platform VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    nickname VARCHAR NOT NULL,
    PRIMARY KEY (db_id),
    UNIQUE (platform,id,nickname)
);
CREATE TABLE players_matches_stats (
    player_id INTEGER,
    id VARCHAR NOT NULL,
    game VARCHAR(5),
    start DATETIME NOT NULL,
    "end" DATETIME NOT NULL,
    map VARCHAR NOT NULL,
    is_win BOOLEAN NOT NULL,
    kills INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    kd_ratio FLOAT NOT NULL,
    killstreaks_used JSON NOT NULL,
    longest_streak INTEGER NOT NULL,
    suicides INTEGER NOT NULL,
    executions INTEGER NOT NULL,
    damage_dealt INTEGER NOT NULL,
    damage_received INTEGER NOT NULL,
    percent_time_moved FLOAT NOT NULL,
    shots_fired INTEGER NOT NULL,
    shots_missed INTEGER NOT NULL,
    headshots INTEGER NOT NULL,
    wall_bangs INTEGER NOT NULL,
    time_played DATETIME NOT NULL,
    distance_traveled FLOAT NOT NULL,
    average_speed FLOAT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(player_id) REFERENCES players (db_id),
    CONSTRAINT game CHECK (game IN ('mw_mp','mw_wz')),
    CHECK (is_win IN (0,1))
);
CREATE TABLE weapon_stats (
    id INTEGER NOT NULL,
    match_id VARCHAR,
    name VARCHAR NOT NULL,
    hits INTEGER NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    shots INTEGER NOT NULL,
    headshots INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(match_id) REFERENCES players_matches_stats (id)
);
CREATE TABLE br_stats (
    id INTEGER NOT NULL,
    match_id VARCHAR,
    teams_count INTEGER NOT NULL,
    players_count INTEGER NOT NULL,
    placement INTEGER NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (match_id),
    FOREIGN KEY(match_id) REFERENCES players_matches_stats (id)
);
