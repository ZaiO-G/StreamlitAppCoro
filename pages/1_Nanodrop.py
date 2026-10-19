import streamlit as st
import pandas as pd
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700;800&family=Nunito+Sans:wght@400;600&display=swap');
    .stApp {
        background-color: #ffffff;
        font-family: 'Nunito', sans-serif;
    }

    h1 {
        font-family: 'Raleway', sans-serif !important;
        color: #00a3a6 !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        border-bottom: 3px solid #00a3a6;
        padding-bottom: 0.4rem;
    }

    h2, h3 {
        font-family: 'Raleway', sans-serif !important;
        color: #275662 !important;
        font-weight: 700 !important;
        border-bottom: 1px solid #66c1bf;
        padding-bottom: 0.3rem;
    }

    p, label, .stMarkdown {
        font-family: 'Nunito', sans-serif !important;
        color: #2d2d2d !important;
    }

    .stAlert {
        background: #e8f7f7 !important;
        border-left: 4px solid #00a3a6 !important;
        border-radius: 8px !important;
        color: #275662 !important;
    }

    .stTextInput input, .stNumberInput input {
        background: #f5fafa !important;
        border: 1.5px solid #66c1bf !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        font-family: 'Nunito', sans-serif !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #00a3a6 !important;
        box-shadow: 0 0 0 2px #00a3a633 !important;
    }

    .stSelectbox div {
        border: 1.5px solid #66c1bf !important;
        border-radius: 8px !important;
    }

    .stButton button, .stDownloadButton button {
        background-color: #00a3a6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Raleway', sans-serif !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.5rem !important;
        transition: background 0.2s !important;
    }

    .stButton button:hover, .stDownloadButton button:hover {
        background-color: #008c8e !important;
    }

    .stMetric {
        background: #e8f7f7 !important;
        border: 1px solid #66c1bf !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }

    .stMetric label {
        color: #008c8e !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.8rem !important;
    }

    .stMetric div {
        color: #275662 !important;
        font-weight: 700 !important;
    }

    .stDataFrame {
        border-radius: 10px !important;
        border: 1px solid #66c1bf !important;
    }

    hr {
        border-color: #66c1bf !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f5fafa !important;
        border-right: 2px solid #66c1bf !important;
    }
</style>
""", unsafe_allow_html=True)
st.title("Normalisation des données après Nanodrop")
st.write("Importe ton fichier Excel, exclus les valeurs aberrantes, et génère ton tableau de normalisation.")

fichier = st.file_uploader("Importe ton fichier excel avec les valeurs brutes du nanodrop", type=["xlsx", "xls"])

if fichier:
    df = pd.read_excel(fichier)
    st.subheader("Aperçu du fichier importé")
    st.dataframe(df)

    st.subheader("Paramètres de normalisation")
    col1, col2 = st.columns(2)
    with col1:
        c_finale = st.number_input("Concentration finale souhaitée (ng/µL)", value=100)
    with col2:
        v_finale = st.number_input("Volume final (µL)", value=20)

    col_id = st.selectbox("Colonne Sample ID", df.columns)
    col_conc = st.selectbox("Colonne concentration (Nucleic Acid)", df.columns)

    st.subheader("Sélectionne les mesures à garder")

    echantillons = df[col_id].unique()
    moyennes = {}

    for ech in echantillons:
        subset = df[df[col_id] == ech].reset_index()
        st.markdown(f"**{ech}**")
        valeurs_gardees = []
        cols = st.columns(len(subset))
        for i, row in subset.iterrows():
            with cols[i]:
                garder = st.checkbox(
                    f"{row[col_conc]} ng/µL",
                    value=True,
                    key=f"{ech}_{i}"
                )
                if garder:
                    valeurs_gardees.append(row[col_conc])
        if valeurs_gardees:
            moyennes[ech] = round(sum(valeurs_gardees) / len(valeurs_gardees), 2)

    if st.button("Générer le tableau de normalisation"):
        resultats = []
        for ech, moy in moyennes.items():
            v_prelever = round((c_finale * v_finale) / moy, 2)
            v_eau = round(v_finale - v_prelever, 2)
            resultats.append({
                "Sample ID": ech,
                "Concentration moyenne (ng/µL)": moy,
                "V à prélever (µL)": v_prelever,
                "V H2O RNase free (µL)": v_eau,
                "V finale (µL)": v_finale
            })

        df_final = pd.DataFrame(resultats)
        st.subheader("Tableau de normalisation")
        st.dataframe(df_final)

        import io
        buffer = io.BytesIO()
        df_final.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        nom_fichier = fichier.name.replace(".xlsx", "").replace(".xls", "")
        st.download_button(
            label="⬇️ Télécharger en Excel",
            data=buffer,
            file_name=f"{nom_fichier}_normalisation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )