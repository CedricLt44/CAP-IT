import streamlit as st
import pandas as pd
import ast
import plotly.express as px
from pathlib import Path
from joblib import Parallel, delayed
import pyarrow.parquet as pq

chemin = Path(__file__).parent
fichier_data = chemin / "csv/df_datavis"
data=pq.read_table(fichier_data ).to_pandas()

df = data[[
        "genres",
        "Actor_Names",
        "Producer_Names",
        "Writer_Names",
        "Director_Names",
        "production_countries",
        "année_de_sortie",
        "revenue",
        "budget",
        "title",
        "averageRating",  # Include averageRatings in the columns
    ]]
# Parallel processing to parse columns
n_jobs = -1  # Use all available cores
for column in [
    "genres",
    "Actor_Names",
    "Producer_Names",
    "Writer_Names",
    "Director_Names",
    "production_countries",
]:
    df[column] = Parallel(n_jobs=n_jobs)(
        delayed(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])(x)
        for x in df[column]
    )

df["année_de_sortie"] = pd.to_numeric(df["année_de_sortie"], errors="coerce")


def show():
    col_tire = st.columns([0.10, 0.80, 0.10])
    with col_tire[1]:
        st.title("Analysis of Role")

    view = st.sidebar.radio(
        "Select View:", ["View by Country and Genre", "View by Role"]
    )

    if view == "View by Country and Genre":
        # User selections
        country_list = sorted(
            [
                c
                for c in df["production_countries"].explode().unique()
                if isinstance(c, str)
            ]
        )
        default_country_index = country_list.index("US") if "US" in country_list else 0
        country = st.sidebar.selectbox(
            "Choose a country:", country_list, index=default_country_index
        )
        year_range = st.sidebar.slider("Select a year range:", 1950, 2023, (1950, 2023))
        genres = sorted(
            set(
                g
                for sublist in df["genres"]
                for g in sublist
                if isinstance(sublist, list)
            )
        )
        selected_genres = st.sidebar.multiselect("Select genres:", genres)

        # Filter data
        filtered_df = df[
            df["production_countries"].apply(
                lambda x: (
                    len(x) == 1 and x[0] == country if isinstance(x, list) else False
                )
            )
            & df["année_de_sortie"].between(*year_range)
            & df["genres"].apply(
                lambda genres_list: (
                    any(g in selected_genres for g in genres_list)
                    if isinstance(genres_list, list)
                    else False
                )
            )
        ]

        if filtered_df.empty:
            st.write("No movies found!")
        else:
            col_role = st.columns([0.10, 0.60, 0.30])
            with col_role[1]:
                # Display top 10 names for each role
                for role in [
                    "Actor_Names",
                    "Writer_Names",
                    "Director_Names",
                    "Producer_Names",
                ]:
                    st.write(f"Top 10 {role.replace('_', ' ')}:")
                    name_counts = (
                        filtered_df.explode(role)
                        .dropna()[role]
                        .value_counts()
                        .nlargest(10)
                    )
                    # Extract movie titles and ratings for hover data
                    name_movies_ratings = (
                        filtered_df.explode(role)[[role, "title", "averageRating"]]
                        .groupby(role)
                        .apply(
                            lambda x: x.nlargest(10, "averageRating")[
                                ["title", "averageRating"]
                            ].to_dict(orient="records")
                        )
                        .to_dict()
                    )
                    hover_data = {
                        name: ", ".join(
                            [
                                f"{movie['title']} ({movie['averageRating']})"
                                for movie in movies
                            ]
                        )
                        for name, movies in name_movies_ratings.items()
                    }

                    # Sort the name counts in descending order
                    name_counts = name_counts.sort_values(ascending=False)
                    # Create the bar chart
                    fig = px.bar(
                        name_counts,
                        x=name_counts.index,
                        y=name_counts.values,
                        labels={"x": role.replace("_", " "), "y": "Count"},
                        height=400,
                        width=600,
                        template="plotly_dark",
                        color_discrete_sequence=["#E8B5DB"],
                        hover_data={
                            "x": [
                                hover_data.get(name, "") for name in name_counts.index
                            ]
                        },
                    )
                    # configuration de l'affichage du plotly (transparence...)
                    fig.update_layout(
                        barmode="overlay",
                        plot_bgcolor="rgba(0, 0, 0, 0)",
                        paper_bgcolor="rgba(0, 0, 0, 0)",
                        width=1000,
                        height=700,
                        xaxis=dict(tickfont=dict(color="#E8B5DB")),
                        yaxis=dict(tickfont=dict(color="#E8B5DB")),
                        legend=dict(
                            title=dict(
                                text="Legend", font=dict(size=12, color="#E8B5DB")
                            ),
                            font=dict(color="#E8B5DB"),
                            bgcolor="rgba(0, 0, 0, 0)",
                        ),
                    )
                    st.plotly_chart(fig)

    elif view == "View by Role":
        role = st.sidebar.radio(
            "Choose the role:",
            ["Actor_Names", "Writer_Names", "Director_Names", "Producer_Names"],
        )
        role_name = st.sidebar.text_input("Enter a name:")
        # Convert the input role name to lowercase for case-insensitive comparison
        role_name_lower = role_name.lower() if role_name else ""
        if role_name_lower:
            # Filter data based on the entered name and selected role
            filtered_df = df[
                df[role].apply(
                    lambda x: (
                        role_name_lower in [name.lower() for name in x]
                        if isinstance(x, list)
                        else False
                    )
                )
            ].dropna(subset=["revenue", "budget"])
            if filtered_df.empty:
                st.write("No data available for selected person in the role.")
            else:
                # Get top 20 films by revenue for the selected person in the role
                top_films = filtered_df.nlargest(20, "revenue")[
                    ["title", "revenue", "budget"]
                ].sort_values(by="revenue", ascending=False)
                # Melt the data to long format for Plotly
                top_films_melted = top_films.melt(
                    id_vars=["title"],
                    value_vars=["revenue", "budget"],
                    var_name="Financial",
                    value_name="Amount",
                )
                # Create the bar chart with sorted data and colored by financials
                col_bar = st.columns([0.10, 0.70, 0.20])
                with col_bar[1]:
                    fig = px.bar(
                        top_films_melted,
                        x="title",
                        y="Amount",
                        color="Financial",
                        barmode="group",
                        title=f"Top 20 films for {role_name} as a {role[:-6]}",  # Remove '_Names' from role for display # type: ignore
                        labels={
                            "title": "Film Title",
                            "Amount": "Amount ($)",
                            "Financial": "Financials",
                        },
                        color_discrete_map={"revenue": "#800080", "budget": "#E8B5DB"},
                    )
                    fig.update_layout(
                        barmode="overlay",
                        plot_bgcolor="rgba(0, 0, 0, 0)",
                        paper_bgcolor="rgba(0, 0, 0, 0)",
                        width=1000,
                        height=700,
                        xaxis=dict(tickfont=dict(color="#E8B5DB")),
                        yaxis=dict(tickfont=dict(color="#E8B5DB")),
                        legend=dict(
                            title=dict(
                                text="Legend", font=dict(size=12, color="#E8B5DB")
                            ),
                            font=dict(color="#E8B5DB"),
                            bgcolor="rgba(0, 0, 0, 0)",
                        ),
                    )
                    st.plotly_chart(fig)
        else:
            st.write("Please enter a name to see the data.")
