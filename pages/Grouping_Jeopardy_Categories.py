import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="Grouping_Jeopardy_Categories")


broad_categories = ["science", "history", "sports",
					"literature", "movies and tv", "music",
					"geography", "word play", "religion"]

st.markdown("<h1 style='text-align: center'> Grouping Jeopardy Categories with NLP</h1>", unsafe_allow_html=True)

st.write("We've seen that there are over 5500 unique categories in the games we stored! What if we wanted to practice with a particular broader category?")

st.write("We can do this with zero-shot classification. This technique is used to predict labels that have not been seen before for each sample. HuggingFace has a pre-trained zero-shot classifier with a BERT transformer.")


@st.cache_data
def get_classified_cats():
	with open("classified_cats.txt", "rb") as f:
		classified_cats = pickle.load(f)

	return classified_cats

@st.cache_data
def get_all_results():
	with open("all_results.txt", "rb") as f:
		all_results = pickle.load(f)

	return all_results

def get_counts_plot(_classified_cats):
	counts_dict = {key: len(value) for key, value in _classified_cats.items()}
	counts_dict = dict(sorted(counts_dict.items(), key=lambda x: x[1]))
	keys, values = zip(*counts_dict.items())
	print(keys)
	print(values)
	new_df = pd.DataFrame({"category": keys, "count": values})
	fig = px.bar(new_df, y="category", x="count", title="Broad Categories Count", orientation='h')
	# fig.update_layout(yaxis=dict(autorange="reversed"))
	return fig
	
def get_confidence_charts(cats):
	# title = st.selectbox("Select title to show keywords (not all shown)", list(data["title"])[:50])
	# desc = data[data["title"] == title]["description"]
	# st.write(desc)

	# ngram = st.selectbox("N-gram Size", [1, 2, 3])
	# diversity = st.slider('Diversity in Results', 0.0, 1.0, step=0.1)
	# extracted = kw_model.extract_keywords(list(desc)[0], use_mmr=True, diversity=diversity, keyphrase_ngram_range=(1,ngram), top_n=5)

	# words, percents = zip(*dict(extracted).items())



	df = (
	pd.DataFrame({"broader category": cats["labels"], "probability": cats["scores"]})
	.sort_values(by="probability", ascending=False)
	.reset_index(drop=True)
	)

	df.index += 1

	# Add styling
	cmGreen = sns.light_palette("blue", as_cmap=True)
	cmRed = sns.light_palette("red", as_cmap=True)
	df = df.style.background_gradient(
		cmap=cmGreen,
		subset=[
			"probability",
		],
	)


	format_dictionary = {
	    "Score": "{:.1%}",
	}

	df = df.format(format_dictionary)

	return df




def main():
	all_results = get_all_results()
	classified_cats = get_classified_cats()

	updated_results = {item["sequence"]:item for item in all_results}

	bar = get_counts_plot(classified_cats)
	st.plotly_chart(bar)

	option = st.selectbox("", broad_categories)

	if option:
		sub_cats = classified_cats[option]
		sub_cat = st.selectbox("", sub_cats)

		df = get_confidence_charts(updated_results[sub_cat])
		st.table(df)
if __name__ == "__main__":
	main()