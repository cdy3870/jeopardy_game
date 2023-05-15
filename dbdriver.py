import psycopg2
from queries import create_schema, delete_tables, create_clue_table
import pandas.io.sql as psql

class DBDriver:
	def __init__(self, host, name, user, password):
		self.conn = psycopg2.connect(f"host={host} dbname={name} user={user} password={password}")
		self.curr = self.conn.cursor()

	def execute_query(self, query):
		self.curr.execute(query)

	def show_data(self):
		# dataframe = psql.read_sql(
		#     "SELECT * FROM jeopardy.clues", self.conn)
		dataframe = psql.read_sql(
		    "SELECT * FROM jeopardy.games", self.conn)		
		print(dataframe)	

	def setup(self):
		self.execute_query(create_schema)
		self.execute_query(delete_tables)
		self.execute_query(create_clue_table)
		self.execute_query(create_game_table)