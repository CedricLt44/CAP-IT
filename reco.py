import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import pyarrow.parquet as pq

# Charger les données des films et enlever les accents des titres
# df = pd.read_csv("csv/base.csv", sep=",", low_memory=False)
path="csv/base.parquet"
df = pq.read_table(path).to_pandas()

# Fonction pour charger le modèle

modelKNN = joblib.load("ml_model/model.pkl")
tfidf_matrix = joblib.load("ml_model/tfidf.pkl")


# Stocker les films dans l'état de la session Streamlit
if "film_df" not in st.session_state:
    st.session_state["film_df"] = df
else:
    film_df = st.session_state["film_df"]


# Fonction pour obtenir les recommandations
"""def get_recommendations(title, tfidf_matrix):
    # Trouver l'indice du titre dans le dataframe
    matching_titles = df[df["title_fr"].str.lower().str.contains(title.lower())]
    if matching_titles.empty:
        return None
    id_title = matching_titles.index[0]
    distances, indices = modelKNN.kneighbors(tfidf_matrix[id_title])
    # Indices des films similaires
    similar_movies_indices = indices.flatten()[1:]
    # Retirer le film lui-même
    similar_movies = df.iloc[similar_movies_indices]
    return similar_movies"""


def get_recommendations(title, tfidf_matrix, genre):
    # Trouver l'indice du titre dans le dataframe
    matching_titles = df[df["title_fr"].str.lower().str.contains(title.lower())]
    if matching_titles.empty:
        return None
    id_title = matching_titles.index[0]
    distances, indices = modelKNN.kneighbors(tfidf_matrix[id_title].reshape(1, -1))
    recommended_movies_indices = indices.flatten()[1:]
    recommended_movies = df.iloc[recommended_movies_indices]
    recommended_movies = recommended_movies[
        (recommended_movies["genres"].str.contains(genre)) | (genre == "-")
    ]
    return recommended_movies


# Sélection du film de référence par l'utilisateur
if "genres" not in st.session_state:
    st.session_state["genres"] = "-"

liste_genres = [
    "-",
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western",
]


# Configuration de l'application Streamlit
def show():
    with st.sidebar:
        # Sélection du genre
        genre = st.sidebar.selectbox("Genre recherché : ", liste_genres,index=liste_genres.index("Adventure"))
        st.session_state["genres"] = genre
        # Afficher l'image du film sélectionné
    col_tire = st.columns([0.10, 0.80, 0.10])
    with col_tire[1]:
        st.title("FILMS")

    col_films = st.columns([0.20, 0.60, 0.20])
    with col_films[1]:
        st.text("Ecrire le titre exact ponctuation comprise")
        title = st.text_input("Entrez le nom d'un film :", value="Alice in Wonderland")
        if title:
            matching_titles = df[df["title_fr"].str.lower().str.contains(title.lower())]
            if not matching_titles.empty:
                id_title = matching_titles.index[0]
                selected_film = df.loc[id_title]
                image = "https://image.tmdb.org/t/p/original"+selected_film["poster_path"]
                with st.sidebar:
                    st.header("Film sélectionné:")
                    st.subheader(selected_film["title_fr"])
                    st.image(image, width=150, caption=selected_film["title_fr"])
        if title:
            title_x = title.lower()
            recommended_movies = get_recommendations(title_x, tfidf_matrix, genre)
            if recommended_movies is not None:
                with st.sidebar:
                    st.write("Films recommandés :")
                    for index, row in recommended_movies[["title_fr"]].iterrows():
                        if st.button(row["title_fr"]):
                            new_recommendation = get_recommendations(
                                row["title_fr"], tfidf_matrix, genre
                            )
                            if new_recommendation is not None:
                                recommended_movies = new_recommendation
            else:
                st.write(f"Le titre '{title}' n'a pas été trouvé dans le dataset.")
        # Afficher les images des films
        url_diapo = """
        <style>
        .scroll-container {
            overflow: auto;
            white-space: nowrap;
            padding: 10px;
            width: 100%;

            /* Ajout des propriétés pour la barre de défilement */
            scrollbar-width: thin; /* Largeur de la barre de défilement */
            scrollbar-color: #e8b5db transparent; /*Couleur de la barre de défilement et de l'arrière-plan */
        }
        /* Pour les navigateurs WebKit (Chrome, Safari) */
        .scroll-container::-webkit-scrollbar {
            width: 20px; /* Largeur de la barre de défilement */
        }
        .scroll-container::-webkit-scrollbar-track {
            background: #F0F2F6; /* Couleur de l'arrière-plan */
        }
        .scroll-container::-webkit-scrollbar-thumb {
            background-color: #e8b5db; /* Couleur de la barre de défilement */
            border-radius: 20px; /* Arrondi de la barre de défilement */
            border: 3px solid #FFFFFF; /* Bordure de la barre de défilement */
            height: 30px
        }
        .image-container {
            display: inline-block;
            text-align: center;
            margin-right: 20px;
        }
        .caption {
            margin-top: 5px;
            font-style: italic;
        }
        </style>
        <div class="scroll-container">"""

        url_images = ""
    col_reco = st.columns([0.05, 0.90, 0.05])
    with col_reco[1]:
        if recommended_movies is not None:
            for idx in range(10):
                try:
                    img_url = recommended_movies.iloc[idx]["poster_path"]
                    path = "https://image.tmdb.org/t/p/original"
                    url = path + img_url
                    # st.image(url, width=150, caption=df_reco.iloc[idx]["Titre vo"])
                    url_images += (
                        '<div class="image-container"><a href="https://www.imdb.com/title/'
                        + recommended_movies.iloc[idx]["tconst"]
                        + '"target="_blank">'
                        + '<img src="'
                        + url
                        + '" width="300"></a><p class="caption">'
                        + recommended_movies.iloc[idx]["title_fr"]
                        + " <br>"
                        + recommended_movies.iloc[idx]["genres"]
                        + " <br>"
                        + recommended_movies.iloc[idx]["Director_Names"]
                        + "</p></div>"
                    )
                except:
                    pass
        else:
            st.write("No recommended movies found.")
        url_diapo += url_images + "</div>"
        st.markdown(url_diapo, unsafe_allow_html=True)
