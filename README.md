# AirWatch Tunisie

Une plateforme de données qui surveille chaque jour la qualité de l'air de cinq villes
tunisiennes (Tunis, Sfax, Sousse, Bizerte, Gabès), vérifie les données avant de les
publier, et prévient avant un pic de pollution.

Projet DataOps, ING5-DS : Chaima Brini, Sirine Nahal.

## Sources

| Source | Contenu | Accès |
|---|---|---|
| API Open-Meteo Air Quality | PM2.5, PM10, NO₂, ozone, poussières, indice européen, heure par heure | gratuite, sans clé |
| API Open-Meteo Météo | température, humidité, pluie, vent, heure par heure | gratuite, sans clé |
| `data/cities.csv` | les 5 villes et leurs coordonnées | dans le dépôt |

Les valeurs de pollution viennent du modèle européen CAMS (Copernicus), pas de capteurs au sol.

## Questions métier

1. Quelle ville dépasse le plus souvent le seuil de l'OMS pour les PM2.5 (15 µg/m³ sur 24 h) ?
2. Le vent et la pluie font-ils baisser la pollution ?
3. Quelles villes faut-il prévenir pour demain ?

## Démarrer

```bash
python -m venv .venv
# Windows : .venv\Scripts\Activate.ps1    Linux/Mac : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Windows : Copy-Item .env.example .env
python -m pytest              # tests sans réseau
python ingest.py              # appelle les deux API et remplit warehouse.duckdb
```

Puis les modèles dbt et les contrôles :

```bash
dbt build                     # modèles staging → intermediate → marts, tests, contrat
dbt source freshness          # les données ont-elles moins de 26 h ?
python query.py "select * from mart_city_daily order by city, day"
```

Pour la CI (sans réseau), un échantillon de vraies données est versionné dans
`tests/fixtures/`. On le recrée avec `python export_samples.py` après une ingestion,
et on le charge avec `python ingest.py --sample`.

Relancer `python ingest.py` ne crée aucun doublon : chaque table brute a une clé
(ville, heure), et une heure déjà chargée est remplacée par sa valeur la plus récente.

## Règles d'équipe

- Rien n'arrive sur `main` sans pull request relue par l'autre membre.
- Aucun secret dans le dépôt : ils vont dans `.env` (ignoré par Git) ou dans les secrets GitHub.
