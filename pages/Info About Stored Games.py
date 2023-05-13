import streamlit as st
from dbdriver import DBDriver
import pandas.io.sql as psql
import plotly.express as px

st.set_page_config(page_title="Info About Stored Games")

def get_cat_dist(db):
	test_df = psql.read_sql(
	f"SELECT * FROM jeopardy.clues", db.conn)
	test_df = test_df["category"].value_counts().reset_index(name='count').rename({"index": "category"}, axis=1).iloc[:10]
	fig = px.bar(test_df, x="category", y="count", title="Clue Counts for Top 10 Most Frequent Categories")

	return fig


db = DBDriver(host="drona.db.elephantsql.com", name="hvkogzmy",
			  user="hvkogzmy", password="TqgdVBnft1hXRg7_oG73QZriwst4_BLA")
bar = get_cat_dist(db)
st.plotly_chart(bar)