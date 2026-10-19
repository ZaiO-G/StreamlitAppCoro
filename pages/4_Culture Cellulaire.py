import math
import streamlit as st
import pandas as pd
import io

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;700;800&family=Nunito+Sans:wght@400;600&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Nunito Sans', sans-serif; }
    h1 { font-family: 'Raleway', sans-serif !important; color: #00a3a6 !important; font-weight: 800 !important; font-size: 2.2rem !important; border-bottom: 3px solid #00a3a6; padding-bottom: 0.4rem; }
    h2, h3 { font-family: 'Raleway', sans-serif !important; color: #275662 !important; font-weight: 700 !important; border-bottom: 1px solid #66c1bf; padding-bottom: 0.3rem; }
    p, label, .stMarkdown { font-family: 'Nunito Sans', sans-serif !important; color: #2d2d2d !important; }
    .stAlert { background: #e8f7f7 !important; border-left: 4px solid #00a3a6 !important; border-radius: 8px !important; color: #275662 !important; }
    .stTextInput input, .stNumberInput input { background: #f5fafa !important; border: 1.5px solid #66c1bf !important; border-radius: 8px !important; color: #1e293b !important; }
    .stSelectbox div { border: none !important; border-radius: 8px !important; }
    .stSelectbox > div > div { border: 1.5px solid #66c1bf !important; border-radius: 8px !important; padding: 4px 8px !important; }
    .stButton button, .stDownloadButton button { background-color: #00a3a6 !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Raleway', sans-serif !important; font-weight: 700 !important; padding: 0.5rem 1.5rem !important; }
    .stButton button:hover, .stDownloadButton button:hover { background-color: #008c8e !important; }
    hr { border-color: #66c1bf !important; }
    .card { background: #f0fafa; border: 1.5px solid #66c1bf; border-radius: 10px; padding: 12px 18px; text-align: center; }
    .card-label { font-size: 0.72rem; color: #275662; font-weight: 600; }
    .card-value { font-size: 1.4rem; font-weight: 800; color: #00a3a6; }
    .card-accent { background: #00a3a6; border-radius: 10px; padding: 12px 18px; text-align: center; }
    .card-accent .card-label { color: #e0f7f7; }
    .card-accent .card-value { color: #ffffff; }
    .result-box { background: #f0fafa; border-left: 4px solid #00a3a6; border-radius: 8px; padding: 12px 18px; margin: 0.5rem 0; font-size: 0.9rem; color: #275662; }
    .warn-box { background: #fff8e1; border-left: 4px solid #f0a500; border-radius: 8px; padding: 12px 18px; margin: 0.5rem 0; font-size: 0.9rem; color: #7a5500; }
    .step-box { background: #f5fafa; border: 1px solid #b2dede; border-radius: 10px; padding: 14px 18px; margin: 0.4rem 0; }
    .step-num { font-family: 'Raleway', sans-serif; font-weight: 800; color: #00a3a6; font-size: 1.1rem; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

# ---------- Paramètres des supports ----------
SUPPORTS = {
    "T25":  {"surface_cm2": 25,   "vol_milieu_mL": 5,   "type": "flasque"},
    "T75":  {"surface_cm2": 75,   "vol_milieu_mL": 15,  "type": "flasque"},
    "P6":   {"surface_cm2": 9.6,  "vol_milieu_mL": 2,   "type": "plaque", "nb_puits": 6},
    "P24":  {"surface_cm2": 2,    "vol_milieu_mL": 0.5, "type": "plaque", "nb_puits": 24},
    "P48":  {"surface_cm2": 1,    "vol_milieu_mL": 0.25,"type": "plaque", "nb_puits": 48},
    "P96":  {"surface_cm2": 0.32, "vol_milieu_mL": 0.1, "type": "plaque", "nb_puits": 96},
}

st.title("Culture cellulaire - Comptage & Ensemencement")
st.write("Calcule ta concentration cellulaire à partir du comptage sur cellule de Malassez, "
         "puis planifie ton ensemencement sur le support de ton choix.")
st.divider()

def fmt_vol(vol_mL):
    """Affiche en µL si < 1 mL, en mL sinon."""
    if vol_mL >= 1:
        return f"{vol_mL:.2f} mL"
    else:
        return f"{vol_mL * 1000:.1f} µL"
# ================================================================
# SECTION 1 — PROTOCOLE DE COMPTAGE
# ================================================================
st.subheader("Étapes préalables au comptage")
st.markdown("""
<div class="step-box"><span class="step-num">1</span>
Jeter délicatement le milieu de culture en inversant la flasque de face par rapport à celle présentant la couche cellulaire, pour ne pas emporter les cellules.
</div>
<div class="step-box"><span class="step-num">2</span>
Rincer avec <b>3 mL de PBS</b>. Pipeter doucement sur les cellules, faire quelques aller-retours, puis retirer le PBS.<br>
<small style="color:#c0392b;"> ⚠️ Attention ⚠️ avec les cellules fragiles : ne <b>jamais</b> pipeter directement sur les cellules ! Ajouter le PBS sur le côté opposé aux cellules, fermer le bouchon, bouger très légèrement la flasque, puis accumuler le PBS dans un coin et retirer au Pipetman.</small>
</div>
<div class="step-box"><span class="step-num">3</span>
Ajouter <b>2-3 mL de trypsine</b>. Laisser recouvrir les cellules <b>5-10 min</b>. Vérifier en inclinant la flasque : le fond cellulaire opaque doit « couler ». Maintenir la flasque à plat, taper le bord plusieurs fois pour faciliter le décollement. Vérifier que la face est redevenue transparente (plus de film opaque).
</div>
<div class="step-box"><span class="step-num">4</span>
Ajouter <b>12 mL de milieu (DMEM ou MEM en fonction de la lignée )</b>. Effectuer plusieurs aller-retours pour séparer les cellules et homogénéiser. Prélever les <b>15 mL totaux</b> et les réserver dans des <b>Falcons 50 mL</b> annotés.
</div>
""", unsafe_allow_html=True)
st.divider()

st.subheader("Protocole de comptage")

st.markdown("""
<div class="step-box"><span class="step-num">1</span>
Prélever à partir du Falcon et diluer dans un Eppendorf distinct :<br>
<b>Au quart</b> : 5 µL cellules + 15 µL milieu &nbsp;|&nbsp; <b>Au dixième</b> : 2 µL cellules + 18 µL milieu<br>
<small style="color:#888;">Ajouter du bleu de trypan si viabilité souhaitée (mélange 1:1 avec la dilution).</small>
</div>
<div class="step-box"><span class="step-num">2</span>
Homogénéiser puis déposer <b>10 µL</b> sur la lame de Malassez.
</div>
<div class="step-box"><span class="step-num">3</span>
Compter les cellules dans <b>25 regroupements</b> de petits carrés (un regroupement = cercle rouge sur la figure).<br>
<small style="color:#888;">La grille = 100 carreaux (25×4). 1 grille entière = 1 mL = 1000 µL.</small>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="result-box" style="font-size:0.85rem;">
<b>Formule :</b><br>
Concentration (cell/mL) = n(comptage) × (carrés<sub>Tot</sub>/25) × Facteur de dilution × 1000<br>
= n(comptage) × <b>4</b> × <b>FD</b> × <b>1000</b>
</div>
""", unsafe_allow_html=True)
st.divider()

# ================================================================
# SECTION 2 — SAISIE DU COMPTAGE
# ================================================================
st.subheader("Comptage ")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Facteur de dilution**")
    fd_choix = st.selectbox("", ["Au quart (×4)", "Au dixième (×10)", "Autre"], key="fd")
    if fd_choix == "Au quart (×4)":
        fd = 4
    elif fd_choix == "Au dixième (×10)":
        fd = 10
    else:
        fd = st.number_input("Facteur de dilution personnalisé", min_value=1, value=4, key="fd_custom")

with col2:
    st.markdown("**Viabilité (bleu de trypan)**")
    trypan = st.checkbox("Exclure les cellules mortes (trypan)", value=True)

st.markdown("")
if trypan:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Cellules vivantes comptées** (claires)")
        n_vivantes = st.number_input("n vivantes", min_value=0, value=0, key="n_viv", label_visibility="collapsed")
    with col_b:
        st.markdown("**Cellules mortes comptées** (bleues)")
        n_mortes = st.number_input("n mortes", min_value=0, value=0, key="n_mort", label_visibility="collapsed")
    n_total = n_vivantes + n_mortes
    viabilite = round(n_vivantes / n_total * 100, 1) if n_total > 0 else 0
    # Avec trypan, FD est déjà ×2 (dilution 1:1 trypan) → on multiplie par 2
    conc_totale = n_total * 4 * fd * 2 * 1000  # ×2 pour la dilution trypan
    conc_vivante = n_vivantes * 4 * fd * 2 * 1000
else:
    st.markdown("**Cellules comptées (25 regroupements)**")
    n_total = st.number_input("n total", min_value=0, value=0, key="n_tot", label_visibility="collapsed")
    n_vivantes = n_total
    viabilite = None
    conc_totale = n_total * 4 * fd * 1000
    conc_vivante = conc_totale

# ---------- Résultats comptage ----------
if n_total > 0:
    st.markdown("")
    cards = [
        ("Cellules totales comptées", f"{n_total}", ""),
        ("Concentration totale", f"{conc_totale:,.0f}", "cell/mL"),
    ]
    if trypan:
        cards.append(("Concentration vivantes", f"{conc_vivante:,.0f}", "cell/mL"))
        cards.append(("Viabilité", f"{viabilite} %", ""))

    cols_cards = st.columns(len(cards))
    for i, (label, val, unit) in enumerate(cards):
        accent = (label in ["Concentration vivantes", "Viabilité"])
        cls = "card-accent" if accent else "card"
        with cols_cards[i]:
            st.markdown(
                f'<div class="{cls}"><div class="card-label">{label}</div>'
                f'<div class="card-value">{val}</div>'
                f'<div class="card-label">{unit}</div></div>',
                unsafe_allow_html=True
            )

    if trypan and viabilite < 70:
        st.markdown(
            '<div class="warn-box">⚠️ Viabilité < 70 % — vérifier l\'état de la culture avant de continuer.</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ================================================================
    # SECTION 3 — ENSEMENCEMENT
    # ================================================================
    st.subheader("Planification de l'ensemencement")

    conc_ref = conc_vivante if trypan else conc_totale
    st.markdown(
        f'<div class="result-box">Concentration de référence utilisée pour le calcul : '
        f'<b>{conc_ref:,.0f} cell/mL</b>'
        f'{"(cellules vivantes)" if trypan else "(toutes cellules)"}</div>',
        unsafe_allow_html=True
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**Support(s) à ensemencer**")
        supports_choisis = st.multiselect(
            "", list(SUPPORTS.keys()), default=["T25", "T75"],
            key="supports", label_visibility="collapsed"
        )
 # Séparer plaques et flasques
    supports_plaque = [s for s in supports_choisis if SUPPORTS[s]["type"] == "plaque"]
    supports_flasque = [s for s in supports_choisis if SUPPORTS[s]["type"] == "flasque"]

    with col_s2:
        if supports_plaque:
            st.markdown("**Densité cible (cell/puit)**")
            densite_puit = st.number_input(
                "", min_value=100, value=50000, step=5000,
                key="densite_puit", label_visibility="collapsed"
            )
        if supports_flasque:
            st.markdown("**Densité cible (cell/mL)**")
            densite_mL = st.number_input(
                "", min_value=1000, value=300000, step=10000,
                key="densite_mL", label_visibility="collapsed"
            )

    if supports_choisis:
        recap = []
        for nom in supports_choisis:
            s = SUPPORTS[nom]
            vol_total = s["vol_milieu_mL"]
            nb_puits = s.get("nb_puits", 1)

             # Cellules nécessaires par puit/flasque
            if s["type"] == "plaque":
                cells_par_puit = densite_puit
            else:
                cells_par_puit = densite_mL * vol_total
            # Volume de suspension à prélever par puit/flasque
            vol_susp_par_puit = cells_par_puit / conc_ref  # mL
            # Volume de milieu à compléter par puit
            vol_milieu_par_puit = vol_total - vol_susp_par_puit

            # Total si plaque
            cells_total = cells_par_puit * nb_puits
            vol_susp_total = vol_susp_par_puit * nb_puits
            vol_milieu_total = vol_milieu_par_puit * nb_puits

            recap.append({
                "support": nom,
                "nb_puits": nb_puits,
                "cells_par_puit": cells_par_puit,
                "vol_susp_par_puit": vol_susp_par_puit,
                "vol_milieu_par_puit": vol_milieu_par_puit,
                "cells_total": cells_total,
                "vol_susp_total": vol_susp_total,
                "vol_milieu_total": vol_milieu_total,
                "vol_total_puit": vol_total,
                "faisable": vol_susp_par_puit <= vol_total,
            })

        st.markdown("")
        for r in recap:
            est_plaque = r["nb_puits"] > 1
            couleur_bord = "#00a3a6" if r["faisable"] else "#f0a500"
            st.markdown(
                f'<div style="border:2px solid {couleur_bord}; border-radius:12px; '
                f'padding:14px 18px; margin-bottom:12px;">',
                unsafe_allow_html=True
            )

            titre = f"{r['support']}"
            if est_plaque:
                titre += f" ({r['nb_puits']} puits)"
            st.markdown(f"**{titre}** — Volume par puit/flasque : {r['vol_total_puit']} mL")

            if not r["faisable"]:
                st.markdown(
                    '<div class="warn-box">⚠️ Volume de suspension nécessaire dépasse le volume total du support. '
                    'La concentration de ta suspension est trop faible pour atteindre la densité cible — '
                    'envisage de centrifuger et resuspendre en volume réduit.</div>',
                    unsafe_allow_html=True
                )
            else:
                if est_plaque:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(
                            f'<div class="card"><div class="card-label">Suspension / puit</div>'
                            f'<div class="card-value">{fmt_vol(vol_susp_par_puit)}</div></div>',                            unsafe_allow_html=True
                        )
                    with col2:
                        st.markdown(
                            f'<div class="card"><div class="card-label">Milieu / puit</div>'
                            f'<div class="card-value">{vol_milieu_par_puit*1000:.1f} µL</div></div>',
                            unsafe_allow_html=True
                        )
                    with col3:
                        st.markdown(
                            f'<div class="card-accent"><div class="card-label">Total suspension ({r["nb_puits"]} puits)</div>'
                            f'<div class="card-value">{vol_susp_total*1000:.1f} µL</div></div>',
                            unsafe_allow_html=True
                        )
                    st.markdown(
                        f'<div class="result-box" style="margin-top:8px; font-size:1.05rem;">Pour <b>{r["nb_puits"]} puits</b>'
                        f'prélever <b>{vol_susp_total*1000:.1f} µL</b> de suspension + '
                        f'<b>{vol_milieu_total*1000:.1f} µL</b> de milieu → mélanger, '
                        f'puis distribuer <b>{r["vol_total_puit"]*1000:.0f} µL</b> par puit.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            f'<div class="card"><div class="card-label">Suspension à prélever</div>'
                            f'<div class="card-value">{vol_susp_par_puit*1000:.1f} µL</div></div>',
                            unsafe_allow_html=True
                        )
                    with col2:
                        st.markdown(
                            f'<div class="card"><div class="card-label">Milieu à ajouter</div>'
                            f'<div class="card-value">{vol_milieu_par_puit:.2f} mL</div></div>',
                            unsafe_allow_html=True
                        )
                    st.markdown(
                        f'<div class="result-box" style="margin-top:8px; font-size:1.05rem;">'
                        f'Prélever <b>{vol_susp_par_puit*1000:.1f} µL</b> de suspension → '
                        f'compléter à <b>{r["vol_total_puit"]} mL</b> avec du milieu '
                        f'(ajouter <b>{vol_milieu_par_puit:.2f} mL</b>).</div>',
                        unsafe_allow_html=True
                    )

            st.markdown('</div>', unsafe_allow_html=True)
