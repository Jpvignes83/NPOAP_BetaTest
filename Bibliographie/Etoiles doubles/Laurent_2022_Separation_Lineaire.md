# Résumé : La séparation linéaire utilisée pour déterminer le caractère physique d'une étoile double visuelle

## Informations bibliographiques

**Auteur :** Philippe Laurent  
**Organisation :** SAF - Commission des Étoiles Doubles, Président de l'Association Astronomie en Provence (83)  
**Date :** Décembre 2022  
**Revue :** Étoiles Doubles - n°05  
**Fichier :** ED-2022-05-LAURENT.pdf

**Mots-clés :** binaries: visual, astrometry

---

## Résumé exécutif

Cet article présente une méthode pour sélectionner des couples d'étoiles doubles visuelles présentant une chance raisonnable d'être des paires physiques, en utilisant le calcul de la séparation linéaire à partir des données Gaia DR3. La méthode permet de filtrer les couples optiques (simples alignements de perspective) et d'identifier les couples physiques probables.

---

## Contexte et problématique

### Le catalogue WDS (Washington Double Star Catalog)

- **Plus de 150 000 entrées** et des millions de mesures
- Constitué à partir de découvertes historiques basées principalement sur un **critère de proximité apparente**
- Contient donc un **grand nombre de couples optiques** (proximité due uniquement à la perspective)
- Les deux étoiles sont alors à des distances très différentes

### Apport des missions spatiales

- **Hipparcos** (1989-1993) : premières données astrométriques précises
- **Gaia** (depuis 2015) : données encore plus précises et couvrant une population beaucoup plus grande
- Permettent aujourd'hui de porter un **regard objectif** sur la nature physique ou optique des couples

---

## Méthode proposée : Séparation linéaire

### Principe

Utiliser les données astrométriques Gaia DR3 pour calculer la **séparation linéaire** (en parsecs) entre les deux composantes d'un couple, plutôt que la seule séparation angulaire.

### Données Gaia DR3 utilisées

- **Positions** en ascension droite et déclinaison (époque 2016)
- **Mouvements propres** en RA et DEC
- **Parallaxes** (pour calculer les distances)

### Calculs effectués

#### 1. Séparation angulaire (ρ) et angle de position (θ)

Formules de Laurent (2022) :

```
ρ = arccos[cos(Δα cos δ₁) cos(δ₂ - δ₁)]
θ = 90° - arctan[sin(δ₂ - δ₁) / (cos(δ₂ - δ₁) sin(Δα cos δ₁))]
```

Où :
- Δα = différence en RA (convertie en degrés décimaux)
- δ₁, δ₂ = déclinaisons des deux composantes

#### 2. Séparation linéaire

Calculée à partir de :
- La séparation angulaire (ρ)
- Les parallaxes des deux composantes (pour obtenir les distances)
- Formule géométrique utilisant la distance moyenne

#### 3. Critère de sélection

**Séparation linéaire < 10 parsecs** → couple physique probable

---

## Résultats et validation

### Couverture Gaia DR3

- **Plus de 125 000 couples** du WDS peuvent être analysés avec Gaia DR3
- Complétude proche de **100% pour séparation ≥ 1 arcsec**
- **50% à 0.5 arcsec**
- Limite inférieure : **≈ 0.2 arcsec** (0.5 arcsec dans champs denses vers centre galactique)

### Étude de 377 couples orbitaux

L'auteur a testé la méthode sur 377 couples ayant des orbites connues (classés par l'USNO) :

- **Résultats étonnants** : certains couples avec orbites de grade 3-4 présentent des séparations linéaires > 10 pc
- **Explication** : contamination mutuelle des composantes sur les images Gaia pour couples serrés
- Les données astrométriques peuvent être affectées par :
  - La proximité des composantes (contamination mutuelle)
  - La forte luminosité d'au moins une des deux étoiles

### Indicateurs de qualité Gaia DR3

Pour évaluer la fiabilité des données :

- **RUWE** (Renormalised unit weight error) : indicateur de qualité de la réduction astrométrique
- **astrometric_gof_al** : Goodness of fit statistic

Ces indicateurs peuvent guider l'utilisateur pour apprécier la fiabilité du calcul de séparation linéaire.

---

## Cas particuliers

### Couples serrés (< 1 arcsec)

- Les données individuelles des composantes ne sont pas systématiquement disponibles
- Risque de contamination mutuelle sur les images Gaia
- Les données astrométriques peuvent être dégradées
- **Limitation importante** de la méthode pour ces couples

### Exemple : HLD 60

- Couple classé **Grade 3** par l'USNO
- Séparation linéaire calculée : **1.78 parsec**
- Orbite bien déterminée (graphique USNO)
- Zones d'incertitude sur distances : disjointes mais proches
  - HLD 60 A : 51.717 pc [51.663 - 51.771]
  - HLD 60 B : 49.931 pc [49.839 - 50.024]

### Couples avec séparation > 10 pc et Grade 5

- 18 couples identifiés avec SL > 10 pc mais classés Grade 5
- Nature orbitale très incertaine
- Exemple : ES 2360 - courbe d'orbite très partielle

---

## Conclusions de l'auteur

