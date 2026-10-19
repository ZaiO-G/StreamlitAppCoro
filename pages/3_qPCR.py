import math
import re
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
    .stTextInput input, .stNumberInput input { background: #f5fafa !important; border: 1.5px solid #66c1bf !important; border-radius: 8px !important; color: #1e293b !important; }
stSelectbox div { border: none !important; border-radius: 8px !important; }
.stSelectbox > div > div { border: 1.5px solid #66c1bf !important; border-radius: 8px !important; padding: 4px 8px !important; }
.stSelectbox { margin-bottom: 1rem !important; }
[data-testid="stSelectbox"] label { font-size: 0.9rem !important; color: #275662 !important; font-weight: 600 !important; margin-bottom: 4px !important; }
    .stButton button, .stDownloadButton button { background-color: #00a3a6 !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Raleway', sans-serif !important; font-weight: 700 !important; padding: 0.5rem 1.5rem !important; }
    .stButton button:hover, .stDownloadButton button:hover { background-color: #008c8e !important; }
    .stDataFrame { border-radius: 10px !important; border: 1px solid #66c1bf !important; }
    hr { border-color: #66c1bf !important; }
    section[data-testid="stSidebar"] { background-color: #f5fafa !important; border-right: 2px solid #66c1bf !important; }

    .plaque-container { overflow-x: auto; margin: 1rem 0; padding-bottom: 6px; }
    table.plaque { border-collapse: separate; border-spacing: 4px; font-size: 0.72rem; }
    table.plaque td { width: 56px; height: 52px; text-align: center; vertical-align: middle;
        border-radius: 50%; font-weight: 600; line-height: 1.15; border: 1px solid #c9d6d6; }
    table.plaque td.empty { background: #f4f6f6; border: 1px dashed #d4dede; }
    table.plaque td small { color: #555; font-size: 0.56rem; }
    table.plaque th { font-size: 0.8rem; color: #275662; font-weight: 700; background: transparent; border: none; padding: 4px; text-align: center; }
    table.plaque th.corner { background: transparent; }
    table.plaque th.colnum { text-align: center; }
    table.plaque th.rowlab { font-size: 0.72rem; text-align:center; padding-right: 6px; white-space: nowrap; }
   table.plaque th.tissue { background: #a35bd1; border-radius: 8px; text-align: center; padding: 4px 8px; color: #ffffff; }
    table.plaque th.gene { color: #275662; }
    table.plaque th.rep { color: #c0392b; font-weight: 600; font-size: 0.66rem; }
    table.plaque th.rowlet { text-align: center; color: #275662; }
    table.plaque th.band { color: #ffffff; border-radius: 6px; padding: 4px 0; }
    .legende-pill { padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

# ---------- Palettes ----------
GROUP_FILL = [ "#d6e8ff", "#ffe3cc", "#d9f2d9", "#f3d9ff", "#fff3cc", "#d9f5f5",
    "#ffd6d6", "#d6f5e3", "#fff0d6", "#e8d6ff", "#d6fff5", "#ffe8d6",
    "#dff5d6", "#f5d6e8", "#d6e8f5", "#f5f5d6", "#f5d6d6", "#d6d6f5",
    "#e8f5d6", "#f5e8d6",]
GROUP_HEAD = [ "#3b82c4", "#e07b39", "#4fa04f", "#a35bd1", "#c9a227", "#2e9e9e",
    "#c43b3b", "#2e9e6b", "#c47a3b", "#030303", "#3bc4b8", "#c4633b",
    "#5bc43b", "#c43b8f", "#3b6bc4", "#a0a02e", "#c43b3b", "#3b3bc4",
    "#6bc43b", "#c4973b",]
SAMPLE_FILL = "#edf1f3"  # couleur unique des échantillons quand il n'y a pas de sous-groupes
GAMME_FILL = ["#ffd9d9", "#d9d9ff", "#d9ffd9", "#fff0d9"]
TISSUE_FILL = ["#c1bbfa", "#0da1a7", "#c1ecd2", "#f7ada0"]
LETTRES = ["A", "B", "C", "D", "E", "F", "G", "H"]
GAMME_LABELS = ["Pur", "1/3", "1/9", "1/27", "1/81", "H2O"]
DUP = 2  # réplicats techniques (fixé à 2 pour cette disposition matricielle)

KITS = {
    "Takara ExTaq TB Green": {
        "premix": 12.5, "amorce_s": 0.5, "amorce_as": 0.5,
        "eau": 9.5, "echantillon": 2.0, "total_mix": 23.0, "total_puit": 25.0,
    },
    "BioRad iTaq SYBR Green": {
        "premix": 10.0, "amorce_s": 1.5, "amorce_as": 1.5,
        "eau": 2.0, "echantillon": 5.0, "total_mix": 15.0, "total_puit": 20.0,
    },
}


def _split_code(code):
    """'3.1' -> ('3.', 1) ; '12' -> ('', 12) ; 'ctrl' -> None (pas de suffixe entier)."""
    m = re.match(r"^(.*?)(\d+)$", code)
    return (m.group(1), int(m.group(2))) if m else None


def parse_ids(s):
    """Sépare sur , et ;. Étend les plages en gardant le préfixe du code animal :
    '6-9' -> 6,7,8,9 ; '3.1-3.3' (ou '3.1-3') -> 3.1,3.2,3.3. Le reste est pris tel quel."""
    out = []
    for tok in re.split(r"[;,]", s):
        tok = tok.strip()
        if not tok:
            continue
        if "-" in tok:
            a, b = (p.strip() for p in tok.split("-", 1))
            pa, pb = _split_code(a), _split_code(b)
            if pa and pb and pa[1] <= pb[1]:
                # même préfixe des deux côtés ('3.1-3.3'), ou borne droite nue ('3.1-3')
                if pa[0] == pb[0] or pb[0] == "":
                    out.extend(f"{pa[0]}{n}" for n in range(pa[1], pb[1] + 1))
                    continue
        out.append(tok)
    return out


st.title("Planification manip qPCR")
st.write("Génère un plan de plaque pour la qPCR et le mix nécéssaire, bonne manip! ")
st.divider()
# ---------- TISSUS ----------
st.subheader("Tissus")
DEF_TISSUS = ["PO", "BO", "RE", "MO"]
nb_tissus = st.number_input("Nombre de tissus", 1, 4, 2)
tissues = []
cols_t = st.columns(min(nb_tissus, 4))
for i in range(nb_tissus):
    with cols_t[i % 4]:
        tissues.append(st.text_input(f"Tissu {i+1}", value=DEF_TISSUS[i], key=f"tissu_{i}"))
        TISSUE_FILL[i % len(TISSUE_FILL)] = st.color_picker(
            "Couleur", value=TISSUE_FILL[i % len(TISSUE_FILL)], key=f"tcol_{i}")
st.divider()

st.subheader("Échantillons")
avec_sous_groupes = st.checkbox(
    "Répartir en sous-groupes (WT, KO…)", value=True,
    help="Décoche si tous les échantillons sont du même type : ils auront une couleur unique, "
         "et la distinction se fera par tissu.")
 
groups = []
if avec_sous_groupes:
    st.caption("Un sous-groupe = une condition (WT, KO,NI…). Dans IDs : liste séparée par `,` ou `;`, "
               "ou plage avec un tiret (`6-9`, `3.1-3.3`).")
    DEF_GRP = [(f"Groupe {i+1}", "") for i in range(50)]
    DEF_GRP[0] = ("WT", "")
    DEF_GRP[1] = ("KO", "")
    nb_groupes = st.number_input("Nombre de sous-groupes", min_value=1, value=2)
    for i in range(nb_groupes):
        gc1, gc2, gc3 = st.columns([1, 2, 0.4])
        with gc1:
            gname = st.text_input(f"Sous-groupe {i+1}", value=DEF_GRP[i][0], key=f"grp_{i}")
        with gc2:
            gids = st.text_input("IDs", value=DEF_GRP[i][1], key=f"ids_{i}")
        with gc3:
            fill = st.color_picker("", value=GROUP_FILL[i % len(GROUP_FILL)], key=f"gcol_{i}")
        ids = parse_ids(gids)
        if ids:
            groups.append({"name": gname, "ids": ids,
                           "fill": fill,
                           "head": fill})
else:
    st.caption("Liste tous les échantillons dans un seul champ, séparés par `,` ou `;`, "
               "ou en plage avec un tiret (`1-10`, `P1-P10`).")
    ids = parse_ids(st.text_input("IDs des échantillons", value=""))
    if ids:
        groups.append({"name": "Échantillons", "ids": ids,
                       "fill": TISSUE_FILL[0], "head": "#6b7280"})
# ---------- GÈNES ----------
st.subheader("Gènes à tester")
DEF_GENES = ["Actine B", "PVM", "Gène 3", "Gène 4"]
nb_genes = st.number_input("Nombre de gènes", 1, 4, 2)
genes = []
cols_g = st.columns(min(nb_genes, 4))
for i in range(nb_genes):
    with cols_g[i % 4]:
        genes.append(st.text_input(f"Gène {i+1}", value=DEF_GENES[i], key=f"gene_{i}"))

# Colonnes d'échantillons (ordre des groupes)
sample_cols = []  # (group_name, sample_id, fill)
for g in groups:
    for sid in g["ids"]:
        sample_cols.append((g["name"], sid, g["fill"]))
n_sample_cols = len(sample_cols)
 
resume = " + ".join(f"{g['name']} ({len(g['ids'])})" for g in groups) if groups else "—"
st.info(f"**{n_sample_cols} échantillons** - {resume}")
st.divider()
 
# ---------- CONTRÔLES DE FAISABILITÉ ----------
gamme_cols = math.ceil(nb_genes / 2) * 3
n_blocs_ech = math.ceil(n_sample_cols / 12)  # blocs de rangées nécessaires pour les échantillons
n_row_pairs = n_blocs_ech * nb_tissus * nb_genes
gamme_en_bas = n_sample_cols + gamme_cols > 12 or n_sample_cols > 12

erreurs = []
if n_sample_cols == 0:
    erreurs.append("Aucun échantillon renseigné: renseigne ton ID d'échantillon (DPI.N°Souris).")
n_row_pairs_max = 3 if gamme_en_bas else 4
if n_row_pairs > n_row_pairs_max:
    erreurs.append(
        f"{n_row_pairs} blocs de rangées nécessaires, "
        f"mais seulement {n_row_pairs_max} disponibles "
        f"({'G-H réservés à la gamme' if gamme_en_bas else 'plaque pleine'})."
    )
if erreurs:
    for e in erreurs:
        st.error("⚠️ " + e)
    st.stop()

# ---------- CONSTRUCTION DE LA PLAQUE ----------
plaque = [[None] * 12 for _ in range(8)]

# Phase 1 : échantillons — un bloc de 2 rangées par (tissu, gène)
row_pairs = [(t, g) for t in tissues for g in genes]   # ordre : pour chaque tissu, chaque gène
for i, (tissue, gene) in enumerate(row_pairs):
    for c, (gname, sid, fill) in enumerate(sample_cols):
        bloc = c // 12        # 0 = colonnes 1-12, 1 = colonnes 1-12 du bloc suivant
        col = c % 12
        r1 = (i + bloc * nb_tissus * nb_genes) * 2
        r2 = r1 + 1
        limite = 6 if gamme_en_bas else 8
        if r1 < limite and r2 < limite:
            t_idx = tissues.index(tissue)
            couleur = TISSUE_FILL[t_idx % len(TISSUE_FILL)] if not avec_sous_groupes else fill
            plaque[r1][col] = {"label": sid, "color": couleur, "kind": "sample"}
            plaque[r2][col] = {"label": sid, "color": couleur, "kind": "sample"}

# Phase 2 : gammes — une gamme par gène, 4 rangées × 3 colonnes à droite
if not gamme_en_bas:
    gamme_col0 = n_sample_cols
    for gi, gene in enumerate(genes):
        block = gi // 2
        half = gi % 2
        base_col = gamme_col0 + block * 3
        base_pair = half * 2
        fill = GAMME_FILL[gi % len(GAMME_FILL)]
        for k, lab in enumerate(GAMME_LABELS):
            rp = base_pair + (k // 3)
            col = base_col + (k % 3)
            r1, r2 = 2 * rp, 2 * rp + 1
            if r2 < 8 and col < 12:
                plaque[r1][col] = {"label": lab, "color": fill, "kind": "gamme", "gene": gene}
                plaque[r2][col] = {"label": lab, "color": fill, "kind": "gamme", "gene": gene}
else:
    for gi, gene in enumerate(genes):
        fill = GAMME_FILL[gi % len(GAMME_FILL)]
        base_col = gi * 6
        for k, lab in enumerate(GAMME_LABELS):
            col = base_col + k
            if col < 12:
                plaque[6][col] = {"label": lab, "color": fill, "kind": "gamme", "gene": gene}
                plaque[7][col] = {"label": lab, "color": fill, "kind": "gamme", "gene": gene}

# ---------- AFFICHAGE DU PLAN ----------
st.subheader("Plan de plaque")

used = sum(1 for r in range(8) for c in range(12) if plaque[r][c] is not None)
st.caption(f"Utilisation : **{used} / 96 puits**")

rows_per_tissue = nb_genes * DUP * n_blocs_ech
sample_rows = nb_tissus * rows_per_tissue


def row_meta(r):
    if r >= sample_rows:
        return None, None, False, False
    t_idx = r // rows_per_tissue
    wti = r % rows_per_tissue
    g_idx = (wti // DUP) % nb_genes   # ignore le numéro de bloc
    is_tissue_first = (wti == 0)
    is_pair_first = (wti % DUP == 0)
    return t_idx, g_idx, is_tissue_first, is_pair_first


html = '<div class="plaque-container"><table class="plaque">'

# Bandeau groupes + gamme
html += '<tr><th colspan="3" class="corner"></th>'
html += '<th colspan="12"></th>'
html += '</tr>'

# Numéros de colonnes
html += '<tr><th colspan="3" class="corner"></th>'
for c in range(1, 13):
    html += f'<th class="colnum">{c}</th>'
html += '</tr>'

# Rangées
for r in range(8):
    html += '<tr>'
    t_idx, g_idx, is_tissue_first, is_pair_first = row_meta(r)
    # Colonne tissu
    if t_idx is not None and is_tissue_first:
        tcol = TISSUE_FILL[t_idx % len(TISSUE_FILL)]
        html += f'<th class="rowlab tissue" rowspan="{rows_per_tissue}" style="background:{tcol};">{tissues[t_idx]}</th>'
    elif t_idx is None:
        html += '<th class="rowlab"></th>'
    # Colonne gène / réplicats
    if t_idx is not None:
        if is_pair_first:
            html += f'<th class="rowlab gene">{genes[g_idx]}</th>'
        else:
            html += '<th class="rowlab rep">Réplicats</th>'
    else:
        html += '<th class="rowlab"></th>'
    # Lettre de rangée
    html += f'<th class="rowlet">{LETTRES[r]}</th>'
    # Puits
    for c in range(12):
        cell = plaque[r][c]
        if cell is None:
            html += '<td class="empty"></td>'
        elif cell["kind"] == "gamme":
            html += f'<td style="background:{cell["color"]};">{cell["label"]}<br><small>{cell["gene"]}</small></td>'
        else:
            html += f'<td style="background:{cell["color"]};">{cell["label"]}</td>'
    html += '</tr>'
html += '</table></div>'
st.markdown(html, unsafe_allow_html=True)

# Légende
st.markdown("")
legende = [(g["name"], g["fill"]) for g in groups]
legende += [(f"Gamme {genes[gi]}", GAMME_FILL[gi % len(GAMME_FILL)]) for gi in range(nb_genes)]
cols_leg = st.columns(min(len(legende), 6))
for idx, (label, couleur) in enumerate(legende):
    with cols_leg[idx % len(cols_leg)]:
        st.markdown(f'<span class="legende-pill" style="background:{couleur};">{label}</span>', unsafe_allow_html=True)
st.divider()
# ---------- KIT ----------
st.subheader("Kit SYBR utilisé")
kit_choisi = st.selectbox("Quel kit utilises-tu ?", list(KITS.keys()))
kit = KITS[kit_choisi]

infos_kit = [
    ("Pré-mix", kit["premix"]),
    ("Amorce S", kit["amorce_s"]),
    ("Amorce AS", kit["amorce_as"]),
    ("Eau RNAse Free", kit["eau"]),
    ("ADNc", kit["echantillon"]),
]
cards_html = '<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:0.5rem;">'
for label, val in infos_kit:
    cards_html += f'''
    <div style="background:#f0fafa; border:1.5px solid #66c1bf; border-radius:10px;
                padding:10px 16px; min-width:100px; text-align:center;">
        <div style="font-size:0.72rem; color:#275662; font-weight:600;">{label}</div>
        <div style="font-size:1.3rem; font-weight:800; color:#00a3a6;">{val} µL</div>
    </div>'''
cards_html += f'''
    <div style="background:#00a3a6; border-radius:10px;
                padding:10px 16px; min-width:120px; text-align:center; align-self:center;">
        <div style="font-size:0.72rem; color:#e0f7f7; font-weight:600;">Total / puit</div>
        <div style="font-size:1.3rem; font-weight:800; color:#ffffff;">{kit["total_puit"]} µL</div>
    </div>'''
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)
st.divider()

# ---------- MIX ----------
st.subheader("Mix à préparer")

wells_per_gene = n_sample_cols * nb_tissus * DUP + len(GAMME_LABELS) * DUP
surplus = st.number_input("Puits de surplus", 0, 50, 5,
                          help="Puits supplémentaires pour compenser les pertes de pipetage.")
wells_prep = wells_per_gene + surplus

st.markdown(
    f'<div style="background:#f0fafa; border-left:4px solid #00a3a6; border-radius:8px; '
    f'padding:10px 16px; margin-bottom:1rem; font-size:0.9rem; color:#275662;">'
    f'Par gène : <b>{wells_per_gene} puits</b> '
    f'({n_sample_cols} éch. × {nb_tissus} tissu(s) × {DUP} + {len(GAMME_LABELS)} gamme × {DUP}) '
    f'+ {surplus} surplus = <b style="color:#00a3a6; font-size:1.05rem;">{wells_prep} puits</b>'
    f'</div>',
    unsafe_allow_html=True
)

mix_data = []
for gi, gene in enumerate(genes):
    mix_data.append({
        "Gène": gene,
        "Nb puits": wells_prep,
        "Pré-mix (µL)": round(kit["premix"] * wells_prep, 1),
        "Amorce S (µL)": round(kit["amorce_s"] * wells_prep, 1),
        "Amorce AS (µL)": round(kit["amorce_as"] * wells_prep, 1),
        "H2O (µL)": round(kit["eau"] * wells_prep, 1),
        "Total mix (µL)": round(kit["total_mix"] * wells_prep, 1),
        "_couleur": GAMME_FILL[gi % len(GAMME_FILL)],
    })

# Tableau coloré par gène en HTML
cols_tab = ["Gène", "Nb puits", "Pré-mix (µL)", "Amorce S (µL)", "Amorce AS (µL)", "H2O (µL)", "Total mix (µL)"]
tab_html = '<table style="width:100%; border-collapse:separate; border-spacing:0 4px; font-size:0.85rem;">'
tab_html += '<tr>' + ''.join(
    f'<th style="text-align:left; padding:6px 10px; color:#275662; font-size:0.78rem;">{c}</th>'
    for c in cols_tab) + '</tr>'
for row in mix_data:
    bg = row["_couleur"]
    tab_html += f'<tr style="background:{bg}; border-radius:8px;">'
    for c in cols_tab:
        tab_html += f'<td style="padding:8px 10px; border-radius:6px;">{row[c]}</td>'
    tab_html += '</tr>'
tab_html += '</table>'
st.markdown(tab_html, unsafe_allow_html=True)
st.caption(f"Rappel : ajouter {kit['echantillon']} µL d'ADNc par puit → {kit['total_puit']} µL par puit au total.")

df_mix = pd.DataFrame([{k: v for k, v in r.items() if k != "_couleur"} for r in mix_data])

# ---------- RAPPEL GAMME ----------
vol_point = DUP * kit["echantillon"]
vol_reco = max(10, math.ceil(vol_point * 1.5))

st.subheader("Rappel : préparation de la gamme")
st.markdown(f"""
La gamme est faite à partir d'un **pool de tous tes échantillons** (tous tissus confondus) :

- **Pur** : pooler quelques µL de chaque échantillon
- **1/3** : 10 µL du Pur + 20 µL RNase Free Water
- **1/9** : 10 µL du 1/3 + 20 µL RNase Free Water
- **1/27** : 10 µL du 1/9 + 20 µL RNase Free Water
- **1/81** : 10 µL du 1/27 + 20 µL RNase Free Water
- **H2O** : RNase Free Water uniquement → contrôle contamination

> {kit['echantillon']} µL par puit, {DUP} puits par point → prévoir **au moins {vol_reco} µL** de chaque point (volume mort inclus).
> Le pool se conserve pour les prochaines qPCR, mais les dilutions sont à refaire à chaque fois.
""")
st.divider()

# ---------- EXPORT ----------
import io
buffer = io.BytesIO()
df_mix.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)
st.download_button("Télécharger le tableau des mix", data=buffer, file_name="mix_qpcr.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")