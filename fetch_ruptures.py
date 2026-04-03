"""
fetch_ruptures.py
-----------------
Télécharge le snapshot instantané des ruptures de carburant
et ajoute une ligne dans data/historique_ruptures.csv.

Appelé automatiquement par GitHub Actions toutes les heures.
"""

import requests
import zipfile
import io
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timezone
import os

URL = "https://donnees.roulez-eco.fr/opendata/instantane_ruptures"
OUTPUT_FILE = "data/historique_ruptures.csv"
CARBURANTS = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]


def fetch_ruptures():
    """Télécharge et parse le flux instantané des ruptures."""
    print(f"[{datetime.now()}] Téléchargement du flux instantané...")
    r = requests.get(URL, timeout=30)
    r.raise_for_status()

    z = zipfile.ZipFile(io.BytesIO(r.content))
    xml_filename = [f for f in z.namelist() if f.endswith(".xml")][0]
    with z.open(xml_filename) as f:
        xml_content = f.read()

    root = ET.fromstring(xml_content)
    rows = []

    for pdv in root.findall("pdv"):
        pdv_id = pdv.get("id")
        cp     = pdv.get("cp", "") or ""
        dept   = cp[:2]

        for rupture in pdv.findall("rupture"):
            rows.append({
                "pdv_id":    pdv_id,
                "dept":      dept,
                "carburant": rupture.get("fuel", ""),
                "type":      rupture.get("type", ""),
            })

    return pd.DataFrame(rows)


def compute_stats(df):
    """Calcule les statistiques agrégées à partir des ruptures brutes."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    stats = {"timestamp": now}

    # Total de stations uniques en rupture (tous carburants confondus)
    stats["nb_total"] = df["pdv_id"].nunique() if len(df) > 0 else 0

    # Par carburant
    for carb in CARBURANTS:
        subset = df[df["carburant"] == carb]
        stats[carb] = subset["pdv_id"].nunique()

    # Par type de rupture
    for t in ["temporaire", "definitive"]:
        subset = df[df["type"] == t]
        stats[t] = subset["pdv_id"].nunique()

    return stats


def append_to_csv(stats):
    """Ajoute une ligne au CSV historique (le crée si nécessaire)."""
    os.makedirs("data", exist_ok=True)

    new_row = pd.DataFrame([stats])

    if os.path.exists(OUTPUT_FILE):
        existing = pd.read_csv(OUTPUT_FILE)
        # Éviter les doublons si le script tourne deux fois la même heure
        if len(existing) > 0 and existing["timestamp"].iloc[-1] == stats["timestamp"]:
            print("⚠️  Entrée déjà présente pour ce timestamp, ignorée.")
            return
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Ligne ajoutée dans {OUTPUT_FILE} — {stats['nb_total']} stations en rupture")
    print(f"   Détail : { {k: v for k, v in stats.items() if k in CARBURANTS} }")


if __name__ == "__main__":
    df = fetch_ruptures()
    stats = compute_stats(df)
    append_to_csv(stats)
