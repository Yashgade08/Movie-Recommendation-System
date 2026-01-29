import pickle
import streamlit as st
import requests
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommender System",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- TMDB API KEY ----------------
API_KEY = "9520fe73ae93df336e14809e9d6cadda"   # your TMDB v3 key

# ---------------- FETCH POSTER (ID BASED) ----------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY}

    try:
        response = requests.get(url, params=params, timeout=3)
        if response.status_code != 200:
            return None

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

        return None

    except requests.exceptions.RequestException:
        return None

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie_title):
    index = movies[movies["title"] == movie_title].index[0]
    distances = similarity[index]

    movie_list = sorted(
        enumerate(distances),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    names = []
    posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]]["id"]   # TMDB movie ID
        title = movies.iloc[i[0]]["title"]

        names.append(title)
        posters.append(fetch_poster(movie_id))

    return names, posters

# ---------------- STREAMLIT UI ----------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movies["title"].values
)

if st.button("Show Recommendation"):
    with st.spinner("Generating recommendations..."):
        names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.write("Poster not available")
