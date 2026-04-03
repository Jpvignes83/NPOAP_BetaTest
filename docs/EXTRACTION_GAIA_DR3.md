# Extraction des Catalogues Gaia DR3

Ce module permet d'extraire des données du catalogue Gaia DR3 via l'API TAP de l'archive ESA, en créant des catalogues filtrés par hémisphère (nord/sud) et répartis par bandes de longitude horaire (RA).

## Objectif

Au lieu de télécharger toutes les données Gaia DR3 via `wget`, ce script permet de créer des requêtes ADQL ciblées pour extraire uniquement les étoiles nécessaires :
- **Magnitude limitée** : G < 15 (configurable)
- **Hémisphère** : Nord (dec >= 0) ou Sud (dec < 0)
- **Répartition par RA** : Bandes de longitude horaire (par défaut 30° = 2h)

Cela optimise les téléchargements et permet d'utiliser ensuite `WatneyAstrometry.GaiaStarExtractor.exe` pour traiter uniquement les données filtrées.

## Installation

Le module nécessite `astroquery` qui est déjà dans les dépendances :

```bash
pip install astroquery
```

## Utilisation

### Exemple simple : Script Python

```python
from core.gaia_dr3_extractor import extract_gaia_catalogs

# Extraire les deux hémisphères avec G < 15, pas de 30°
results = extract_gaia_catalogs(
    output_dir="catalogues_gaia_dr3",
    mag_limit=15.0,
    ra_step_deg=30.0,
    hemisphere=None,  # None = les deux hémisphères
    output_format='csv',
    combine_files=False
)

print(f"Total étoiles : {results['total_count']:,}")
print(f"Hémisphère NORD : {results['north_count']:,} étoiles")
print(f"Hémisphère SUD  : {results['south_count']:,} étoiles")
```

### Exemple complet : Script d'exemple

Un script d'exemple complet est disponible dans `examples/extract_gaia_catalogues.py` :

```bash
python examples/extract_gaia_catalogues.py
```

### Utilisation avancée : Classe GaiaDR3Extractor

```python
from core.gaia_dr3_extractor import GaiaDR3Extractor

# Créer un extracteur
extractor = GaiaDR3Extractor(output_dir="catalogues_gaia_dr3")

# Extraire uniquement l'hémisphère nord
north_files, north_count = extractor.extract_hemisphere_catalog(
    hemisphere='north',
    mag_limit=15.0,
    ra_step_deg=30.0,
    output_format='csv',
    combine_files=False
)

print(f"Hémisphère nord : {north_count:,} étoiles dans {len(north_files)} fichiers")

# Extraire uniquement l'hémisphère sud
south_files, south_count = extractor.extract_hemisphere_catalog(
    hemisphere='south',
    mag_limit=15.0,
    ra_step_deg=30.0,
    output_format='csv',
    combine_files=False
)

print(f"Hémisphère sud : {south_count:,} étoiles dans {len(south_files)} fichiers")
```

## Paramètres

### `mag_limit` : Magnitude limite
- **Type** : `float`
- **Défaut** : `15.0`
- **Description** : Magnitude limite G pour filtrer les étoiles (G < mag_limit)

### `ra_step_deg` : Pas de RA en degrés
- **Type** : `float`
- **Défaut** : `30.0` (2 heures)
- **Description** : Pas de RA pour diviser le ciel en bandes. Valeurs recommandées :
  - `30.0` (2h) : 12 bandes par hémisphère
  - `15.0` (1h) : 24 bandes par hémisphère
  - `60.0` (4h) : 6 bandes par hémisphère

### `hemisphere` : Hémisphère à extraire
- **Type** : `str` ou `None`
- **Défaut** : `None`
- **Valeurs** : `'north'`, `'south'`, ou `None` (les deux)

### `output_format` : Format de sortie
- **Type** : `str`
- **Défaut** : `'csv'`
- **Valeurs** : `'csv'`, `'fits'`, ou `'votable'`

### `combine_files` : Combiner les fichiers
- **Type** : `bool`
- **Défaut** : `False`
- **Description** : Si `True`, combine tous les fichiers par hémisphère en un seul catalogue

## Structure des fichiers créés

Les fichiers créés suivent la convention de nommage :
```
gaia_dr3_{hemisphere}_ra{ra_min:02d}h-{ra_max:02d}h_mag{mag_limit:.1f}.{format}
```

Exemples :
- `gaia_dr3_nord_ra00h-02h_mag15.0.csv` : Hémisphère nord, RA 0h-2h, G < 15
- `gaia_dr3_sud_ra12h-14h_mag15.0.csv` : Hémisphère sud, RA 12h-14h, G < 15

Si `combine_files=True`, un fichier combiné est aussi créé :
- `gaia_dr3_{hemisphere}_complete_mag{mag_limit:.1f}.{format}`

## Colonnes dans les fichiers CSV

Les fichiers CSV contiennent les colonnes suivantes :
- `source_id` : Identifiant unique Gaia
- `ra` : Ascension droite (degrés)
- `dec` : Déclinaison (degrés)
- `g_mag` : Magnitude G
- `pmra` : Proper motion en RA (mas/an)
- `pmdec` : Proper motion en DEC (mas/an)
- `parallax` : Parallaxe (mas)
- `radial_velocity` : Vitesse radiale (km/s)

## Utilisation avec Watney Astrometry

Une fois les catalogues extraits, vous pouvez utiliser `WatneyAstrometry.GaiaStarExtractor.exe` pour les traiter :

```bash
# Exemple : extraire les étoiles depuis les fichiers CSV créés
WatneyAstrometry.GaiaStarExtractor.exe \
    --max-magnitude 15.0 \
    --out z:\gaia3stars \
    --files z:\catalogues_gaia_dr3 \
    --threads 10
```

## Avantages par rapport au téléchargement complet

1. **Téléchargement optimisé** : Seules les étoiles filtrées (G < 15) sont téléchargées
2. **Répartition par RA** : Fichiers plus petits et faciles à gérer
3. **Séparation hémisphères** : Permet de traiter indépendamment nord et sud
4. **Format flexible** : CSV, FITS, ou VOTable selon vos besoins

## Limites et considérations

- **Temps de téléchargement** : Les requêtes TAP peuvent prendre du temps selon le nombre de bandes
- **Taille des fichiers** : Avec G < 15, chaque bande de 30° contient environ quelques millions d'étoiles
- **API Gaia** : Le script utilise l'API publique de l'archive ESA, soumise aux limites de taux

## Dépannage

### Erreur : "astroquery.gaia non disponible"
```bash
pip install astroquery
```

### Erreur : Timeout sur les requêtes TAP
- Réduisez `ra_step_deg` (bandes plus petites)
- Augmentez le délai entre les requêtes dans le code

### Erreur : Trop d'étoiles dans une bande
- Augmentez `ra_step_deg` pour avoir plus de bandes
- Vérifiez que `mag_limit` est correctement défini

## Références

- [Gaia Archive - Documentation ESA](https://www.cosmos.esa.int/web/gaia-users/archive)
- [ADQL Documentation](https://www.ivoa.net/documents/ADQL/)
- [Watney Astrometry](https://github.com/Jusas/WatneyAstrometry)
