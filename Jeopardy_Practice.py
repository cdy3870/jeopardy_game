from clue import Clue
from dbdriver import DBDriver
from queries import insert_clues, insert_games
import streamlit as st
import pandas.io.sql as psql
import pandas as pd
import random
import time
import asyncio
from datetime import datetime
from PIL import Image
from game import Game
from pages.Grouping_Jeopardy_Categories import get_classified_cats, get_all_results, get_confidence_charts

st.set_page_config(
	page_title="Jeopardy Practice",
	layout="wide",
	page_icon="🔥"
)

st.markdown("<h1 style='text-align: center'> Jeopardy Practice </h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center'> Test your trivia knowledge with over 500 old Jeopardy games. </p>", unsafe_allow_html=True)

broad_categories = ["science", "history", "sports",
					"literature", "movies and tv", "music",
					"geography", "word play", "religion"]

value_map = {200: 1, 400: 2, 600: 3, 800: 4, 1000: 5}

@st.cache_resource
def setup_db(reset, host="localhost", name="jeopardydb", user="calvinyu", password="password"):
	db = DBDriver(host=host, name=name, user=user, password=password)

	if reset:
		db.setup()

	return db

def get_insert_query(offset, n_clues):
	clues = Clue(offset, n_clues)
	clues_data = clues._get_clues()["data"]
	query_list = []
	for clue in clues_data:
		query_list.append(insert_clues.format(clue["id"], clue["game_id"], clue["value"], clue["daily_double"],
											 clue["round"].replace("'", "''"), clue["category"].replace("'", "''"),
											 clue["clue"].replace("'", "''"), clue["response"].replace("'", "''")))
	insert_query = "BEGIN; \n" + '\n'.join(query_list) + "\nCOMMIT;"	

	return insert_query


def get_insert_query_game(game_ids):
	games = Game(game_ids)
	game_data = games._get_games_from_ids()
	query_list = []
	for game in game_data:
		query_list.append(insert_games.format(game["id"], game["episode_num"], game["season_id"], game["air_date"],
											 game["notes"].replace("'", "''"), game["contestant1"],
											 game["contestant2"], game["contestant3"],
											 game["winner"], game["score1"], game["score2"], game["score3"]))
	insert_query = "BEGIN; \n" + '\n'.join(query_list) + "\nCOMMIT;"	
	print(insert_query)
	return insert_query

def store_games(db, number_of_games):
	i = 0
	while i < number_of_games * 60:
		insert_query = get_insert_query(i, 60)
		db.execute_query(insert_query)
		i += 60

def store_game_info(db):
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues", db.conn)

	game_ids = list(sorted(test_df["game_id"].unique()))

	queries = get_insert_query_game(game_ids)

	db.execute_query(queries)


def get_game(_conn):
	game_numbers = list(range(1, 51))
	random_game = random.randint(1, 51)
	dataframe = psql.read_sql(
	f"SELECT * FROM jeopardy.clues WHERE game_id = {random_game}", _conn)
	
	df = dataframe.drop(["clue_id", "game_id"], axis=1)
	return df

@st.cache_data
def extract_categories(df):
	j_round_cats = df[df["round"] == "J!"]["category"].unique()
	dj_round_cats = df[df["round"] == "DJ!"]["category"].unique()

	categories = pd.DataFrame({"Category": j_round_cats, "Double Jeopardy Category": dj_round_cats})

	return categories

@st.cache_data
def get_clue_numbers(_num):
	clue_numbers = list(range(1, _num))
	random.shuffle(clue_numbers)
	return clue_numbers

def update_num_correct():
	st.session_state.num_correct += 1
	st.session_state.pressed_correct = True	


def get_confidence_charts_helper(df, index):
	all_results = get_all_results()
	updated_results = {item["sequence"]:item for item in all_results}
	conf_chart = get_confidence_charts(updated_results[df.iloc[index]["category"]])
	return conf_chart

