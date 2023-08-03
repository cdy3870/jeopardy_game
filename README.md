# Jeopardy Game

This repo contains a Jeopardy game I created using the Cluebase API. It contains features such as playing random full games from the past and allows you to prep for a popular category or a specific general category.

## Requirements

This dashboard is hosted on Streamlit's community cloud and does not require you to run the code locally. You can access the site through this link: https://jeopardy.streamlit.app/. If the app does not work in Chrome, try Safari.

## Libraries, Frameworks, APIs, Cloud Services
1. Libraries and Frameworks
- HuggingFace
- Pandas
- Streamlit
- Scikit-Learn
- Plotly
2. APIs
- Cluebase (https://cluebase.readthedocs.io/en/latest/)
3. Databases
- PostgresSQL hosted on ElephantSQL

## How it works and services involved
1. 500 old Jeopardy games are stored into a PostgresSQL DB by performing requests to the Cluebase API
2. Simple control flow logic is used to generate new games and clues and the score is also tracked
3. A zero-shot learning classifier (https://huggingface.co/tasks/zero-shot-classification) is used to group categories
- Zero-shot learning is essentially learning to predict from instances that the model has never seen before
- If we use a pre-trained NLP language model from HuggingFace, we are able to group categories such as chemistry and physics into a general science category
- A heat map is used to show the confidence the model has in the specific categories
4. Additional visualizations of data are shown using Plotly to give a better overview of data used
