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
