import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import pyarrow.parquet as pq


# memoire cache
if "df" not in st.session_state:
    chemin = Path(__file__).parent
    fichier_data = chemin / "csv/df_datavis"
    df = pq.read_table(fichier_data ).to_pandas()
    st.session_state["df"] = df
else:
    df = st.session_state["df"]

# Liste des pays cibles
country_columns = ["US", "FR", "GB", "JP", "IN", "KR", "CN", "ALL"]


def show():

    # Créer une barre de sélection de pays dans la sidebar
    with st.sidebar:
        st.subheader("Choisissez un pays:")
        selected_country = st.radio("Sélectionner le pays", country_columns)

        # Filtrer le DataFrame en fonction du pays sélectionné
        filtered_df = df[df["top7_countries"].apply(lambda x: selected_country in x)]

        # Définition des genres
        genre = [
            "Drama",
            "Comedy",
            "Documentary",
            "Romance",
            "Thriller",
            "Action",
            "Horror",
            "Crime",
            "Adventure",
            "Family",
            "Music",
            "Mystery",
            "Science Fiction",
            "Fantasy",
            "History",
            "Animation",
            "War",
            "Western",
        ]

    # _____________________________________________________________________
    # Nombre de films par genres
    # _____________________________________________________________________
    # la page
    col_tire = st.columns([0.20, 0.75, 0.15])
    with col_tire[1]:
        st.title("Analyse des genres")
    col_texte = st.columns([0.20, 0.55, 0.25])
    with col_texte[1]:
        st.divider()
        multi = """
<p style="font-size: 18px; color: #e8b5db;">
L'analyse des données cinématographiques offre une perspective fascinante sur les préférences culturelles 
et les tendances mondiales en matière de divertissement. Dans cette étude, nous explorons une vaste collection
de films à travers différents pays, en nous concentrant particulièrement sur la répartition des genres cinématographiques.
</p>
        """
        st.markdown(multi, unsafe_allow_html=True)
        st.divider()
    col_titre_bar = st.columns([0.30, 0.50, 0.20])
    with col_titre_bar[1]:
        st.header("Nombre de films par genre")
    col_genre = st.columns([0.10, 0.70, 0.20])
    with col_genre[1]:
        genre_counts = filtered_df[genre].sum()
        df_genre_counts = pd.DataFrame(
            {"Genre": genre, "Nombre de films": genre_counts}
        )
        df_genre_counts = df_genre_counts.sort_values(
            by="Nombre de films", ascending=False
        )
        fig = px.bar(
            df_genre_counts,
            x="Genre",
            y="Nombre de films",
            color="Genre",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        # configuration de l'affichage du potly ( transparence...)
        fig.update_layout(
            barmode="overlay",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            width=1000,
            height=700,
            xaxis=dict(tickfont=dict(color="#e8b5db")),
            yaxis=dict(tickfont=dict(color="#e8b5db")),
            legend=dict(
                title=dict(text="Legend", font=dict(size=12, color="#e8b5db")),
                font=dict(color="#e8b5db"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
        )
        st.plotly_chart(fig)

        # _____________________________________________________________________
        # Rentabilité des films par genres
        # _____________________________________________________________________
    col_titre_graph = st.columns([0.30, 0.50, 0.20])
    with col_titre_graph[1]:
        st.header("Rentabilité des films par genres")
    col_histo = st.columns([0.15, 0.70, 0.15])
    with col_histo[1]:
        data_budget = filtered_df[filtered_df["budget"] != 0]
        genre_budget = {}
        for g in genre:
            genre_budget[g] = (data_budget[g] * data_budget["budget"]).sum()

        data_revenues = filtered_df[filtered_df["revenue"] != 0]
        genre_revenues = {}
        for g in genre:
            genre_revenues[g] = (data_revenues[g] * data_revenues["revenue"]).sum()

        df_revenues = pd.DataFrame(
            list(genre_revenues.items()), columns=["Genre", "Revenue"]
        )
        df_budgets = pd.DataFrame(
            list(genre_budget.items()), columns=["Genre", "Budget"]
        )

        genre_budget_percentage = {}

        for genre in genre_budget:
            revenue = genre_revenues.get(genre, 0)
            budget = genre_budget[genre]
            if revenue != 0:
                percentage = (budget / revenue) * 100
            else:
                percentage = 0
            genre_budget_percentage[genre] = percentage

        df_budget_percentage = pd.DataFrame(
            list(genre_budget_percentage.items()),
            columns=["Genre", "Budget Percentage"],
        )

        df_merged = pd.merge(df_revenues, df_budgets, on="Genre")
        df_merged = pd.merge(df_merged, df_budget_percentage, on="Genre")

        df_merged["100%"] = 100
        df_merged_sorted = df_merged.sort_values(by="Budget Percentage")
        trace2 = go.Bar(
            x=df_merged_sorted["Genre"],
            y=df_merged_sorted["Budget Percentage"],
            marker=dict(color="#e8b5db"),
            name="Budget",
            hoverinfo="y",
        )

        trace1 = go.Bar(
            x=df_merged_sorted["Genre"],
            y=df_merged_sorted["100%"],
            marker=dict(color="#800080"),
            name="Revenue",
            hoverinfo="y",
        )

        fig = go.Figure(data=[trace1, trace2])

        fig.update_layout(
            barmode="overlay",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            width=1000,
            height=700,
            xaxis=dict(tickfont=dict(color="#e8b5db")),
            yaxis=dict(tickfont=dict(color="#e8b5db")),
            legend=dict(
                title=dict(text="Legend", font=dict(size=12, color="#e8b5db")),
                font=dict(color="#e8b5db"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
        )

        st.plotly_chart(fig)

        lambda row: (
    print(
        f"Title: {row['title']}, Percentage: {(row['budget'] / row['revenue']) * 100:.2f}%"
    )
    if row["revenue"]!= 0 and (row["budget"] / row["revenue"]) * 100 > 100
    else None
)
        # _____________________________________________________________________
        # Moyenne des scores par genres et par années
        # _____________________________________________________________________
    col_titre_scatter = st.columns([0.30, 0.50, 0.20])
    with col_titre_scatter[1]:
        st.header("Moyenne des scores par genres et par années")
    col_sc = st.columns([0.1, 0.70, 0.20])
    with col_sc[1]:
        data = filtered_df[
            (filtered_df["averageRating"] != 0)
            & (filtered_df["numVotes"] > 50)
            & (filtered_df["année_de_sortie"] > 1960)
        ]
        genre = [
            "Drama",
            "Comedy",
            "Documentary",
            "Romance",
            "Thriller",
            "Action",
            "Horror",
            "Crime",
            "Adventure",
            "Family",
            "Music",
            "Mystery",
            "Science Fiction",
            "Fantasy",
            "History",
            "Animation",
            "War",
            "Western",
        ]
        traces = []
        for g in genre:
            # Regrouper par année de sortie et calculer la moyenne de la note moyenne pour chaque année
            genre_data = (
                data[data[g] == 1]
                .groupby("année_de_sortie")["averageRating"]
                .mean()
                .reset_index()
            )
            # Tracer la moyenne par année
            trace = go.Scatter(
                x=genre_data["année_de_sortie"],
                y=genre_data["averageRating"],
                mode="lines",
                name=g,
            )
            traces.append(trace)

            # Création de la figure
            layout = go.Layout(
                xaxis=dict(title="Année de sortie"),
                yaxis=dict(title="Note moyenne"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                hovermode="closest",
                template="plotly_white",
            )
        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            width=1000,
            height=700,
            xaxis=dict(tickfont=dict(color="#e8b5db")),
            yaxis=dict(tickfont=dict(color="#e8b5db")),
            legend=dict(
                title=dict(text="Legend", font=dict(size=12, color="#e8b5db")),
                font=dict(color="#e8b5db"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
        )

        st.plotly_chart(fig)

        # _____________________________________________________________________
        # Moyenne des nombre de vote par genres et par années
        # _____________________________________________________________________
    col_titre_scatter2 = st.columns([0.30, 0.50, 0.20])
    with col_titre_scatter2[1]:
        st.header("Nombre de vote par genres et par années")
    col_sc2 = st.columns([0.1, 0.70, 0.20])
    with col_sc2[1]:
        df_nv = filtered_df[
            (filtered_df["numVotes"] != 0)
            & (filtered_df["numVotes"] > 50)
            & (filtered_df["année_de_sortie"] > 1960)
        ]
        traces = []
        for g in genre:
            genre_data = (
                df_nv[df_nv[g] == 1]
                .groupby("année_de_sortie")["numVotes"]
                .mean()
                .reset_index()
            )
            trace = go.Scatter(
                x=genre_data["année_de_sortie"],
                y=genre_data["numVotes"],
                mode="lines",
                name=g,
            )
            traces.append(trace)
        # Création de la figure
        layout = go.Layout(
            xaxis=dict(title="Année de sortie"),
            yaxis=dict(title="Nombres de Votes"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            hovermode="closest",
            template="plotly_white",
        )

        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            width=1000,
            height=700,
            xaxis=dict(tickfont=dict(color="#e8b5db")),
            yaxis=dict(tickfont=dict(color="#e8b5db")),
            legend=dict(
                title=dict(text="Legend", font=dict(size=12, color="#e8b5db")),
                font=dict(color="#e8b5db"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
        )
        # Affichage de la figure
        st.plotly_chart(fig)

        st.session_state["filtered_df"] = filtered_df
