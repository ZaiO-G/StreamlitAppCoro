from shared.auth import check_password
check_password()
import streamlit as st

st.set_page_config(
    page_title="Outils Labo — Équipe Corona INRAE",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700;800&family=Nunito+Sans:wght@400;600&display=swap');

    .stApp { background-color: #ffffff; font-family: 'Nunito Sans', sans-serif; }

    h1 { font-family: 'Raleway', sans-serif !important; color: #00a3a6 !important; font-weight: 800 !important; font-size: 2.2rem !important; border-bottom: 3px solid #00a3a6; padding-bottom: 0.4rem; }
    h2, h3 { font-family: 'Raleway', sans-serif !important; color: #275662 !important; font-weight: 700 !important; border-bottom: 1px solid #66c1bf; padding-bottom: 0.3rem; }
    p, label, .stMarkdown { font-family: 'Nunito Sans', sans-serif !important; color: #2d2d2d !important; }

    .stAlert { background: #e8f7f7 !important; border-left: 4px solid #00a3a6 !important; border-radius: 8px !important; color: #275662 !important; }

    .stButton button { background-color: #00a3a6 !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Raleway', sans-serif !important; font-weight: 700 !important; padding: 0.5rem 1.5rem !important; }
    .stButton button:hover { background-color: #008c8e !important; }

    hr { border-color: #66c1bf !important; }

    section[data-testid="stSidebar"] { background-color: #f5fafa !important; border-right: 2px solid #66c1bf !important; }
    section[data-testid="stSidebar"] * { font-family: 'Nunito Sans', sans-serif !important; color: #275662 !important; }

    .card {
        background: #f5fafa;
        border: 1px solid #66c1bf;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-3px); }
    .card h3 { border: none !important; font-size: 1.1rem !important; }
    .card p { font-size: 0.9rem; color: #64748b !important; }
</style>
""", unsafe_allow_html=True)

# --- EN-TÊTE ---
col_logo, col_titre = st.columns([1, 4])
with col_logo:
   st.image("logo_inrae.png", width=180)
with col_titre:
    st.title("Outils Labo — Équipe Corona")
    st.markdown("**Institut national de recherche pour l'agriculture, l'alimentation et l'environnement**")

st.divider()
# --- PRÉSENTATION DES OUTILS ---
st.subheader("Outils disponibles")

col1, col2,col3,col4,col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class='card'>
        <h3>Normalisation Nanodrop</h3>
        <p>Importe tes mesures Nanodrop, exclus les valeurs aberrantes et génère automatiquement ton tableau de normalisation avec les volumes à prélever.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Nanodrop.py", label="Ouvrir")

with col2:
    st.markdown("""
    <div class='card'>
        <h3>Préparation Anticorps IHC</h3>
        <p>Sélectionne tes anticorps primaires et secondaires, vérifie les incompatibilités et calcule les volumes de tampon à préparer pour tes immunohistochimies.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_IHC.py", label="Ouvrir")

with col3:
    st.markdown("""
    <div class='card'>
        <h3>qPCR - Plan de plaque</h3>
        <p>Génère ton plan de plaque et calcule les mix à préparer.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_qPCR.py", label="Ouvrir")

with col4:
    st.markdown("""
    <div class='card'>
        <h3>Culture Cellulaire</h3>
        <p>Calcule ta concentration cellulaire à partir du comptage de cellule.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Culture Cellulaire.py", label="Ouvrir")

with col5:
    st.markdown("""
    <div class='card'>
        <h3>GFP_Fusion</h3>
        <p>Prépare tes transfections.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_GFP_Fusion.py", label="Ouvrir")
st.divider()
st.caption("Outil développé par LMBV - Équipe Corona INRAE")