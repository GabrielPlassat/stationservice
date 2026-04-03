"""
app.py — Dashboard Streamlit
Visualise l'évolution des ruptures de carburant
à partir du CSV collecté par GitHub Actions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Ruptures carburants 🇫🇷",
    page_icon="⛽",
    layout="wide",
)

CARBURANTS = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
COULEURS = {
    "Gazole": "#2196F3",
    "SP95":   "#4CAF50",
    "SP98":   "#FF9800",
    "E10":    "#9C27B0",
    "E85":    "#009688",
    "GPLc":   "#F44336",
}

# ── Chargement des données ────────────────────────────────────────────────────
DATA_URL = "data/historique_ruptures.csv"

@st.cache_data(ttl=3600)  # Recharge au max toutes les heures
def load_data():
    df = pd.read_csv(DATA_URL, parse_dates=["timestamp"])
    df = df.sort_values("timestamp")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Le fichier data/historique_ruptures.csv est introuvable. "
             "Lancez d'abord `python fetch_ruptures.py` ou attendez "
             "que GitHub Actions effectue sa première collecte.")
    st.stop()

# ── En-tête ───────────────────────────────────────────────────────────────────
st.title("⛽ Ruptures de carburant en France")
st.caption(f"Données collectées toutes les heures via l'Open Data gouvernemental. "
           f"Dernière mise à jour : **{df['timestamp'].max().strftime('%d/%m/%Y %H:%M')}**")

# ── Filtres ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 Filtres")
    date_min = df["timestamp"].min().date()
    date_max = df["timestamp"].max().date()

    plage = st.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    carb_choisis = st.multiselect(
        "Carburants à afficher",
        options=CARBURANTS,
        default=CARBURANTS,
    )

# Appliquer le filtre de dates
if isinstance(plage, tuple) and len(plage) == 2:
    mask = (df["timestamp"].dt.date >= plage[0]) & (df["timestamp"].dt.date <= plage[1])
    df_filtered = df[mask]
else:
    df_filtered = df

# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

derniere = df_filtered.iloc[-1] if len(df_filtered) > 0 else df.iloc[-1]
avant    = df_filtered.iloc[-2] if len(df_filtered) > 1 else None

delta_total = int(derniere["nb_total"] - avant["nb_total"]) if avant is not None else None

col1.metric("🔴 Stations en rupture", int(derniere["nb_total"]),
            delta=delta_total, delta_color="inverse")
col2.metric("⛽ Gazole", int(derniere.get("Gazole", 0)))
col3.metric("🟢 SP95", int(derniere.get("SP95", 0)))
col4.metric("🟠 SP98", int(derniere.get("SP98", 0)))

st.divider()

# ── Graphique 1 : évolution globale ──────────────────────────────────────────
st.subheader("📈 Évolution globale — toutes ruptures confondues")

fig1 = px.line(
    df_filtered,
    x="timestamp",
    y="nb_total",
    labels={"timestamp": "Date / Heure", "nb_total": "Nombre de stations"},
    markers=False,
)
fig1.update_traces(line_color="#e74c3c", line_width=2)
fig1.update_layout(hovermode="x unified", height=350)
st.plotly_chart(fig1, use_container_width=True)

# ── Graphique 2 : par carburant ───────────────────────────────────────────────
st.subheader("📊 Par carburant")

carbs_dispo = [c for c in carb_choisis if c in df_filtered.columns]
if carbs_dispo:
    df_melt = df_filtered.melt(
        id_vars=["timestamp"],
        value_vars=carbs_dispo,
        var_name="carburant",
        value_name="nb_stations",
    )
    fig2 = px.line(
        df_melt,
        x="timestamp",
        y="nb_stations",
        color="carburant",
        color_discrete_map=COULEURS,
        labels={"timestamp": "Date / Heure", "nb_stations": "Stations en rupture",
                "carburant": "Carburant"},
        markers=False,
    )
    fig2.update_layout(hovermode="x unified", height=400)
    st.plotly_chart(fig2, use_container_width=True)

# ── Graphique 3 : temporaire vs définitive ────────────────────────────────────
st.subheader("🔀 Ruptures temporaires vs définitives")

if "temporaire" in df_filtered.columns and "definitive" in df_filtered.columns:
    df_type = df_filtered.melt(
        id_vars=["timestamp"],
        value_vars=["temporaire", "definitive"],
        var_name="type",
        value_name="nb_stations",
    )
    fig3 = px.area(
        df_type,
        x="timestamp",
        y="nb_stations",
        color="type",
        color_discrete_map={"temporaire": "#f39c12", "definitive": "#e74c3c"},
        labels={"timestamp": "Date / Heure", "nb_stations": "Stations", "type": "Type"},
    )
    fig3.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ── Tableau des dernières valeurs ─────────────────────────────────────────────
with st.expander("📋 Voir les données brutes"):
    st.dataframe(
        df_filtered.sort_values("timestamp", ascending=False).head(100),
        use_container_width=True,
    )
    st.download_button(
        "⬇️ Télécharger le CSV complet",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="ruptures_carburants.csv",
        mime="text/csv",
    )
