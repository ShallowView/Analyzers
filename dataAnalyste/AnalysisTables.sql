-- Reset already existing tables
drop table if exists wr_color;
drop table if exists wr_title;
drop table if exists avg_elo_opening;

create table if not exists wr_color
(
  result CHAR(1) CHECK (result IN ('W', 'B', 'D')),
  count INTEGER,
  win_rate float8
);

create table if not exists wr_title
(
  title TEXT,
  win_rate float8
);

create table if not exists avg_elo_opening
(
  opening UUID references openings (id),
  avg_elo float8
);

ALTER TABLE wr_color
  OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally
ALTER TABLE wr_title
  OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally
ALTER TABLE avg_elo_opening
  OWNER TO SVCollaborator; -- Don't run this if you're creating the tables locally