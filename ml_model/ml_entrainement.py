import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import pyarrow.parquet as pq

# Load the data from parquet file
df = pq.read_table("csv/film_ver4.parquet").to_pandas()
df_ia = df[["tconst", "title", "overview"]]
# Initialize the TfidfVectorizer with max_df=0.8, min_df=50, and stop_words="english"
tfidf = TfidfVectorizer(max_df=0.8, min_df=50, stop_words="english")

# Fit and transform the 'overview' column of df_ia
tfidf_matrix = tfidf.fit_transform(df_ia.overview)

# Initialize the NearestNeighbors model with n_neighbors=50
modelKNN = NearestNeighbors(n_neighbors=50)

# Fit the model with tfidf_matrix
modelKNN.fit(tfidf_matrix)

# Save the model and tfidf_matrix using joblib
joblib.dump(modelKNN, "model.pkl")
joblib.dump(tfidf_matrix, "tfidf.pkl")
