import streamlit as st
from dbdriver import DBDriver
import pandas.io.sql as psql
import plotly.express as px
import pandas as pd
import pickle

st.set_page_config(page_title="Stored_Games_Overview", layout="wide")

st.markdown("<h1 style='text-align: center'> What Games Were Stored? </h1>", unsafe_allow_html=True)

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
	print(clues.head())

	earliest_date = games["air_date"].min()
	latest_date = games["air_date"].max()
	length = len(games)
	num_clues = len(clues)
	num_unique = len(clues["category"].unique())
	num_unique_cont = len(set(list(games["contestant1"].unique()) 
						+ list(games["contestant2"].unique())
						+ list(games["contestant1"].unique())))


	info_df = pd.DataFrame({"Date Range": [f"{earliest_date} - {latest_date}"],
							"Total Games": [length], "Total Clues": [num_clues],
							 "Total Categories": [num_unique], "Total Contestants": [num_unique_cont]})

	return info_df

def get_cat_dist(df):

	df = df["category"].value_counts().reset_index(name='count').rename({"index": "category"}, axis=1).iloc[:10]
	fig = px.bar(df, y="category", x="count", title="Top 10 Most Frequent Categories", orientation='h')
	fig.update_layout(yaxis=dict(autorange="reversed"))
	return fig

def get_cat_dist_low(df):

	df = df["category"].value_counts().reset_index(name='count').rename({"index": "category"}, axis=1).iloc[-10:]
	fig = px.bar(df, y="category", x="count", title="Bottom 10 Categories", orientation='h')
	fig.update_layout(xaxis_range=[0,55])
	return fig


def get_score_over_time(df):
	test_df = df.copy()
	test_df["winner score"] = df[["score1", "score2", "score3"]].max(axis=1)
	test_df["lowest score"] = df[["score1", "score2", "score3"]].min(axis=1)
	test_df["avg score"] = df[["score1", "score2", "score3"]].mean(axis=1)

	fig = px.line(test_df, x="air_date", y=["winner score", "lowest score", "avg score"], title="Scores Over Time")

	return fig


def main():
	db = DBDriver(host="drona.db.elephantsql.com", name="hvkogzmy",
				  user="hvkogzmy", password="TqgdVBnft1hXRg7_oG73QZriwst4_BLA")


	clues = get_clues(db)
	games = get_games(db)

	info_df = get_info(games, clues)

	col1, col2, col3 = st.columns(3)
	col2.dataframe(info_df)

	col1, col2 = st.columns(2)
	bar = get_cat_dist(clues)
	col1.plotly_chart(bar)
	lowest = get_cat_dist_low(clues)
	col2.plotly_chart(lowest)

	col1, col2, col3 = st.columns(3)
	line = get_score_over_time(games)
	col2.plotly_chart(line)

if __name__ == "__main__":
	main()