async def watch(ts):
	with st.empty():
		while ts:
			# test.markdown(
			# 	f"""
			# 	<p class="time">
			# 		{str(datetime.now())}
			# 	</p>
			# 	""", unsafe_allow_html=True)
			mins, secs = divmod(ts, 60)
			time_now = '{:02d}:{:02d}'.format(mins, secs)
			st.header(f"{time_now}")
			r = await asyncio.sleep(1)
			ts -= 1

@st.cache_data()
def get_top_categories(_db, num):
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues", _db.conn)
	top_categories = tuple(test_df["category"].value_counts()
						.reset_index(name='count').rename({"index": "category"}, axis=1).iloc[:num]["category"])

	return top_categories

def get_specific_category(category, db):
	query_string = ""
	for cat in category:

		query_string = query_string + "\'" + cat.replace("'","\"") + "' , "
	query_string = "(" + query_string[:-2] + ")"
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues WHERE category IN {query_string}", db.conn)

	return test_df


def main():
	db = setup_db(reset=False, host="drona.db.elephantsql.com", name="hvkogzmy",
				user="hvkogzmy", password="TqgdVBnft1hXRg7_oG73QZriwst4_BLA")


	top_categories = get_top_categories(db, 25)


	# store_games(db, 500)
	# store_game_info(db)
	

	# store_games(db, 50)
	if 'result' not in st.session_state:
		st.session_state.result = None
	if 'clue_number' not in st.session_state:
		st.session_state.clue_number = 0
	if 'total_clues' not in st.session_state:
		st.session_state.total_clues = 0
	if 'pressed_correct' not in st.session_state:
		st.session_state.pressed_correct = False
	if 'num_correct' not in st.session_state:
		st.session_state.num_correct = 0
	if 'difficulty' not in st.session_state:
		st.session_state.difficulty = {0:0, 1:0, 2:0, 3:0, 4:0}
	if 'in_cat' not in st.session_state:
		st.session_state.in_cat = False

	option = None
	group_type = None

	with st.sidebar:
		option = "Full Random Game"
		image = Image.open('image.png')

		st.image(image, width=300)

		add_radio = st.radio(
			"Choose mode",
			("Full Random Game", "By Category (Top 25)", "Grouped Categories Using NLP")
		)
		if add_radio == "By Category (Top 25)":
			option = st.selectbox("", top_categories)
			group_type = "top"

		if add_radio == "Grouped Categories Using NLP":
			option = st.selectbox("", [b.upper() for b in broad_categories])
			group_type = "broad"



	if option == "Full Random Game":
		col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
		_, new_col3, _ = st.columns(3)
		new_col1, new_col2 = st.columns(2)

		col7.write(f"Total correct: {st.session_state.num_correct}/{st.session_state.total_clues}")

		st.session_state.in_cat = False


		if col4.button("Reset Scores"):
			st.session_state.num_correct = 0
			st.session_state.total_clues = 0

		if col1.button("New Game"):
			try:
				st.session_state.clue_number = 1
				df = get_game(db.conn)
				print(df["value"].value_counts())

			finally:
				st.session_state.result = df

		clue_numbers = get_clue_numbers(59)

		if st.session_state.result is not None:
			df = st.session_state.result
			categories = extract_categories(df)
			new_col3.table(categories)


		if st.session_state.clue_number > 0 and st.button("Next Random Clue"):

			st.session_state.pressed_correct = False
			st.session_state.clue_number += 1
			st.session_state.total_clues += 1


			temp_result = None
			while temp_result is None:
				try:
					temp_result = df.loc[clue_numbers[st.session_state.clue_number]]	
					st.session_state.clue_number += 1		        
				except:
					 pass

			if st.session_state.clue_number == 59:
				st.write("All clues for game shown. Generate a new game to continue playing.")
				st.session_state.clue_number = 0

			value = df.loc[clue_numbers[st.session_state.clue_number]]["value"]
			if df.loc[clue_numbers[st.session_state.clue_number]]["round"] == "DJ!":
				difficulty_level = value_map[value/2]
			else:
				difficulty_level = value_map[value]

			new_col1.write(f"**Difficulty level:** {difficulty_level}/5")
			new_col1.write("**Category:** " + df.loc[clue_numbers[st.session_state.clue_number]]["category"])
			new_col1.write("**Clue:** " + df.loc[clue_numbers[st.session_state.clue_number]]["clue"])
			conf_chart = get_confidence_charts_helper(df, clue_numbers[st.session_state.clue_number])
			new_col2.table(conf_chart)
			
			st.session_state.temp = True

			


		if st.session_state.clue_number > 0 and not st.session_state.pressed_correct:
			placeholder = st.empty()
			isclick = placeholder.button("Show Answer")
			if isclick:
				new_col1.write("**Category:** " + df.loc[clue_numbers[st.session_state.clue_number]]["category"])
				new_col1.write("**Clue:** " + df.loc[clue_numbers[st.session_state.clue_number]]["clue"])
				new_col1.write("**Answer:** " + df.loc[clue_numbers[st.session_state.clue_number]]["response"])
				placeholder.empty()

				conf_chart = get_confidence_charts_helper(df, clue_numbers[st.session_state.clue_number])
				new_col2.table(conf_chart)	
				

				st.button("Correct", on_click=update_num_correct)

				st.session_state.temp = False


	else:
		if group_type == "broad":
			classified_cats = get_classified_cats()
			specific_cats = classified_cats[option.lower()]
			df = get_specific_category(specific_cats, db)
			length = len(df)


		elif group_type == "top":
			df = get_specific_category([option], db)
			length = len(df)


		clue_numbers = get_clue_numbers(length - 1)

		if not st.session_state.in_cat:
			st.session_state.clue_number = 0

		st.session_state.in_cat = True

		col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
		new_col1, new_col2 = st.columns(2)


		col1.write(f"Total clues: {length}")

		if col4.button("Reset Scores"):
			st.session_state.num_correct = 0
			st.session_state.total_clues = 0
		col7.write(f"Total correct: {st.session_state.num_correct}/{st.session_state.total_clues}")



		if st.session_state.clue_number > -1 and st.button("Next Random Clue"):



			st.session_state.pressed_correct = False
			st.session_state.clue_number += 1
			st.session_state.total_clues += 1

			if st.session_state.clue_number == length:
				# st.write("All clues for game shown. Generate a new game to continue playing.")
				st.session_state.clue_number = 0


			index = clue_numbers[st.session_state.clue_number]

			if index > length:
				index -= (index - length)
				index -= 1

			temp_result = None
			while temp_result is None:
				try:
					temp_result = df.loc[index]	
					st.session_state.clue_number += 1		        
				except:
					 pass

			value = df.iloc[index]["value"]
			if df.iloc[index]["round"] == "DJ!":
				difficulty_level = value_map[value/2]
			else:
				difficulty_level = value_map[value]


			new_col1.write(f"**Difficulty level**: {difficulty_level}/5")
			new_col1.write("**Category:** " + df.loc[index]["category"])
			new_col1.write("**Clue:** " + df.loc[index]["clue"])
			
			conf_chart = get_confidence_charts_helper(df, index)
			new_col2.table(conf_chart)



		if st.session_state.clue_number > -1 and not st.session_state.pressed_correct:
			placeholder = st.empty()
			isclick = placeholder.button("Show Answer")

			if isclick:
				index = clue_numbers[st.session_state.clue_number]

				if index > length:
					index -= (index - length)
					index -= 1

				new_col1.write("**Category:** " + df.loc[index]["category"])
				new_col1.write("**Clue:** " + df.loc[index]["clue"])
				new_col1.write("**Answer:** " + df.loc[index]["response"])
				placeholder.empty()
				conf_chart = get_confidence_charts_helper(df, index)
				new_col2.table(conf_chart)

				

				st.button("Correct", on_click=update_num_correct)





			
	# if st.session_state.temp:	
	# 	asyncio.run(watch(30))

if __name__ == "__main__":
	main()