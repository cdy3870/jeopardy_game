import streamlit as st
from dbdriver import DBDriver
import pandas.io.sql as psql
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Info About Stored Games")

@st.cache_data()
def get_clues(_db):
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues", _db.conn)	

	return test_df

@st.cache_data()
def get_games(_db):
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.games", _db.conn)	

	return test_df

@st.cache_data()
def get_info(games, clues):
	earliest_date = games["air_date"].min()
	latest_date = games["air_date"].max()
	length = len(games)
	num_clues = len(clues)
	num_unique = len(clues["category"].unique())

	info_df = pd.DataFrame({"Date Range": [f"{earliest_date} - {latest_date}"],
							"Total Games": [length], "Total Clues": [num_clues],
							 "Total Categories": [num_unique]})

	return info_df

def get_cat_dist(df):

	df = df["category"].value_counts().reset_index(name='count').rename({"index": "category"}, axis=1).iloc[:10]
	fig = px.bar(df, x="category", y="count", title="Clue Counts for Top 10 Most Frequent Categories")

	return fig

def get_score_over_time(df):
	print(df["air_date"])	
	test_df = df.copy()
	test_df["winner score"] = df[["score1", "score2", "score3"]].max(axis=1)

	fig = px.line(test_df, x="air_date", y="winner score", title="Winner Score Over Time")

	return fig


def main():
	db = DBDriver(host="drona.db.elephantsql.com", name="hvkogzmy",
				  user="hvkogzmy", password="TqgdVBnft1hXRg7_oG73QZriwst4_BLA")


	clues = get_clues(db)
	games = get_games(db)
	info_df = get_info(games, clues)
	# col1, col2, col3 = st.columns(3)

	# col1.write("Basic information: ")

	info_df


	bar = get_cat_dist(clues)
	st.plotly_chart(bar)


	line = get_score_over_time(games)
	st.plotly_chart(line)


if __name__ == "__main__":
	main()