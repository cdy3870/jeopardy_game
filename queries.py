create_schema = """CREATE SCHEMA IF NOT EXISTS jeopardy;"""

delete_tables = """
DROP TABLE IF EXISTS jeopardy.clues;
"""

create_clue_table = """
CREATE TABLE IF NOT EXISTS jeopardy.clues (
	clue_id INT PRIMARY KEY,
	game_id INT,
	value INT,
	daily_double BOOL,
	round VARCHAR(10),
	category VARCHAR(1000),
	clue VARCHAR(1000),
	response VARCHAR(1000)
);
"""

insert_clues = """INSERT INTO jeopardy.clues VALUES ({}, {}, {}, {}, '{}', '{}', '{}', '{}');"""


create_game_table = """
CREATE TABLE IF NOT EXISTS jeopardy.games (
	game_id INT PRIMARY KEY,
	episode_num INT,
	season_id INT,
	air_date VARCHAR(20),
	notes VARCHAR(1000),
	contestant1 INT,
	contestant2 INT,
	contestant3 INT,
	winner INT,
	score1 INT,
	score2 INT,
	score3 INT
);
"""

delete_game_table = """
DROP TABLE IF EXISTS jeopardy.games;
"""


insert_games = """INSERT INTO jeopardy.games VALUES ({}, {}, {}, '{}', '{}', {}, {}, {}, {}, {}, {}, {});"""