### Avantages de la méthode

1. **Sélection pertinente** : permet d'écarter un grand nombre de couples manifestement optiques
2. **Grande base de données** : plus de 125 000 couples analysables avec Gaia DR3
3. **Critère objectif** : basé sur des données astrométriques précises

### Limitations

1. **Pas de rigueur absolue** : le critère n'est pas infaillible
2. **Erreurs possibles** : données astrométriques perturbées pour couples serrés
3. **Seuil indicatif** : 10 parsecs est un seuil raisonnable mais pas absolu

### Recommandations

- **Seuil de 10 parsecs** : valeur raisonnable tenant compte des imprécisions
- **Vérifier les indicateurs de qualité** (RUWE, astrometric_gof_al) pour évaluer la fiabilité
- **Écarter les couples** avec séparation linéaire très élevée (> 1000 pc parfois) qui sont manifestement optiques

---

## Outil proposé

L'auteur mentionne un **outil Excel "WDS-Gaia"** qui facilite :
- Le calcul de la séparation linéaire d'une liste de couples
- L'extraction des données Gaia DR3
- La sélection automatique selon le critère

---

## Applications dans NPOAP

### Implémentation réalisée

1. **Module `core/linear_separation_calculator.py`** :
   - Calcul de séparation angulaire (ρ) et angle de position (θ)
   - Calcul de séparation linéaire à partir des parallaxes
   - Requêtes Gaia DR3 pour chaque composante
   - Vérification du mouvement propre commun

2. **Interface dans l'onglet "Étoiles Binaires"** :
   - Sélection de fichier CSV Gaia DR3
   - Recherche automatique de couples proches dans le fichier
   - Seuil de séparation linéaire configurable (défaut : 10 pc)
   - Seuil de séparation angulaire maximale configurable (défaut : 60 arcsec)
   - Génération de catalogues filtrés

### Format CSV Gaia DR3 attendu

**Colonnes obligatoires :**
- `ra` : Ascension droite (degrés)
- `dec` : Déclinaison (degrés)
- `parallax` : Parallaxe (mas)

**Colonnes optionnelles :**
- `source_id` : Identifiant unique Gaia
- `pmra` : Mouvement propre en RA (mas/an)
- `pmdec` : Mouvement propre en DEC (mas/an)
- `ruwe` : Indicateur de qualité astrométrique
- `phot_g_mean_mag` ou `g_mag` : Magnitude G Gaia

### Fichiers générés

1. **`linear_separation_all_YYYYMMDD_HHMMSS.csv`** : Tous les couples analysés
2. **`linear_separation_physical_YYYYMMDD_HHMMSS.csv`** : Couples physiques uniquement (SL < seuil)

### Colonnes du fichier de sortie

- `source_id1`, `source_id2` : Identifiants Gaia des deux composantes
- `ra1`, `dec1`, `ra2`, `dec2` : Coordonnées des composantes
- `separation_linear_pc` : Séparation linéaire en parsecs
- `separation_angular_arcsec` : Séparation angulaire en arcsec
- `position_angle_deg` : Angle de position en degrés
- `distance1_pc`, `distance2_pc` : Distances des composantes
- `distance_avg_pc` : Distance moyenne
- `parallax1_mas`, `parallax2_mas` : Parallaxes des composantes
- `is_physical` : True si SL < 10 pc (critère de Laurent)
- `is_physical_by_threshold` : True si SL < seuil configuré
- `threshold_pc` : Seuil utilisé pour l'analyse
- `pm_common` : True si mouvement propre commun détecté
- `pmra1`, `pmdec1`, `pmra2`, `pmdec2` : Mouvements propres (si disponibles)
- `ruwe1`, `ruwe2` : Indicateurs de qualité Gaia (si disponibles)
- `g_mag1`, `g_mag2` : Magnitudes G Gaia (si disponibles)

---

## Références citées

1. **Washington Double Star Catalog** : http://www.astro.gsu.edu/wds/
2. **Gaia Data Release 3** : https://www.cosmos.esa.int/web/gaia/dr3
3. **WDSSTOOL** : Recherche et édition de listes d'étoiles doubles visuelles - David CHIRON
4. **The CPMDS catalogue** : Common proper motion double stars in the Bordeaux Carte du Ciel zone
5. **Sixth Catalog of Orbits of Visual Binary Stars** : http://www.astro.gsu.edu/wds/orb6.html
6. **Commission des étoiles doubles de la SAF** : https://ced.saf-astronomie.fr/

---

## Points clés à retenir

1. **Méthode simple et efficace** pour filtrer les couples optiques
2. **Basée sur données Gaia DR3** : précises et nombreuses
3. **Critère : SL < 10 pc** pour considérer un couple comme physique probable
4. **Limitations** : couples serrés (< 1 arcsec) peuvent avoir des données contaminées
5. **Vérifier les indicateurs de qualité** (RUWE) pour évaluer la fiabilité
6. **Permet de créer des catalogues** de couples physiques probables pour programmes d'observation

---

**Date de création du résumé :** 2026-01-19  
**Catégorie :** Etoiles doubles  
**Type :** Article de revue (SAF - Commission des Étoiles Doubles)
