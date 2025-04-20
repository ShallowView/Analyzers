-- Reset already existing tables
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS opening;

-- Create the player table
CREATE TABLE IF NOT EXISTS player (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    title VARCHAR(10),
    max_elo INT
);

-- Create the opening table
CREATE TABLE IF NOT EXISTS opening (
    id UUID PRIMARY KEY,
    eco VARCHAR(3) NOT NULL,
    name VARCHAR(100) NOT NULL,
    pgn TEXT NOT NULL
);

-- Create the game table
CREATE TABLE IF NOT EXISTS game (
    id UUID PRIMARY KEY,
    white UUID NOT NULL REFERENCES player(id),
    black UUID NOT NULL REFERENCES player(id),
    result CHAR(1) CHECK (result IN ('W', 'B', 'D')),
    white_elo INT,
    black_elo INT,
    date_time TIMESTAMP,
    time_control VARCHAR(50),
    opening UUID REFERENCES opening(id)
);