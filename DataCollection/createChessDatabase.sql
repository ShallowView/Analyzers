-- Reset already existing tables
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS openings;

-- Create the players table
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(10),
    max_elo INT
);
ALTER TABLE players OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally

-- Create the openings table
CREATE TABLE IF NOT EXISTS openings (
    id UUID PRIMARY KEY,
    eco VARCHAR(3) NOT NULL,
    name VARCHAR(100) NOT NULL,
    pgn TEXT NOT NULL,
    UNIQUE (name, pgn)
);
ALTER TABLE openings OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally

-- Create the games table
CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY,
    white UUID NOT NULL REFERENCES players(id),
    black UUID NOT NULL REFERENCES players(id),
    result CHAR(1) CHECK (result IN ('W', 'B', 'D')),
    white_elo INT,
    black_elo INT,
    date_time TIMESTAMP,
    time_control VARCHAR(50),
    opening UUID REFERENCES openings(id),
    UNIQUE (white, black, date_time)
);
ALTER TABLE games OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally

-- Create the function to update the max_elo field in the players table
CREATE OR REPLACE FUNCTION update_players_max_elo()
RETURNS void AS $$
BEGIN
    UPDATE players
    SET max_elo = subquery.max_elo
    FROM (
        SELECT id, MAX(max_elo) AS max_elo
        FROM (
            SELECT players.id, MAX(games.white_elo) AS max_elo
            FROM games
            JOIN players ON players.id = games.white
            GROUP BY players.id

            UNION

            SELECT players.id, MAX(games.black_elo) AS max_elo
            FROM games
            JOIN players ON players.id = games.black
            GROUP BY players.id
        ) AS combined
        GROUP BY id
    ) AS subquery
    WHERE players.id = subquery.id;
END;
$$ LANGUAGE plpgsql;