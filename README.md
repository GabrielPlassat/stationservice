# ⛽ Ruptures carburants — Suivi automatique

Suivi horaire du nombre de stations-service en rupture de carburant en France,
via l'[Open Data gouvernemental](https://www.prix-carburants.gouv.fr/rubrique/opendata/).

## 🗂️ Structure du projet

```
├── .github/workflows/fetch_ruptures.yml  ← GitHub Actions (collecte horaire)
├── data/
│   └── historique_ruptures.csv           ← CSV auto-généré (1 ligne/heure)
├── fetch_ruptures.py                     ← Script de collecte
├── app.py                                ← Dashboard Streamlit
├── requirements.txt
└── README.md
```

---

## 🚀 Mise en place (étape par étape)

### Étape 1 — Créer le repo GitHub

1. Aller sur [github.com](https://github.com) → **New repository**
2. Nommer le repo (ex. `ruptures-carburants`)
3. Le mettre en **Public** (nécessaire pour Streamlit Community Cloud gratuit)
4. Cliquer **Create repository**

### Étape 2 — Uploader les fichiers

Dans votre nouveau repo, cliquer sur **Add file → Upload files** et déposer :
- `fetch_ruptures.py`
- `app.py`
- `requirements.txt`
- `.github/workflows/fetch_ruptures.yml` *(créer d'abord le dossier via "Add file → Create new file" en tapant `.github/workflows/fetch_ruptures.yml`)*

### Étape 3 — Activer GitHub Actions

1. Aller dans l'onglet **Actions** de votre repo
2. Cliquer sur **"I understand my workflows, go ahead and enable them"** si demandé
3. Cliquer sur le workflow **"Collecte ruptures carburants"**
4. Cliquer **"Run workflow"** pour tester immédiatement

✅ Après quelques secondes, le fichier `data/historique_ruptures.csv` apparaît dans votre repo.

Le workflow s'exécute ensuite **automatiquement toutes les heures**.

### Étape 4 — Déployer le dashboard sur Streamlit

1. Aller sur [share.streamlit.io](https://share.streamlit.io)
2. Se connecter avec votre compte GitHub
3. Cliquer **New app**
4. Sélectionner votre repo, branche `main`, fichier `app.py`
5. Cliquer **Deploy**

🎉 Votre dashboard est en ligne et se met à jour à chaque commit automatique !

---

## 📊 Données collectées

Le CSV `data/historique_ruptures.csv` contient une ligne par heure :

| Colonne | Description |
|---------|-------------|
| `timestamp` | Date et heure du snapshot (UTC) |
| `nb_total` | Nombre total de stations en rupture |
| `Gazole` | Stations en rupture de Gazole |
| `SP95` | Stations en rupture de SP95 |
| `SP98` | Stations en rupture de SP98 |
| `E10` | Stations en rupture de E10 |
| `E85` | Stations en rupture de E85 |
| `GPLc` | Stations en rupture de GPLc |
| `temporaire` | Ruptures de type temporaire |
| `definitive` | Ruptures de type définitive |

---

## ⚙️ Modifier la fréquence de collecte

Dans `.github/workflows/fetch_ruptures.yml`, modifier la ligne `cron` :

```yaml
- cron: "0 * * * *"    # toutes les heures (défaut)
- cron: "0 */2 * * *"  # toutes les 2 heures
- cron: "0 8 * * *"    # une fois par jour à 8h UTC
```

> ⚠️ GitHub Actions peut avoir un délai de quelques minutes sur les crons.
> Le plan gratuit offre 2000 minutes/mois (largement suffisant ici : ~720 min/mois).

---

## 📡 Source des données

- **Site** : https://www.prix-carburants.gouv.fr
- **Endpoint** : `https://donnees.roulez-eco.fr/opendata/instantane_ruptures`
- **Licence** : [Licence ouverte Etalab v2.0](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf)
