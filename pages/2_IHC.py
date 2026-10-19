from shared.auth import check_password
check_password()
import streamlit as st
import pandas as pd

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700;800&family=Nunito+Sans:wght@400;600&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Nunito Sans', sans-serif; }
    h1 { font-family: 'Raleway', sans-serif !important; color: #00a3a6 !important; font-weight: 800 !important; font-size: 2.2rem !important; border-bottom: 3px solid #00a3a6; padding-bottom: 0.4rem; }
    h2, h3 { font-family: 'Raleway', sans-serif !important; color: #275662 !important; font-weight: 700 !important; border-bottom: 1px solid #66c1bf; padding-bottom: 0.3rem; }
    p, label, .stMarkdown { font-family: 'Nunito Sans', sans-serif !important; color: #2d2d2d !important; }
    .stAlert { background: #e8f7f7 !important; border-left: 4px solid #00a3a6 !important; border-radius: 8px !important; color: #275662 !important; }
    .stTextInput input, .stNumberInput input { background: #f5fafa !important; border: 1.5px solid #66c1bf !important; border-radius: 8px !important; color: #1e293b !important; font-family: 'Nunito Sans', sans-serif !important; }
    .stSelectbox div { border: 1.5px solid #66c1bf !important; border-radius: 8px !important; }
    .stButton button, .stDownloadButton button { background-color: #00a3a6 !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Raleway', sans-serif !important; font-weight: 700 !important; padding: 0.5rem 1.5rem !important; }
    .stButton button:hover, .stDownloadButton button:hover { background-color: #008c8e !important; }
    .stMetric { background: #e8f7f7 !important; border: 1px solid #66c1bf !important; border-radius: 10px !important; padding: 1rem !important; }
    .stMetric label { color: #008c8e !important; font-size: 0.8rem !important; }
    .stMetric div { color: #275662 !important; font-weight: 700 !important; }
    .stDataFrame { border-radius: 10px !important; border: 1px solid #66c1bf !important; }
    hr { border-color: #66c1bf !important; }
    section[data-testid="stSidebar"] { background-color: #f5fafa !important; border-right: 2px solid #66c1bf !important; }
</style>
""", unsafe_allow_html=True)

AC_PRIMAIRES = [
    {"nom": "SARS monoclonal", "espece": "Mouse", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "SARS Nucleocapside protein", "boite": "Boîte 1", "note_dilution": ""},
    {"nom": "Arginase 1 polyclonal", "espece": "Rabbit", "dilution": "1/200", "demasquage": "", "marquage": "Macrophages M2", "boite": "Boîte 1", "note_dilution": ""},
    {"nom": "CK18", "espece": "Mouse", "dilution": "1/200", "demasquage": "Avec démasquage", "marquage": "Cytosquelette", "boite": "Boîte 1", "note_dilution": ""},
    {"nom": "Iba1 (Chicken)", "espece": "Chicken", "dilution": "1/100", "demasquage": "Avec démasquage (hamster) / Sans (souris)", "marquage": "Macrophages / microglie", "boite": "Boîte 1", "note_dilution": "⚠️ dilution Hamster : 1/100 — Souris : 1/500 (à tester 1/1000)"},
    {"nom": "Acetyl alpha tubuline (Mouse)", "espece": "Mouse", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "Cils", "boite": "Boîte 1", "note_dilution": ""},
    {"nom": "Acetyl alpha tubuline (Rabbit)", "espece": "Rabbit", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "Cils", "boite": "Boîte 1", "note_dilution": ""},
    {"nom": "SARS N (Mouse - lot noir)", "espece": "Mouse", "dilution": "1/1000", "demasquage": "", "marquage": "SARS Nucleocapside protein", "boite": "Boîte 1", "note_dilution": "⚠️ dilution Hamster : 1/1000"},
    {"nom": "GAP43 (Rabbit)", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Sans démasquage", "marquage": "Neurones immatures", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "hACE2", "espece": "Goat", "dilution": "1/10", "demasquage": "Avec démasquage", "marquage": "SARS-CoV-2 receptor ACE-2", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "Iba1 (Rabbit)", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Sans démasquage", "marquage": "Macrophages / microglie", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "His-tag monoclonal", "espece": "Mouse", "dilution": "1/500", "demasquage": "", "marquage": "6x His synthetic peptide", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "GNAT3", "espece": "Goat", "dilution": "", "demasquage": "", "marquage": "G protein subunit alpha transducin 3", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "GFP polyclonal", "espece": "Goat", "dilution": "", "demasquage": "", "marquage": "GFP", "boite": "Boîte 2", "note_dilution": ""},
    {"nom": "PGP 9.5", "espece": "Rabbit", "dilution": "1/2000", "demasquage": "Sans démasquage", "marquage": "Protéine spécifique des neurones", "boite": "Boîte 3", "note_dilution": ""},
    {"nom": "GAP43 (Mouse)", "espece": "Mouse", "dilution": "1/200", "demasquage": "Sans démasquage", "marquage": "Neurones immatures", "boite": "Boîte 3", "note_dilution": ""},
    {"nom": "CD68", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Macrophages M1", "boite": "Boîte 3", "note_dilution": ""},
    {"nom": "FoxJ1", "espece": "Goat", "dilution": "", "demasquage": "", "marquage": "Cils", "boite": "Boîte 3", "note_dilution": ""},
    {"nom": "BST2", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "BST2", "boite": "Boîte 4", "note_dilution": ""},
    {"nom": "H1N1", "espece": "Goat", "dilution": "", "demasquage": "", "marquage": "Virus influenza type A", "boite": "Boîte 4", "note_dilution": ""},
    {"nom": "CD163", "espece": "Mouse", "dilution": "", "demasquage": "", "marquage": "Macrophages M2", "boite": "Boîte 4", "note_dilution": ""},
    {"nom": "GSDMDC1", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "GSDMDC1", "boite": "Boîte 4", "note_dilution": ""},
    {"nom": "OMP (Fujifilm)", "espece": "Goat", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "Neurones olfactifs matures", "boite": "Boîte 4", "note_dilution": ""},
    {"nom": "LC3B", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Autophagie - cytosquelette", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "OMP (Don Margolis)", "espece": "Goat", "dilution": "1/400", "demasquage": "Sans démasquage", "marquage": "Neurones olfactifs matures", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "CD3", "espece": "Rabbit", "dilution": "1/20", "demasquage": "Avec démasquage", "marquage": "Lymphocytes T", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "OMP (WAKO)", "espece": "Goat", "dilution": "1/200", "demasquage": "", "marquage": "Neurones olfactifs matures", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "Adenylate Cyclase Type III", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Neurones olfactifs", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "Neutrophile Elastase", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Elastase", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "Mcherry", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Sans démasquage", "marquage": "Cassette MCherry", "boite": "Boîte 5", "note_dilution": ""},
    {"nom": "MPO hamster/rat", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Avec démasquage", "marquage": "Myeloperoxydase des neutrophiles", "boite": "Boîte 6", "note_dilution": ""},
    {"nom": "PCNA", "espece": "Mouse", "dilution": "", "demasquage": "", "marquage": "Cellules en prolifération", "boite": "Boîte 6", "note_dilution": ""},
    {"nom": "N-SOV", "espece": "Rabbit", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "N du SOV / N du PVM", "boite": "Boîte 6", "note_dilution": ""},
    {"nom": "Cleaved Caspase 3", "espece": "Rabbit", "dilution": "1/400", "demasquage": "Sans démasquage", "marquage": "Apoptose", "boite": "Boîte 6", "note_dilution": ""},
    {"nom": "APN", "espece": "Mouse", "dilution": "1/1000", "demasquage": "", "marquage": "Aminopeptidase N", "boite": "Boîte 6", "note_dilution": ""},
    {"nom": "ARN double brin dsRNA (J2)", "espece": "Mouse", "dilution": "1/1500", "demasquage": "Sans démasquage", "marquage": "Réplication virale", "boite": "Boîte 7", "note_dilution": ""},
    {"nom": "SARS (Rabbit - Novus)", "espece": "Rabbit", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "SARS Nucleocapside protein", "boite": "Boîte 7", "note_dilution": ""},
    {"nom": "mouse Ly6G", "espece": "Rat", "dilution": "1/500", "demasquage": "", "marquage": "Neutrophiles", "boite": "Boîte 7", "note_dilution": ""},
    {"nom": "MPO souris", "espece": "Rabbit", "dilution": "1/100", "demasquage": "Avec démasquage", "marquage": "Myeloperoxydase des neutrophiles", "boite": "Boîte 7", "note_dilution": ""},
    {"nom": "N SARS", "espece": "Goat", "dilution": "1/1000", "demasquage": "Sans démasquage", "marquage": "SARS Nucleocapside protein", "boite": "Boîte 7", "note_dilution": ""},
    {"nom": "ADCY3 polyclonal", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Avec démasquage", "marquage": "Neurones olfactifs", "boite": "Boîte 8", "note_dilution": ""},
    {"nom": "CNGA2 polyclonal", "espece": "Rabbit", "dilution": "1/100", "demasquage": "Sans démasquage", "marquage": "Neurones olfactifs", "boite": "Boîte 8", "note_dilution": ""},
    {"nom": "SOX2 monoclonal", "espece": "Rat", "dilution": "1/200", "demasquage": "Avec démasquage", "marquage": "Sustentaculaires", "boite": "Boîte 8", "note_dilution": ""},
    {"nom": "CK18 polyclonal", "espece": "Rabbit", "dilution": "1/200", "demasquage": "Sans démasquage", "marquage": "Sustentaculaires", "boite": "Boîte 8", "note_dilution": ""},
    {"nom": "SARS N (Goat - Boite 8)", "espece": "Goat", "dilution": "1/2000", "demasquage": "Sans démasquage", "marquage": "SARS Nucleocapside protein", "boite": "Boîte 8", "note_dilution": ""},
    {"nom": "FoxJ1", "espece": "Mouse", "dilution": "", "demasquage": "", "marquage": "Cils", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "Ki67", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Cellules en prolifération", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "G alpha s/olf (Mouse)", "espece": "Mouse", "dilution": "", "demasquage": "", "marquage": "Neurones olfactifs", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "G alpha s/olf (Rabbit)", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Neurones olfactifs", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "OMP (Mouse)", "espece": "Mouse", "dilution": "1/100", "demasquage": "Sans démasquage", "marquage": "Neurones olfactifs matures", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "human CD3", "espece": "Rabbit", "dilution": "", "demasquage": "", "marquage": "Lymphocytes T", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "hamster IgA", "espece": "Rabbit", "dilution": "1/250", "demasquage": "Sans démasquage", "marquage": "IgA hamster", "boite": "Frigo 4°C", "note_dilution": ""},
    {"nom": "GAP43 (Rabbit - Novus)", "espece": "Rabbit", "dilution": "1/500", "demasquage": "Sans démasquage", "marquage": "Neurones immatures", "boite": "Boîte 2", "note_dilution": "⚠️ Diltuion validé sur souris au 1/2000 total"},
]

SECONDAIRES = [
    {"espece_cible": "Mouse",   "canal": "488", "nom": "Alexa 488 Goat anti-Mouse",    "producteur": "Goat"},
    {"espece_cible": "Rabbit",  "canal": "488", "nom": "Alexa 488 Goat anti-Rabbit",   "producteur": "Goat"},
    {"espece_cible": "Goat",    "canal": "488", "nom": "Alexa 488 Donkey anti-Goat",   "producteur": "Donkey"},
    {"espece_cible": "Rat",     "canal": "488", "nom": "Alexa 488 Donkey anti-Rat",    "producteur": "Donkey"},
    {"espece_cible": "Sheep",   "canal": "488", "nom": "Alexa 488 Donkey anti-Sheep",  "producteur": "Donkey"},
    {"espece_cible": "Pig",     "canal": "488", "nom": "Alexa 488 Goat anti-Pig",      "producteur": "Goat"},
    {"espece_cible": "Human",   "canal": "488", "nom": "Alexa 488 Goat anti-Human",    "producteur": "Goat"},
    {"espece_cible": "Chicken", "canal": "488", "nom": "Alexa 488 Goat anti-Chicken",  "producteur": "Goat"},
    {"espece_cible": "Mouse",   "canal": "555", "nom": "Alexa 555 Goat anti-Mouse",    "producteur": "Goat"},
    {"espece_cible": "Mouse",   "canal": "555", "nom": "Alexa 555 Donkey anti-Mouse",  "producteur": "Donkey"},
    {"espece_cible": "Rabbit",  "canal": "555", "nom": "Alexa 555 Donkey anti-Rabbit", "producteur": "Donkey"},
    {"espece_cible": "Goat",    "canal": "555", "nom": "Alexa 555 Donkey anti-Goat",   "producteur": "Donkey"},
    {"espece_cible": "Goat",    "canal": "546", "nom": "Alexa 546 Donkey anti-Goat",   "producteur": "Donkey"},
    {"espece_cible": "Mouse",   "canal": "647", "nom": "Alexa 647 Donkey anti-Mouse",  "producteur": "Donkey"},
    {"espece_cible": "Rabbit",  "canal": "647", "nom": "Alexa 647 Donkey anti-Rabbit", "producteur": "Donkey"},
    {"espece_cible": "Goat",    "canal": "647", "nom": "Alexa 647 Donkey anti-Goat",   "producteur": "Donkey"},
    {"espece_cible": "Rat",     "canal": "647", "nom": "Alexa 647 Donkey anti-Rat",    "producteur": "Donkey"},
    {"espece_cible": "Chicken", "canal": "647", "nom": "Alexa 647 Donkey anti-Chicken","producteur": "Donkey"},
]

DILUTIONS_SEC = {"488": "1/400", "555": "1/800", "594": "1/800", "546": "1/800", "647": "1/800"}
ESPECES = ["Mouse", "Rabbit", "Goat", "Rat", "Sheep", "Pig", "Human", "Chicken", "Donkey"]
NOMS_AC = ["— Sélectionner —", "✏️ Autre Anticorps (saisie manuelle)"] + [a["nom"] for a in AC_PRIMAIRES]

# --- TITRE ---
st.title("Outil IHC - Préparation Anticorps")
st.write("Pensé et designé par Zai et Isis, bonne manip! :)")

st.markdown(f"[Accéder à la base anticorps]({st.secrets['lien_anticorps']})")
st.warning(f"⚠️ Penses à vérifier le stock d'anticorps, ainsi que les dilutions avant de commencer → [Ouvrir le Google Sheet]({st.secrets['lien_gsheet']})")
st.write("Sélectionne tes anticorps primaires et secondaires, vérifie les incompatibilités et calcule les volumes.")
try:
    st.image("schema_IHC3.png", use_container_width=True, caption="Principe de l'immunohistochimie")
except:
    pass

# --- PARAMÈTRES GÉNÉRAUX ---
st.subheader("Paramètres généraux")
col1, col2, col3 = st.columns(3)
with col1:
    nb_lames = st.number_input("Nombre de lames", min_value=1, value=6)
with col2:
    vol_par_lame = st.number_input("Volume par lame (µL)", min_value=10, value=200)
with col3:
    surplus = st.number_input("Surplus à ajouter (µL)", min_value=0, value=200)

vol_total = int(nb_lames * vol_par_lame + surplus)
st.info(f"Volume total à préparer : **{vol_total} µL** ({nb_lames} lames × {vol_par_lame} µL + {surplus} µL de surplus)")

# --- HELPER calcul volumes ---
def calcul_volumes(vol_total, dilution_str, nom):
    try:
        facteur = int(dilution_str.replace("1/", "").strip())
        vol_ac = round(vol_total / facteur, 2)
        if vol_ac < 1:
            vol_ac = 1.0
            vol_tampon = round(facteur - vol_ac, 2)
            return vol_ac, vol_tampon, facteur, True
        else:
            return vol_ac, round(vol_total - vol_ac, 2), vol_total, False
    except:
        return None, None, vol_total, False

# --- SAISIE ANTICORPS PRIMAIRES ---
st.subheader("Anticorps Primaires")
st.caption("Les primaires seront mélangés dans un seul tampon de dilution.")

tab1, tab2, tab3 = st.tabs(["Canal 1", "Canal 2", "Canal 3"])
primaires = []

for i, tab in enumerate([tab1, tab2, tab3]):
    with tab:
        choix = st.selectbox("Anticorps", NOMS_AC, key=f"ac_{i}")

        if choix == "✏️ Autre Anticorps (saisie manuelle)":
            nom_custom = st.text_input("Nom de l'anticorps", placeholder="ex: Anti-CD4", key=f"nom_custom_{i}")
            espece = st.selectbox("Espèce hôte", ESPECES, key=f"espece_manuel_{i}")
            dilution = st.text_input("Dilution", placeholder="ex: 1/500", key=f"dilution_manuel_{i}")
            demasquage = st.text_input("Démasquage", placeholder="ex: Sans démasquage", key=f"demasquage_manuel_{i}")
            if nom_custom:
                primaires.append({
                    "canal": i + 1, "nom": nom_custom, "espece": espece,
                    "dilution": dilution, "demasquage": demasquage,
                    "marquage": "Saisie manuelle", "boite": "À vérifier", "note_dilution": ""
                })

        elif choix != "— Sélectionner —":
            ac_info = next(a for a in AC_PRIMAIRES if a["nom"] == choix)

            # Clé unique par Ac — force Streamlit à recréer le widget avec les bonnes valeurs
            ac_key = f"{i}_{choix}"

            espece = st.selectbox(
                "Espèce hôte", ESPECES,
                index=ESPECES.index(ac_info["espece"]),
                key=f"espece_{ac_key}"
            )
            dilution = st.text_input(
                "Dilution",
                value=ac_info["dilution"],
                key=f"dilution_{ac_key}"
            )
            demasquage = st.text_input(
                "Démasquage",
                value=ac_info["demasquage"],
                key=f"demasquage_{ac_key}"
            )

            st.info(f"**{ac_info['marquage']}** — {ac_info['boite']}")
            if ac_info["note_dilution"]:
                st.warning(f"⚠️ {ac_info['note_dilution']}")

            primaires.append({
                "canal": i + 1, "nom": choix, "espece": espece,
                "dilution": dilution, "demasquage": demasquage,
                "marquage": ac_info["marquage"], "boite": ac_info["boite"],
                "note_dilution": ac_info["note_dilution"]
            })
# --- VÉRIFICATION INCOMPATIBILITÉS ---
especes_primaires = [p["espece"] for p in primaires]
doublons = set([e for e in especes_primaires if especes_primaires.count(e) > 1])
if doublons:
    st.markdown(f"<p style='color:red; font-weight:bold; font-size:1.1rem;'>⚠️ INCOMPATIBILITÉ DÉTECTÉE : deux anticorps primaires produits dans {', '.join(doublons)} — impossible de continuer !</p>", unsafe_allow_html=True)

# --- CALCUL VOLUMES PRIMAIRES ---
recap_primaires = []

if primaires:
    st.subheader("Solution n°1 Anticorps Primaires")
    st.success(f" Prépare **1 seul tube** de **{vol_total} µL de tampon anticorps**, puis ajoute dedans :")

    total_ac_preleve = 0

    for p in primaires:
        if not p["dilution"]:
            st.warning(f"⚠️ Dilution non renseignée pour **{p['nom']}**")
            continue

        vol_ac, vol_tampon, vol_utilise, ajuste = calcul_volumes(vol_total, p["dilution"], p["nom"])

        if vol_ac is None:
            st.warning(f"Format invalide pour **{p['nom']}** — utilise le format 1/500")
            continue

        total_ac_preleve += vol_ac

        if ajuste:
            st.warning(f"⚠️ **{p['nom']}** : volume ajusté à **{vol_utilise} µL** (vol Ac < 1µL avec le volume initial)")

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**→ {p['nom']}** ({p['espece']}) — dilution {p['dilution']}")
            if p['demasquage']:
                st.caption(f" Démasquage : {p['demasquage']}")
        with c2:
            st.metric("À prélever", f"{vol_ac} µL")

        recap_primaires.append({
            "nom": p["nom"], "vol_ac": vol_ac,
            "vol_total_utilise": vol_utilise, "ajuste": ajuste, "p": p
        })

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Volume tampon à préparer", f"{vol_total} µL")
    with c2:
        st.metric("Volume total Ac à ajouter", f"{round(total_ac_preleve, 2)} µL")
    st.info(f"💡 **Mode opératoire** : Prélève **{vol_total} µL de tampon anticorps** dans un tube, puis ajoute successivement chaque anticorps selon les volumes ci-dessus.")

# --- ANTICORPS SECONDAIRES ---
secondaires_choisis = []

if primaires and not doublons:
    st.subheader(" Solution n°2: Anticorps Secondaires")
    canaux_utilises = []

    for p in primaires:
        st.markdown(f"**Secondaire pour {p['nom']}** (cible : {p['espece']})")
        options = [
            s for s in SECONDAIRES
            if s["espece_cible"] == p["espece"]
            and s["producteur"] not in especes_primaires
            and s["canal"] not in canaux_utilises
        ]

        if not options:
            st.error(f"❌ Aucun secondaire compatible pour **{p['nom']}** !")
            continue

        noms_options = [f"{s['nom']} (filtre {s['canal']}, dilution {DILUTIONS_SEC[s['canal']]})" for s in options]
        choix_sec = st.selectbox(f"Choix pour {p['nom']}", noms_options, key=f"sec_{p['canal']}")
        sec_choisi = options[noms_options.index(choix_sec)]
        canaux_utilises.append(sec_choisi["canal"])
        secondaires_choisis.append({**sec_choisi, "primaire": p["nom"], "dilution": DILUTIONS_SEC[sec_choisi["canal"]]})

    if secondaires_choisis:
        st.subheader("Volumes Anticorps Secondaires")
        st.success(f" Prépare **1 seul tube** de **{vol_total} µL de tampon anticorps**, puis ajoute dedans :")

        for s in secondaires_choisis:
            vol_ac, vol_tampon, vol_utilise, ajuste = calcul_volumes(vol_total, s["dilution"], s["nom"])
            if ajuste:
                st.warning(f"⚠️ **{s['nom']}** : volume ajusté à **{vol_utilise} µL**")
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**→ {s['nom']}** pour {s['primaire']} — filtre {s['canal']}")
            with c2:
                st.metric("À prélever", f"{vol_ac} µL")

        st.divider()

# --- RÉCAPITULATIF FINAL ---
if recap_primaires or secondaires_choisis:
    st.subheader("Récapitulatif Final")
    st.success("✅ C'est good! Aucune incompatibilité détectée !")

    recap = []
    for r in recap_primaires:
        p = r["p"]
        note = f"Volume ajusté à {r['vol_total_utilise']} µL (vol Ac < 1µL)" if r["ajuste"] else ""
        recap.append({
            "Type": "Primaire", "Anticorps": p["nom"], "Boîte": p["boite"],
            "Cible": p["marquage"], "Espèce hôte": p["espece"], "Dilution": p["dilution"],
            "Démasquage": p["demasquage"], "Vol Ac (µL)": r["vol_ac"],
            "Vol tampon (µL)": r["vol_total_utilise"] - r["vol_ac"],
            "Vol total solution (µL)": r["vol_total_utilise"], "Note": note
        })

    for s in secondaires_choisis:
        vol_ac, vol_tampon, vol_utilise, ajuste = calcul_volumes(vol_total, s["dilution"], s["nom"])
        note = f"Volume ajusté à {vol_utilise} µL (vol Ac < 1µL)" if ajuste else ""
        recap.append({
            "Type": "Secondaire", "Anticorps": s["nom"], "Boîte": "Stock secondaires",
            "Cible": s["espece_cible"], "Espèce hôte": s["producteur"], "Dilution": s["dilution"],
            "Démasquage": "", "Vol Ac (µL)": vol_ac, "Vol tampon (µL)": vol_tampon,
            "Vol total solution (µL)": vol_utilise, "Note": note
        })

    df_recap = pd.DataFrame(recap)
    st.dataframe(df_recap)

    import io
    buffer = io.BytesIO()
    df_recap.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    st.download_button(
        label="⬇Télécharger le récapitulatif",
        data=buffer,
        file_name="prépa IHC.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- RAPPEL DES FORMULES ---
with st.expander("Les formules derrière l'outil - au cas où !"):
    st.markdown("""
    Si un jour l'appli est down ou que tu veux vérifier à la main, voilà comment on calcule tout ça :

    ---

    <span style='font-size:1rem; font-weight:bold;'> Volume total à préparer</span>

    C'est simplement le volume dont tu as besoin pour couvrir toutes tes lames, plus un peu de marge :
    > *Vol total = (nb lames × vol par lame) + surplus*

    ---

    <span style='font-size:1rem; font-weight:bold;'> Combien d'anticorps prélever ?</span>

    Tu divises le volume total par le facteur de dilution :
     *Vol Ac = Vol total ÷ facteur de dilution*

    Par exemple pour une dilution 1/500 avec 1400 µL : 1400 ÷ 500 = **2,8 µL d'Ac**

    Le reste, c'est du tampon anticorps : 1400 − 2,8 = **1397,2 µL de tampon**

    ---

    <span style='font-size:1rem; font-weight:bold;'>⚠️ Si le volume tombe en dessous de 1 µL...</span>

    On ne peut pas pipeter moins de 1 µL de façon fiable, donc on augmente le volume total jusqu'à obtenir au moins 1 µL d'Ac.
    *Vol total ajusté = facteur de dilution × 1*

    Exemple pour du 1/2000 : on passe à 2000 µL de solution minimum.

    ---

    <span style='font-size:1rem; font-weight:bold;'>🔬 Dilutions des secondaires</span>

    Par défaut on utilise toujours :
    - Alexa **488** → **1/400**
    - Alexa **555, 594, 546, 647** → **1/800**
    """, unsafe_allow_html=True)