from shared.auth import check_password
check_password()
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
    .result-box { background: #f0fafa; border-left: 4px solid #00a3a6; border-radius: 8px; padding: 12px 18px; margin: 0.5rem 0; font-size: 0.95rem; color: #275662; }
    .warn-box { background: #fff8e1; border-left: 4px solid #f0a500; border-radius: 8px; padding: 12px 18px; margin: 0.5rem 0; font-size: 0.9rem; color: #7a5500; }
    .step-box { background: #f5fafa; border: 1px solid #b2dede; border-radius: 10px; padding: 14px 18px; margin: 0.4rem 0; }
    .step-num { font-family: 'Raleway', sans-serif; font-weight: 800; color: #00a3a6; font-size: 1.1rem; margin-right: 8px; }
    table.plaque { border-collapse: separate; border-spacing: 4px; font-size: 0.7rem; }
    table.plaque td { width: 56px; height: 50px; text-align: center; vertical-align: middle;
        border-radius: 50%; font-weight: 600; line-height: 1.15; border: 1px solid #c9d6d6; }
    table.plaque td.empty { background: #f4f6f6; border: 1px dashed #d4dede; }
    table.plaque th { font-size: 0.78rem; color: #275662; font-weight: 700; background: transparent;
        border: none; padding: 4px; text-align: center; }
</style>
""", unsafe_allow_html=True)

COND_COLORS = [
    "#d6e8ff", "#ffe3cc", "#d9f2d9", "#f3d9ff", "#fff3cc", "#d9f5f5",
    "#ffd6d6", "#d6f5e3", "#fff0d6", "#e8d6ff", "#d6fff5", "#ffe8d6",
]
CTRL_COLORS = {"Non transfecté (NT)": "#e8e8e8", "Mock / lipofectamine seule": "#f5e6cc", "Plasmide contrôle": "#cce6f5"}
LETTRES = ["A", "B", "C", "D", "E", "F", "G", "H"]

SUPPORTS = {
    "P6":  {"vol_mix_uL": 250, "vol_milieu_uL": 2000, "nb_puits": 6,  "cols": 3, "rows": 2},
    "P24": {"vol_mix_uL": 100, "vol_milieu_uL": 500,  "nb_puits": 24, "cols": 6, "rows": 4},
    "P48": {"vol_mix_uL": 50,  "vol_milieu_uL": 250,  "nb_puits": 48, "cols": 8, "rows": 6},
    "P96": {"vol_mix_uL": 20,  "vol_milieu_uL": 100,  "nb_puits": 96, "cols": 12, "rows": 8},
}

SEUIL_DILUTION = 1000


def fmt_vol(vol_uL):
    if vol_uL >= 1000:
        return f"{vol_uL / 1000:.2f} mL"
    return f"{vol_uL:.1f} µL"


st.title("GFP Fusion - Préparation des transfections")
st.write("Calcule les volumes de tes mix plasmide et lipofectamine, puis visualise le plan de plaque suggéré.")
st.divider()

# ================================================================
# PROTOCOLE
# ================================================================
st.subheader("Rappel du protocole")

st.markdown("""
<div class="step-box"><span class="step-num">1</span>
Préparer <b>deux mix séparément</b> dans un Eppendorf :<br>
&bull; <b>Mix plasmide</b> : V<sub>plasmide</sub> (pour X ng) + optiMEM qsp demi-volume final.<br>
&bull; <b>Mix lipofectamine</b> (commun à toutes les conditions) : lipofectamine + optiMEM qsp demi-volume final.<br>
Homogénéiser chaque mix, puis mélanger plasmide + lipo pour chaque condition. Laisser <b>30 min à TA</b>.
</div>
<div class="step-box" style="background:#fff8e1; border-color:#f0a500;">
<span class="step-num" style="color:#f0a500;">⚠️</span>
Si le plasmide a une concentration &gt; 1000 ng/µL, préparer une <b>dilution intermédiaire au 1/10</b>
dans de l'eau stérile ou de l'optiMEM avant de constituer le mix.
</div>
<div class="step-box"><span class="step-num">2</span>
Pendant l'incubation : préparer le <b>milieu de culture de transfection</b> (DMEM sans SVF).<br>
<small style="color:#888;">Si l'expérience nécessite de la trypsine ou du PBS, préparer les milieux conditionnés
(ex. trypsine 0.05 % : C<sub>i</sub> = 0.5 mg/mL → C<sub>f</sub> = 10 µg/mL dans DMEM sans SVF).</small>
</div>
<div class="step-box"><span class="step-num">3</span>
Retirer le milieu DMEM + SVF des puits. Ajouter le milieu de transfection (DMEM sans SVF ± PBS/trypsine).
</div>
<div class="step-box"><span class="step-num">4</span>
Déposer le mix final <b>goutte à goutte</b> sur les cellules, au plus proche de la surface du milieu.<br>
<small style="color:#888;">Vérifier au microscope que la transfection n'a pas décollé les cellules.</small>
</div>
<div class="step-box"><span class="step-num">5</span>
Incuber à <b>37 °C / CO₂ 5 %</b> pendant <b>24 h</b>.
</div>
""", unsafe_allow_html=True)
st.divider()

# ================================================================
# PARAMÈTRES GÉNÉRAUX
# ================================================================
st.subheader("Paramètres généraux")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Format de plaque**")
    support = st.selectbox("", list(SUPPORTS.keys()), index=2, key="support", label_visibility="collapsed")
with c2:
    st.markdown("**ADN total par puit (ng)**")
    adn_par_puit = st.number_input("", min_value=1, value=250, step=50, key="adn", label_visibility="collapsed")
with c3:
    st.markdown("**Lipofectamine par puit (µL)**")
    lipo_par_puit = st.number_input("", min_value=0.1, value=1.0, step=0.5, key="lipo_puit",
                                    label_visibility="collapsed")

sup = SUPPORTS[support]
vol_mix = sup["vol_mix_uL"]
demi_vol = vol_mix / 2

st.markdown(
    f'<div class="result-box">Format <b>{support}</b> — volume de mix final : <b>{vol_mix} µL/puit</b> '
    f'(2 × {demi_vol:.0f} µL) - lipofectamine : <b>{lipo_par_puit:.2f} µL/puit</b></div>',
    unsafe_allow_html=True
)
st.divider()

# ================================================================
# CONDITIONS
# ================================================================
st.subheader("Conditions de transfection")

nb_conditions = st.number_input("Nombre de conditions", min_value=1, value=3, key="nb_cond")

sc1, sc2 = st.columns(2)
with sc1:
    st.markdown("**Nombre de puits par condition**")
    nb_puits = st.number_input("", min_value=1, value=5, key="nb_puits", label_visibility="collapsed")
with sc2:
    st.markdown("**Puits de surplus**")
    surplus = st.number_input("", min_value=0, value=1, key="surplus", label_visibility="collapsed")

nb_puits_prep = nb_puits + surplus
st.divider()

conditions = []
for ci in range(int(nb_conditions)):
    st.markdown(f"#### Condition {ci + 1}")
    nom_cond = st.text_input("Nom", value=f"Condition {ci + 1}", key=f"nom_cond_{ci}")
    co_transf = st.checkbox("Co-transfection", key=f"co_{ci}")
    nb_plasm = int(st.number_input("Nb plasmides", min_value=2, value=2, key=f"nb_plasm_{ci}")) if co_transf else 1

    plasmides = []
    for pi in range(nb_plasm):
        cols = st.columns([2, 1, 1])
        with cols[0]:
            p_nom = st.text_input(f"Plasmide {pi+1}", value=f"Plasmide {pi+1}", key=f"pnom_{ci}_{pi}")
        with cols[1]:
            p_ng = st.number_input("ng/puit", min_value=1,
                                   value=adn_par_puit if nb_plasm == 1 else adn_par_puit // nb_plasm,
                                   key=f"png_{ci}_{pi}")
        with cols[2]:
            p_conc = st.number_input("Conc. (ng/µL)", min_value=1.0, value=500.0, key=f"pconc_{ci}_{pi}")
        plasmides.append({"nom": p_nom, "ng": p_ng, "conc": p_conc})

    total_ng = sum(p["ng"] for p in plasmides)
    if total_ng != adn_par_puit:
        st.markdown(
            f'<div class="warn-box">⚠️Total ADN : <b>{total_ng} ng</b> (attendu : {adn_par_puit} ng).</div>',
            unsafe_allow_html=True)

    conditions.append({"nom": nom_cond, "plasmides": plasmides,
                       "color": COND_COLORS[ci % len(COND_COLORS)]})
    st.markdown("---")

# ================================================================
# CONTRÔLES
# ================================================================
st.subheader("Contrôles")
ctrl_options = ["Non transfecté (NT)", "Mock / lipofectamine seule", "Plasmide contrôle"]
ctrl_choisis = st.multiselect("Sélectionne tes contrôles", ctrl_options, default=["Non transfecté (NT)"])

controles = []
for ctrl in ctrl_choisis:
    if ctrl == "Plasmide contrôle":
        cc1, cc2 = st.columns(2)
        with cc1:
            ctrl_nom = st.text_input("Plasmide contrôle", value="pEGFP", key="ctrl_plasm_nom")
        with cc2:
            ctrl_conc = st.number_input("Conc. (ng/µL)", min_value=1.0, value=500.0, key="ctrl_plasm_conc")
        controles.append({"type": ctrl, "nom": ctrl_nom,
                          "plasmides": [{"nom": ctrl_nom, "ng": adn_par_puit, "conc": ctrl_conc}],
                          "color": CTRL_COLORS[ctrl]})
    elif ctrl == "Mock / lipofectamine seule":
        controles.append({"type": ctrl, "nom": "Mock", "plasmides": [], "color": CTRL_COLORS[ctrl]})
    else:
        controles.append({"type": ctrl, "nom": "NT", "plasmides": [], "color": CTRL_COLORS[ctrl]})

st.divider()

# ================================================================
# PLAN DE PLAQUE SUGGÉRÉ
# ================================================================
st.subheader("Plan de plaque suggéré")

all_items = conditions + controles
plate_cols = sup["cols"]
plate_rows = sup["rows"]
plaque = [[None] * plate_cols for _ in range(plate_rows)]

# Remplissage par condition, ligne par ligne
idx = 0
for item in all_items:
    nom = item.get("nom", "")
    color = item.get("color", "#e8e8e8")
    for _ in range(nb_puits):
        r, c = divmod(idx, plate_cols)
        if r < plate_rows:
            plaque[r][c] = {"label": nom, "color": color}
        idx += 1

# Rendu HTML
html = '<div style="overflow-x:auto; margin:1rem 0;"><table class="plaque">'
html += '<tr><th></th>'
for c in range(1, plate_cols + 1):
    html += f'<th>{c}</th>'
html += '</tr>'
for r in range(plate_rows):
    html += f'<tr><th>{LETTRES[r]}</th>'
    for c in range(plate_cols):
        cell = plaque[r][c]
        if cell is None:
            html += '<td class="empty"></td>'
        else:
            # Raccourcir le label si besoin
            lab = cell["label"]
            if len(lab) > 8:
                lab = lab[:7] + "…"
            html += f'<td style="background:{cell["color"]};">{lab}</td>'
    html += '</tr>'
html += '</table></div>'
st.markdown(html, unsafe_allow_html=True)

# Légende
leg_items = [(item.get("nom", ""), item.get("color", "#e8e8e8")) for item in all_items]
cols_leg = st.columns(min(len(leg_items), 6))
for i, (label, couleur) in enumerate(leg_items):
    with cols_leg[i % len(cols_leg)]:
        st.markdown(
            f'<span style="background:{couleur}; padding:4px 10px; border-radius:6px; '
            f'font-size:0.8rem; font-weight:600; border:1px solid rgba(0,0,0,0.08);">{label}</span>',
            unsafe_allow_html=True)

nb_total_plaque = sum(nb_puits for _ in all_items)
st.caption(f"Utilisation : **{min(nb_total_plaque, sup['nb_puits'])} / {sup['nb_puits']} puits**")
st.divider()

# ================================================================
# CALCULS — MIX LIPOFECTAMINE POOLÉ
# ================================================================
st.subheader("Récapitulatif des mix")

# Compter les puits nécessitant de la lipo (tout sauf NT)
nb_puits_lipo = sum(nb_puits_prep for item in all_items
                    if item.get("type", "") != "Non transfecté (NT)")
vol_lipo_pool = lipo_par_puit * nb_puits_lipo
vol_optimem_lipo_pool = demi_vol * nb_puits_lipo - vol_lipo_pool

st.markdown(
    f'<div class="result-box" style="font-size:1.05rem;">'
    f'<b>Mix lipofectamine commun</b> (pour {nb_puits_lipo} puits, surplus inclus) :<br>'
    f'&bull; Lipofectamine 2000 : <b>{fmt_vol(vol_lipo_pool)}</b><br>'
    f'&bull; optiMEM : <b>{fmt_vol(vol_optimem_lipo_pool)}</b><br>'
    f'Aliquoter ensuite <b>{fmt_vol(demi_vol * nb_puits_prep)}</b> par condition ({demi_vol:.0f} µL × {nb_puits_prep} puits) avant de mélanger avec le mix plasmide.</div>',
    unsafe_allow_html=True
)
st.markdown("")

# Mix plasmide par condition
all_mixes = []
for item in all_items:
    nom = item.get("nom", "")
    plasmides = item.get("plasmides", [])
    is_nt = item.get("type", "") == "Non transfecté (NT)"
    is_mock = item.get("type", "") == "Mock / lipofectamine seule"

    vol_plasm_details = []
    vol_plasm_total = 0
    dilution_warning = False

    for p in plasmides:
        dilue = p["conc"] > SEUIL_DILUTION
        conc_eff = p["conc"] / 10 if dilue else p["conc"]
        v_uL = p["ng"] / conc_eff
        if dilue:
            dilution_warning = True
        vol_plasm_details.append({
            "nom": p["nom"], "ng": p["ng"],
            "conc_stock": p["conc"], "conc_eff": conc_eff, "dilue": dilue,
            "vol_1puit": v_uL, "vol_total": v_uL * nb_puits_prep,
        })
        vol_plasm_total += v_uL

    vol_optimem_plasm_1 = demi_vol - vol_plasm_total
    vol_optimem_plasm = vol_optimem_plasm_1 * nb_puits_prep

    all_mixes.append({
        "nom": nom, "is_nt": is_nt, "is_mock": is_mock,
        "plasmides": vol_plasm_details,
        "vol_optimem_plasm": vol_optimem_plasm,
        "vol_mix_total": vol_mix * nb_puits_prep,
        "dilution_warning": dilution_warning,
        "nb_puits": nb_puits_prep,
    })

# Affichage par condition
for mix in all_mixes:
    couleur_bord = "#f0a500" if mix["dilution_warning"] else "#00a3a6"
    st.markdown(
        f'<div style="border:2px solid {couleur_bord}; border-radius:12px; '
        f'padding:16px 20px; margin-bottom:14px;">',
        unsafe_allow_html=True)

    st.markdown(f"**{mix['nom']}** - {mix['nb_puits']} puits ({nb_puits} + {surplus} surplus)")

    if mix["is_nt"]:
        st.markdown(
            '<div class="result-box">Contrôle non transfecté — aucun mix à préparer.</div>',
            unsafe_allow_html=True)
    else:
        if mix["plasmides"]:
            plasm_html = f"<b>Mix plasmide</b> ({mix['nb_puits']} puits) :<br>"
            for p in mix["plasmides"]:
                if p["dilue"]:
                    plasm_html += (
                        f"&bull; {p['nom']} : <small>stock {p['conc_stock']:.0f} ng/µL "
                        f"→ dilué 1/10 → <b>{p['conc_eff']:.1f} ng/µL</b></small><br>"
                        f"&nbsp;&nbsp;&nbsp;{p['ng']} ng/puit ÷ {p['conc_eff']:.1f} ng/µL "
                        f"→ <b>{fmt_vol(p['vol_1puit'])}/puit</b> "
                        f"→ total <b>{fmt_vol(p['vol_total'])}</b><br>")
                else:
                    plasm_html += (
                        f"&bull; {p['nom']} : {p['ng']} ng/puit ÷ {p['conc_stock']:.0f} ng/µL "
                        f"→ <b>{fmt_vol(p['vol_1puit'])}/puit</b> "
                        f"→ total <b>{fmt_vol(p['vol_total'])}</b><br>")
            plasm_html += f"&bull; optiMEM qsp : <b>{fmt_vol(mix['vol_optimem_plasm'])}</b>"
            st.markdown(f'<div class="result-box">{plasm_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="result-box"><b>Mix plasmide</b> : mock - optiMEM seul : '
                f'<b>{fmt_vol(demi_vol * mix["nb_puits"])}</b></div>',
                unsafe_allow_html=True)

        st.markdown(
            f'<div class="result-box" style="font-size:1.05rem;">'
            f'Ajouter <b>{fmt_vol(demi_vol * nb_puits_prep)}</b> du mix lipofectamine commun ({nb_puits_prep} puits) → '
            f'volume final : <b>{fmt_vol(mix["vol_mix_total"])}</b> '
            f'→ déposer <b>{vol_mix} µL/puit</b> goutte à goutte.</div>',
            unsafe_allow_html=True)

        if mix["dilution_warning"]:
            st.markdown(
                '<div class="warn-box">⚠️ Concentration &gt; 1000 ng/µL — '
                'préparer une <b>dilution au 1/10</b> avant de constituer le mix.</div>',
                unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
# ================================================================
# MILIEU DE TRANSFECTION
# ================================================================
st.subheader("Préparation du milieu de transfection")
st.caption("À préparer pendant les 30 min d'incubation du mix plasmide/lipofectamine OptiMEM.")

mc1, mc2 = st.columns(2)
with mc1:
    st.markdown("**Volume de milieu par puit (µL)**")
    vol_milieu_puit = st.number_input("", min_value=50, value=300, step=50,
                                      key="vol_milieu_puit", label_visibility="collapsed")
with mc2:
    st.markdown("**Conditions milieu**")
    milieu_options = st.multiselect("", ["+ PBS", "+ Trypsine"], default=["+ PBS", "+ Trypsine"],
                                    key="milieu_opts", label_visibility="collapsed")

# Nombre total de puits pour le milieu (toutes conditions + contrôles)
nb_puits_milieu = nb_puits * len(all_items)
vol_milieu_total = vol_milieu_puit * nb_puits_milieu  # µL

# Trypsine : Ci = 0.5 mg/mL = 500 µg/mL, Cf = 10 µg/mL
CI_TRYP = 500   # µg/mL
CF_TRYP = 10    # µg/mL

for opt in milieu_options:
    st.markdown(f"#### Milieu DMEM sans SVF {opt}")

    if opt == "+ Trypsine":
        vol_tryp = vol_milieu_total * CF_TRYP / CI_TRYP  # µL
        vol_dmem = vol_milieu_total - vol_tryp

        st.markdown(
            f'<div class="result-box" style="font-size:1.05rem;">'
            f'Pour <b>{nb_puits_milieu} puits</b> × {vol_milieu_puit} µL = '
            f'<b>{fmt_vol(vol_milieu_total)}</b> de milieu total :<br><br>'
            f'&bull; Trypsine 0.05 % (C<sub>i</sub> = 0.5 mg/mL → C<sub>f</sub> = 10 µg/mL) : '
            f'<b>{fmt_vol(vol_tryp)}</b><br>'
            f'&bull; DMEM sans SVF : <b>{fmt_vol(vol_dmem)}</b><br><br>'
            f'<small>Dans un Falcon 15 mL : {fmt_vol(vol_tryp)} de trypsine fraîche + '
            f'{fmt_vol(vol_dmem)} de DMEM sans SVF.</small></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-box" style="font-size:1.05rem;">'
            f'Pour <b>{nb_puits_milieu} puits</b> × {vol_milieu_puit} µL = '
            f'<b>{fmt_vol(vol_milieu_total)}</b> de milieu total :<br><br>'
            f'&bull; PBS : même volume que le milieu → <b>{fmt_vol(vol_milieu_total)}</b><br>'
            f'&bull; DMEM sans SVF : <b>{fmt_vol(vol_milieu_total)}</b><br><br>'
            f'<small>Préparer séparément dans un Falcon 15 mL.</small></div>',
            unsafe_allow_html=True
        )

st.divider()
# ================================================================
# EXPORT
# ================================================================
st.divider()

export_data = []
for mix in all_mixes:
    row = {"Condition": mix["nom"], "Nb puits (surplus incl.)": mix["nb_puits"]}
    if mix["is_nt"]:
        row["Type"] = "Non transfecté"
    elif mix["is_mock"]:
        row["Type"] = "Mock"
    else:
        row["Type"] = "Transfection"
    for p in mix["plasmides"]:
        row[f"{p['nom']} (µL total)"] = round(p["vol_total"], 2)
        if p.get("dilue"):
            row[f"{p['nom']} conc. effective (ng/µL)"] = round(p["conc_eff"], 1)
    row["optiMEM plasmide (µL)"] = round(mix["vol_optimem_plasm"], 2)
    row["Mix total (µL)"] = round(mix["vol_mix_total"], 2)
    export_data.append(row)

# Ajouter ligne lipo poolée
export_data.append({
    "Condition": "Mix lipofectamine commun",
    "Nb puits (surplus incl.)": nb_puits_lipo,
    "Type": "Pool",
    "optiMEM plasmide (µL)": round(vol_optimem_lipo_pool, 2),
    f"Lipofectamine 2000 (µL)": round(vol_lipo_pool, 2),
})

df_export = pd.DataFrame(export_data)
st.dataframe(df_export, use_container_width=True, hide_index=True)

buffer = io.BytesIO()
df_export.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)
st.download_button(
    "Télécharge le récapitulatif",
    data=buffer,
    file_name="transfection_mix.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)