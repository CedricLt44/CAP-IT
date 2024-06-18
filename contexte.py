import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

chemin = Path(__file__).parent
fichier_data = chemin / "csv/creuse_final_2022.csv"
fichier_dataviz = chemin / "csv/creuze_dataviz.csv"
data = pd.read_csv(fichier_dataviz)
df = pd.read_csv(fichier_data)

# nettoyage du csv
df.drop(columns=["Unnamed: 0"])
df["PdM en entrées des films américains"] = df[
    "PdM en entrées des films américains"
].str.replace(",", ".")
df["PdM en entrées des films français"] = df[
    "PdM en entrées des films français"
].str.replace(",", ".")
# Conversion des colonnes en numérique
df["PdM en entrées des films américains"] = pd.to_numeric(
    df["PdM en entrées des films américains"]
)
df["PdM en entrées des films français"] = pd.to_numeric(
    df["PdM en entrées des films français"]
)
# création d'une liste des départemants unique
dept_names = df["DEP_name"].unique().tolist()
# création d'une option qui permet de tout selectionnés
dept_names.insert(0, "FRANCE")


def show():
    col_logo = st.columns([0.05, 0.30, 0.40, 0.20, 0.05])
    with col_logo[1]:
        st.image("Images/inseelogo.png", width=60)
    with col_logo[2]:
        st.image("Images/Logocnc.png", width=200)
    with col_logo[3]:
        st.image("Images/imdblogo.png", width=115)

    # Afficher le titre et l'entête
    col_title = st.columns([0.25, 0.30, 0.30, 0.15])
    with col_title[1]:
        st.title("CONTEXTE")
    col_header = st.columns([0.20, 0.60, 0.20])
    with col_header[1]:
        st.header("Marché du cinéma en FRANCE")

    col_carte = st.columns([0.2, 0.60, 0.20])
    with col_carte[1]:
        st.header("Répartition des PDM")
        # création d'une selected box
        selected_dept = st.selectbox("Sélectionne un departement", dept_names)
        # si tout les departement selectionné
        # Convert the "séances" column to numeric

        if selected_dept == "FRANCE":
            fig = px.scatter_mapbox(
                df,
                template="plotly_dark",
                lat="latitude",
                lon="longitude",
                hover_name="DEP_name",
                hover_data=[
                    "séances",
                    "PdM en entrées des films américains",
                    "PdM en entrées des films français",
                    "nom",
                    "commune",
                ],
                color="PdM en entrées des films français",
                size="PdM en entrées des films français",
                color_continuous_scale=px.colors.sequential.Plasma,
                labels={"PdM en entrées des films français": "Films français"},
                size_max=20,
                zoom=5,
                # height=650,
                # width=810,
            )
            # Définir le style de la carte
            fig = fig.update_layout(mapbox_style="open-street-map")

            # Ajuster les marges de la mise en page
            fig.update_layout(
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                plot_bgcolor="rgba(0, 0, 0, 0.2)",
                paper_bgcolor="rgba(0, 0, 0, 0.2)",
                width=810,
                height=650,
            )
            # Changer la couleur de la légende
            fig.update_layout(
                legend=dict(font=dict(size=12, color="#e8b5db")),
                coloraxis_colorbar=dict(
                    title=dict(
                        font=dict(
                            color="#e8b5db"  # Couleur du titre de la barre de couleur
                        )
                    ),
                    tickfont=dict(
                        color="#e8b5db"  # Couleur des ticks de la barre de couleur
                    ),
                ),
            )
            # Afficher la figure dans Streamlit
            st.plotly_chart(fig)
        else:
            filtered_df = df[df["DEP_name"] == selected_dept]
            fig = px.scatter_mapbox(
                filtered_df,
                lat="latitude",
                lon="longitude",
                hover_name="DEP_name",
                hover_data=[
                    "séances",
                    "PdM en entrées des films américains",
                    "PdM en entrées des films français",
                    "nom",
                    "commune",
                ],
                color="PdM en entrées des films français",
                size="PdM en entrées des films français",
                color_continuous_scale=px.colors.sequential.Plasma,
                labels={"PdM en entrées des films français": "Films français"},
                size_max=20,
                zoom=8,
                height=680,
                width=810,
            )
            # Définir le style de la carte
            fig = fig.update_layout(mapbox_style="open-street-map")
            # Ajuster les marges de la mise en page
            fig.update_layout(
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                plot_bgcolor="rgba(0, 0, 0, 0.2)",
                paper_bgcolor="rgba(0, 0, 0, 0.2)",
                width=1000,
                height=700,
            )
            # Afficher la figure dans Streamlit
            st.plotly_chart(fig)
    col_title_px = st.columns([0.20, 0.60, 0.20])
    with col_title_px[1]:
        st.header("Répartition des notes par genre et par pays")
    col_px = st.columns([0.10, 0.70, 0.20])
    with col_px[1]:
        fig = px.scatter(
            data,
            x="Genre",
            y="Rating",
            color="Country",
            size=data["Count"],
            size_max=50,
            opacity=0.5,
            width=810,
        )
        fig.update_traces(marker=dict(sizemin=5))
        fig.update_layout(
            barmode="overlay",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0.2)",
            width=1000,
            height=700,
            xaxis=dict(tickfont=dict(color="#e8b5db")),
            yaxis=dict(tickfont=dict(color="#e8b5db")),
            legend=dict(
                title=dict(text="Legend", font=dict(size=12, color="#e8b5db")),
                font=dict(color="#e8b5db"),
                bgcolor="rgba(0, 0, 0, 0.2)",
            ),
        )

        st.plotly_chart(fig)
    col_tech = st.columns([0.20, 0.70, 0.10])
    with col_tech[1]:
        st.header("Technologies utilisées")
        multi = """
        <p style="font-size: 18px; color: #e8b5db;">
        Ce projet a été réalisé en utilisant les LIBRAIRY suivantes :<br>
         - streamlit<br>
         - Pandas<br>
         - plotly.express<br>
         - sklearn<br>
        </p>
        """
        st.markdown(multi, unsafe_allow_html=True)
        st.header("Languages utilisés")
        multi = """
        <p style="font-size: 18px; color: #e8b5db;">
        Ce projet a été réalisé en utilisant les LANGAGES suivants :<br>
        - Python 3.12<br>
        - Css
        </p>
        """
        st.markdown(multi, unsafe_allow_html=True)
