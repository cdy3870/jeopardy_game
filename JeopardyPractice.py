from clue import Clue
from dbdriver import DBDriver
from queries import insert_clues
import streamlit as st
import pandas.io.sql as psql
import pandas as pd
import random
import time
import asyncio
from datetime import datetime
from PIL import Image

st.set_page_config(
	page_title="Jeopardy Practice",
	layout="wide",
	page_icon="🔥"
)

st.markdown("# Jeopardy Practice")

st.write("Test your trivia knowledge with 500 old Jeopardy games.")

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

def store_games(db, number_of_games):
	i = 0
	while i < number_of_games * 60:
		insert_query = get_insert_query(i, 60)
		db.execute_query(insert_query)
		i += 60

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
def get_clue_numbers():
	clue_numbers = list(range(1, 61))
	random.shuffle(clue_numbers)
	return clue_numbers

def update_num_correct():
	st.session_state.num_correct += 1
	st.session_state.pressed_correct = True	


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

def main():
	db = setup_db(reset=False, host="drona.db.elephantsql.com", name="hvkogzmy",
				user="hvkogzmy", password="TqgdVBnft1hXRg7_oG73QZriwst4_BLA")

	# store_games(db, 500)
	
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues", db.conn)
	top_10_categories = tuple(test_df["category"].value_counts()
						.reset_index(name='count').rename({"index": "category"}, axis=1).iloc[:10]["category"])

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

	if 'temp' not in st.session_state:
		st.session_state.temp = True

	with st.sidebar:
		image = Image.open('image.png')

		st.image(image, width=300)

		add_radio = st.radio(
			"Choose mode",
			("Full Random Game", "Specific Category")
		)
		if add_radio == "Specific Category":
			option = st.selectbox("", top_10_categories)


	col1, col2, col3, col4 = st.columns(4)

	col3.write(f"Num correct: {st.session_state.num_correct}/{st.session_state.total_clues}")




	if col2.button("Reset Scores"):
		st.session_state.total_clues = 0

	if col1.button("Generate New Game"):
		try:
			st.session_state.clue_number = 1
			df = get_game(db.conn)
			print(df["value"].value_counts())

		finally:
			st.session_state.result = df

	clue_numbers = get_clue_numbers()

	if st.session_state.result is not None:
		df = st.session_state.result
		categories = extract_categories(df)
		categories


	if st.session_state.clue_number > 0 and st.button("Next Random Clue"):



		st.session_state.pressed_correct = False
		st.session_state.clue_number += 1
		st.session_state.total_clues += 1

		if st.session_state.clue_number == 61:
			# st.write("All clues for game shown. Generate a new game to continue playing.")
			st.session_state.clue_number = 0

		value = df.iloc[clue_numbers[st.session_state.clue_number]]["value"]
		if df.iloc[clue_numbers[st.session_state.clue_number]]["round"] == "DJ!":
			difficulty_level = value_map[value/2]
		else:
			difficulty_level = value_map[value]

		st.write(f"Difficulty level: {difficulty_level}/5")
		st.write("Category: " + df.iloc[clue_numbers[st.session_state.clue_number]]["category"])
		st.write("Clue: " + df.iloc[clue_numbers[st.session_state.clue_number]]["clue"])

		st.session_state.temp = True

		


	if st.session_state.clue_number > 0 and not st.session_state.pressed_correct:
		placeholder = st.empty()
		isclick = placeholder.button("Show Answer")
		if isclick:
			st.write("Category: " + df.iloc[clue_numbers[st.session_state.clue_number]]["category"])
			st.write("Clue: " + df.iloc[clue_numbers[st.session_state.clue_number]]["clue"])
			st.write("Answer: " + df.iloc[clue_numbers[st.session_state.clue_number]]["response"])
			placeholder.empty()

			col5, col6, col7, col8, col9, col10 = st.columns(6)
			

			col5.button("Correct", on_click=update_num_correct)

			st.session_state.temp = False
			
	# if st.session_state.temp:	
	# 	asyncio.run(watch(30))

if __name__ == "__main__":
	main()