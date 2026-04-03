# Résumé des Articles sur l'Analyse des Transits d'Exoplanètes

## 1. High-precision Stellar Limb-darkening in Exoplanetary Transits (Morello et al. 2017)

### Résumé Détaillé :

Cet article explore les limites de précision dans la modélisation des transits d'exoplanètes dues aux formules mathématiques utilisées pour approximer le limb-darkening stellaire, et à l'utilisation de coefficients obtenus soit depuis des modèles d'atmosphères stellaires, soit empiriquement.

### Points Clés :

#### 1.1. Précision Requise
- **≤100 ppm** pour la caractérisation des atmosphères planétaires
- **~10 ppm** avec les instruments JWST (James Webb Space Telescope)
- Les différences de 10-100 ppm dans les profondeurs de transit à différentes longueurs d'onde peuvent être attribuées à la profondeur optique dépendante de la longueur d'onde des couches externes de la planète

#### 1.2. La Loi "Power-2" Recommandée
La loi power-2 est définie comme :
```
I(μ) / I(1) = 1 - c * (1 - μ^α)
```
où :
- `μ = cos(θ)` avec θ l'angle entre la normale à la surface et la ligne de visée
- `c` et `α` sont les deux coefficients à ajuster
- `I(1)` est l'intensité au centre du disque

**Avantages de la loi power-2** :
- Surpasse les autres lois à deux coefficients (quadratique, square-root) dans la plupart des cas
- Performance particulièrement supérieure pour les étoiles froides (types M)
- Meilleure approximation que les lois quadratique et square-root pour les modèles stellaires observés dans l'infrarouge proche à moyen (HST/WFC3, Spitzer/IRAC)
- Dans certains cas, surpasse même la loi claret-4 à quatre coefficients

#### 1.3. Comparaison des Lois de Limb-Darkening

**Lois testées** :
1. **Quadratique** : `I(μ)/I(1) = 1 - u₁(1-μ) - u₂(1-μ)²`
2. **Square-root** : `I(μ)/I(1) = 1 - v₁(1-μ) - v₂(1-√μ)`
3. **Claret-4** : `I(μ)/I(1) = 1 - Σₙ₌₁⁴ aₙ(1-μ^(n/2))`
4. **Power-2** : `I(μ)/I(1) = 1 - c(1-μ^α)` ⭐ **Recommandée**

**Résultats de précision** (erreurs moyennes en intensité spécifique) :
- **Power-2** : 0.1% - 1.0% (max 5-7% pour F0V dans le visible)
- **Claret-4** : 0.05% - 0.6% (max <4%) - Plus robuste mais nécessite 4 coefficients
- **Square-root** : Performance similaire à power-2
- **Quadratique** : 1% - 6% (max jusqu'à 25%) - Moins précise

#### 1.4. Problèmes Identifiés

**Avec les coefficients théoriques (plane-parallel)** :
- Biais intrinsèque d'environ **30 ppm** pour la plupart des étoiles hôtes (types F-M)
- Erreurs jusqu'à **100 ppm** pour les étoiles F0V dans le visible
- Les erreurs sont plus petites dans l'infrarouge (limb-darkening moins prononcé)

**Avec les coefficients empiriques (ajustés)** :
- Les coefficients empiriques basés sur des formules à deux coefficients peuvent être **significativement biaisés**, même si les résidus de la courbe de lumière sont proches de la limite du bruit photonique
- Les modèles peuvent donner des ajustements "parfaits" aux courbes de lumière tout en ayant des biais importants dans les paramètres de transit
- Biais mesurés : jusqu'à **200-225 ppm** à 0.4 μm pour les naines M avec la loi quadratique
- Biais généralement <45 ppm avec power-2, sauf pour quelques cas problématiques (visible, étoiles F0V)

#### 1.5. Stratégie Optimale Développée

**Problème** : L'ajustement des 4 coefficients de claret-4 échoue souvent à converger à cause de dégénérescences entre les paramètres.

**Solution proposée** :
1. **Mesurer a/R* et i dans l'infrarouge** (où le limb-darkening est faible)
   - Les paramètres orbitaux a/R* et i sont indépendants de la longueur d'onde
   - L'infrarouge permet une mesure précise avec des lois simples (power-2 suffit)
   - JWST/MIRI fournira ces observations pour des dizaines d'exoplanètes

2. **Utiliser ces valeurs comme priors gaussiens** lors de l'ajustement dans le visible
   - Permet la convergence de l'ajustement claret-4
   - Réduit les barres d'erreur de ~45-115 ppm à ~25-50 ppm
   - Réduit les biais de +15 à -7 ppm (au lieu de biais plus importants)

3. **Résultats** :
   - Précision absolue de **≤30 ppm** dans la profondeur de transit modélisée
   - Précision relative de **≤10 ppm** sur la bande HST/WFC3
   - Convergence réussie de l'ajustement claret-4 avec les priors

#### 1.6. Modèles Plane-Parallel vs Sphériques

**Différences importantes** :
- Les modèles **sphériques** présentent une chute abrupte d'intensité à petit μ (proche du limbe)
- Les modèles **plane-parallel** ont une intensité significativement >0 pour tous les μ
- Le "rayon photométrique" effectif est mieux représenté par le point où le gradient dI/dμ atteint un maximum
- Ce rayon apparent (r₀) est systématiquement plus petit que le rayon de la couche la plus externe :
  - 0.05-0.1% pour les naines M
  - Jusqu'à ~0.2% pour F0V
- Les erreurs correspondantes en profondeur de transit sont environ **deux fois plus grandes**

**Implications** :
- Les tables de coefficients théoriques basées sur plane-parallel peuvent introduire des biais
- Le rayon stellaire "photométrique" doit être défini avec soin pour chaque bande passante
- Les variations du rayon apparent avec la longueur d'onde sont faibles (pic-à-pic ~11 ppm en profondeur de transit)

#### 1.7. Synergies JWST + Kepler/K2/TESS

- **JWST/MIRI** : Mesures précises des paramètres orbitaux dans l'infrarouge
- **Kepler/K2/TESS** : Observations dans le visible qui bénéficient des priors infrarouges
- Cette approche peut résoudre certaines controverses dans la littérature concernant les coefficients de limb-darkening empiriques
- Ré-analyse des cibles Kepler et K2 possible avec cette nouvelle approche

### Implications pour NPOAP :

1. **Erreurs potentielles** : Un traitement inadéquat du limb-darkening peut donner des erreurs **≥10%** sur les rayons planétaires déduits des transits observés en UV ou visible

2. **Recommandation principale** : Utiliser la loi **power-2** pour les ajustements à deux coefficients, particulièrement pour les étoiles froides

3. **Pour une précision maximale** : Utiliser la loi **claret-4** avec des priors sur a/R* et i obtenus depuis l'infrarouge ou des observations précédentes

4. **Validation** : Les coefficients empiriques peuvent être utilisés pour tester la validité des modèles d'atmosphères stellaires

## 2. Analytic Light Curves for Planetary Transit Searches (Mandel & Agol 2002)

### Points Clés :
- Formules analytiques pour les courbes de lumière de transit
- Méthode rapide et précise pour générer des modèles de transit
- Utilisation de fonctions spéciales (elliptiques) pour calculer la fraction de flux occulté
- Support pour différentes lois de limb-darkening (linéaire, quadratique, etc.)

## 3. An Improved Method for Estimating the Masses of Stars with Transiting Planets (Enoch et al. 2010)

### Résumé Détaillé :

Cet article développe une nouvelle méthode en une seule étape pour déterminer les masses des étoiles hôtes d'exoplanètes à partir de leurs températures effectives, métallicités et densités stellaires photométriques. La méthode est basée sur l'étude de Torres et al. (2009) qui a montré que des masses et rayons stellaires précis pouvaient être obtenus via une calibration utilisant log g, T_eff et [Fe/H]. Enoch et al. substituent log ρ (densité stellaire) à log g, ce qui est plus approprié pour les systèmes exoplanétaires en transit où la densité stellaire peut être obtenue directement depuis la photométrie.

### Points Clés :

#### 3.1. Contexte et Motivation

**Problème** :
- Pour déterminer les paramètres physiques d'une planète en transit et de son étoile hôte, il est essentiel de mesurer indépendamment la masse stellaire
- Les méthodes traditionnelles utilisent des tracks évolutives et isochrones, mais le résultat n'est fiable que si les modèles le sont
- Southworth (2009) a montré que les écarts entre différents ensembles de modèles évolutifs représentent la source dominante d'incertitude systématique dans les paramètres planétaires
- Exemple : l'écart des valeurs de masse obtenues pour HD 209458 avec différents modèles est d'environ 4%

**Solution proposée** :
- Utiliser une calibration directe basée sur des données observationnelles (binaires stellaires) plutôt que des modèles théoriques
- Substituer log ρ (densité stellaire) à log g, car :
  - La densité stellaire peut être obtenue directement depuis la photométrie de transit
  - Elle est plus précise que log g pour les systèmes exoplanétaires (Sozzetti et al. 2007)
  - Elle ne dépend pas de modèles évolutifs

#### 3.2. Détermination de la Densité Stellaire depuis le Transit

La densité stellaire peut être obtenue directement depuis les paramètres mesurables d'une courbe de lumière de transit de haute qualité :

**Équation de Seager & Mallén-Ornelas (2003)** :
```
ρ = (4π²)/(P²G) × [(1+√ΔF)² - b²(1-sin²(πT/P))]^(3/2) / [sin²(πT/P)]
```

où :
- `P` = période orbitale
- `ΔF` = profondeur de transit (ΔF = (F_out - F_transit)/F_out)
- `b` = paramètre d'impact
- `T` = durée totale du transit
- `G` = constante gravitationnelle

**Paramètres requis** :
- Durée et profondeur du transit
- Paramètre d'impact
- Période orbitale

Tous ces paramètres sont mesurables depuis une courbe de lumière photométrique de haute qualité, sans nécessiter de spectroscopie.

#### 3.3. Calibration des Masses et Rayons Stellaires

**Méthode** :
- Utilisation des données de Torres et al. (2009) : 19 systèmes binaires (38 étoiles) avec métallicités connues
- Fit polynomial pondéré par les erreurs sur les mesures de masse et rayon
- Analyse Monte Carlo de 50,000 runs pour obtenir les erreurs sur les coefficients

**Équations de calibration** :

**Pour la masse** :
```
log M = a₁ + a₂X + a₃X² + a₄log ρ + a₅(log ρ)² + a₆(log ρ)³ + a₇[Fe/H]
```

**Pour le rayon** :
```
log R = b₁ + b₂X + b₃log ρ + b₄[Fe/H]
```

où `X = log(T_eff) - 4.1`

**Coefficients (Table 1 de l'article)** :

| Coefficient | Masse (aᵢ) | Erreur | Rayon (bᵢ) | Erreur |
|------------|------------|--------|------------|--------|
| Constante  | 0.458      | 0.017  | 0.150      | 0.002  |
| X          | 1.430      | 0.019  | 0.434      | 0.005  |
| X²         | 0.329      | 0.128  | -          | -      |
| log ρ      | 0.042      | 0.021  | 0.381      | 0.002  |
| (log ρ)²   | 0.067      | 0.019  | -          | -      |
| (log ρ)³   | 0.010      | 0.004  | -          | -      |
| [Fe/H]     | 0.044      | 0.019  | 0.012      | 0.004  |

**Précision** :
- Scatter dans les valeurs ajustées vs mesurées : `σ(log M) = 0.023` et `σ(log R) = 0.009`
- Excellent accord avec les valeurs mesurées (Figure 1 de l'article)

#### 3.4. Application aux Étoiles Hôtes SuperWASP

**Résultats** :
- Application à 17 étoiles hôtes SuperWASP
- Comparaison avec les valeurs obtenues par analyse isochrone
- **Accord très bon** entre les deux méthodes (Table 2 de l'article)

**Cas particuliers** :
- **WASP-10** : Seul cas où les valeurs ne s'accordent pas parfaitement
  - Rayon isochrone : 0.70 ± 0.01 R☉
  - Rayon calibration : 0.60 ± 0.01 R☉
  - Étoile inhabituelle : haute densité (3.10 g/cm³) et haut niveau d'activité
  - Ces écarts de calibration pour les étoiles de faible masse et haute activité sont discutés dans Torres et al. (2009)

#### 3.5. Intégration dans l'Analyse MCMC

**Avantages** :
- La masse stellaire devient un **paramètre dérivé** dans la chaîne MCMC au lieu d'un paramètre de saut contraint par un prior
- Plus robuste car la masse est calculée directement depuis les observations à chaque étape
- Utilisation de priors bayésiens sur T_eff et [Fe/H] (mesurés par spectroscopie)

**Contraintes** :
- **Contrainte Main Sequence** : Pour les étoiles sur la séquence principale, une relation R ∝ M^0.8 est imposée comme prior bayésien
  - Évite la surestimation du rayon stellaire lorsque la photométrie est de mauvaise qualité
  - Nécessaire quand la durée d'ingress/egress ne peut pas être mesurée précisément
- **Exceptions** : WASP-1, 12 et 15 ont cette contrainte relâchée car ce sont des étoiles plus évoluées (âges > temps de vie sur la séquence principale)

**Effet de l'incertitude sur l'excentricité** :
- L'incertitude sur l'excentricité orbitale (depuis les mesures de vélocité radiale) affecte la densité stellaire
- **Exemple WASP-13** :
  - Avec e = 0.18 ± 0.05 : M = 1.05 ± 0.03 M☉, R = 1.24 ± 0.02 R☉
  - Avec e = 0 (fixé) : M = 1.11 ± 0.03 M☉, R = 1.05 ± 0.05 R☉
  - **Effet sur la masse** : ~6% (petit)
  - **Effet sur le rayon** : ~18% (plus important)
- **Conclusion** : L'effet de l'incertitude sur l'excentricité sur la masse finale est petit, mais plus important sur le rayon

#### 3.6. Robustesse de la Méthode

**Résultats clés** :
- ✅ **Masse** : La calibration de masse est **robuste** même avec une photométrie médiocre
- ⚠️ **Rayon** : Un bon estimateur du rayon stellaire nécessite une **bonne courbe de lumière de transit** pour déterminer précisément la durée d'ingress et d'egress
- ✅ **Accord excellent** avec les analyses isochrones pour la plupart des étoiles

**Recommandations** :
- Pour établir les rayons planétaires, il n'y a pas de substitut à une photométrie de bonne qualité
- La contrainte Main Sequence peut fournir une contrainte additionnelle utile si l'étoile peut être montrée (par des moyens indépendants) comme non-évoluée

### Implémentation Proposée :

1. **Module de calcul de densité stellaire** :
   - Implémenter l'équation de Seager & Mallén-Ornelas (2003) pour calculer ρ depuis les paramètres de transit
   - Intégrer dans `core/seager_ornelas_transit.py`

2. **Module de calibration masse/rayon** :
   - Implémenter les équations (4) et (5) avec les coefficients de la Table 1
   - Créer `core/enoch_stellar_mass.py` avec :
     - `calculate_stellar_mass(teff, log_rho, feh)` : Calcule la masse stellaire
     - `calculate_stellar_radius(teff, log_rho, feh)` : Calcule le rayon stellaire
     - Gestion des erreurs via propagation d'incertitudes

3. **Intégration dans l'analyse MCMC** :
   - Utiliser la densité stellaire comme paramètre d'entrée
   - Calculer la masse comme paramètre dérivé à chaque étape
   - Ajouter des priors bayésiens sur T_eff et [Fe/H]
   - Option pour activer/désactiver la contrainte Main Sequence

4. **Interface utilisateur** :
   - Afficher la densité stellaire calculée depuis le transit
   - Afficher la masse et le rayon stellaires calculés via la calibration
   - Comparer avec les valeurs théoriques (si disponibles)
   - Avertir si la photométrie est de mauvaise qualité (affecte le rayon)

5. **Validation** :
   - Tester sur les 17 étoiles SuperWASP de l'article
   - Comparer les résultats avec les valeurs isochrones publiées
   - Vérifier la robustesse avec différents niveaux de bruit photométrique

### Points Clés :
- Amélioration de l'estimation des masses stellaires à partir des transits
- Utilisation combinée des données de transit et de vélocité radiale
- Précision améliorée sur les paramètres stellaires

## 4. High-precision time-series photometry for the discovery and characterization of exoplanets

### Points Clés (général) :
- Techniques de photométrie de haute précision
- Méthodes de détection et caractérisation
- Traitement des données temporelles

## 5. Full-frame Data Reduction Method: A Data Mining Tool to Detect Potential Variations in Optical Photometry (Dai et al. 2023)

### Résumé Détaillé :

Cet article présente une méthode de réduction de données photométriques "full-frame" qui permet d'extraire simultanément les courbes de lumière de **toutes les étoiles** apparaissant dans le même champ de vue (FOV) d'une série temporelle d'images astronomiques, et non seulement des étoiles cibles. Cette approche maximise l'utilisation des données observationnelles et permet de détecter des variations potentielles dans des étoiles "constantes" sans nécessiter d'observations dédiées.

### Points Clés :

#### 5.1. Problème Identifié

**Gaspillage de données** :
- La photométrie différentielle traditionnelle se concentre uniquement sur quelques étoiles (cible, comparaison, check)
- Toutes les autres étoiles dans le champ de vue (plusieurs à des dizaines d'arcminutes) sont généralement **abandonnées**
- C'est un énorme gaspillage de données observationnelles
- Beaucoup d'étoiles "constantes" peuvent en réalité être variables mais non détectées

**Exemples historiques** :
- L'étoile standard G24-9 (DQ7 white dwarf) a été reclassifiée comme système binaire à éclipses V1412 Aql après observations de suivi
- Plusieurs étoiles standards ont été mal classifiées à cause de leur variabilité apparente

#### 5.2. Solution : Programme SPDE (Synchronous Photometry Data Extraction)

**Objectif** :
- Extraire automatiquement les courbes de lumière de **toutes les étoiles** détectées dans une série temporelle
- Détecter des variations potentielles dans des étoiles "constantes"
- Réduire le gaspillage de données observationnelles

**Technologies utilisées** :
- **Python** avec packages Astropy
- **ccdproc** : Classification et calibration de base
- **photutils** : Détection d'étoiles (DAOPHOT) et photométrie par ouverture annulaire
- **astroquery** : Requêtes vers SIMBAD et VizieR

**Pipeline en 5 étapes** (Figure 1) :

1. **Classification** :
   - Classification automatique des images (bias, dark, flats, science)
   - Deux options : par mots-clés FITS ou par clustering non supervisé (K-means)

2. **Pre-processing** :
   - Calibration automatique (bias, dark, flat)
   - Vérification de la disponibilité des images de calibration
   - Réduction des erreurs manuelles dans les logs d'observation

3. **Quality Justification** :
   - Évaluation de la qualité de la série temporelle
   - Identification de l'image de référence (celle avec le plus d'étoiles détectées, Nmax)
   - Classification en 4 grades (A, B, C, D) selon le ratio d'images de qualité médiane
   - Suppression automatique des images de mauvaise qualité (Fd < 20%)

4. **Automatic Matching** :
   - **Problème** : Les excursions d'image (décalages dus au seeing et erreurs de suivi) font que la même étoile apparaît à des positions différentes sur chaque image
   - **Solution** : Algorithme de matching automatique basé sur un triangle de référence (3 étoiles brillantes proches du centre)
   - Recherche de triangles congruents sur toutes les images
   - Calcul du décalage (translation) pour chaque image
   - Vérification que >80% des étoiles sont correctement matchées
   - Mapping des coordonnées pixel → coordonnées célestes (WCS ou Astrometry.net)

5. **Annulus Aperture Photometry** :
   - Photométrie différentielle par ouverture annulaire pour toutes les étoiles matchées
   - Estimation automatique du FWHM (3 méthodes : interpolation, Gauss, Moffat)
   - Choix automatique de la forme d'ouverture (circulaire/elliptique/rectangulaire) selon Rfwhm
   - Test de plusieurs tailles d'ouverture (Na = 12-14 grilles dans la plage 1-5×FWHM)
   - **Production massive** : Nf × Na × Ncm × (Ncm-1)/2 courbes de lumière différentielles
   - Sélection automatique des courbes optimales (minimal scatter)

**Résultats** :
- Pour RX J2102.0+3359 : **363 courbes de lumière optimales** (75% de Nmax = 484)
- Pour Paloma J0524+4244 : **641 courbes de lumière optimales** (61% de Nmax = 1051)

#### 5.3. Programme LCA (Light Curve Analysis)

**Objectif** :
- Analyser automatiquement les courbes de lumière produites par SPDE
- Identifier les variations potentielles
- Classifier les types de variations

**4 modules** :

1. **Separations** :
   - Classification morphologique en 3 types :
     - **Périodique** : Variations répétitives (Rlc > fg ou Amp > Ag)
     - **Transitoire** : Événements uniques (humps/dips avec amplitude > ht et durée > lt)
     - **Peculiar** : Variations monotones ou irrégulières
   - Utilise un lissage par spline 1D et des seuils ajustables (Table B1)

2. **Demonstrations** :
   - Affichage graphique des courbes de lumière suspectes
   - Réduction des opérations manuelles

3. **Markings** :
   - Marquage des étoiles variables sur la carte de référence (finding chart)
   - Identification visuelle facilitée

4. **Cross-identifications** :
   - Requêtes automatiques vers **58 catalogues VizieR**
   - Compilation des paramètres physiques (T_eff, distance, masse, rayon, période, amplitude)
   - Compilation de la luminosité multi-bandes (FUV à radio, X-ray, etc.)
   - Identification via SIMBAD

#### 5.4. Résultats sur Deux Séries Temporelles

**RX J2102.0+3359** (ARCSAT 0.5m, 158 images, 3h, Grade-B) :
- 363 étoiles avec courbes de lumière optimales
- 18 courbes avec variations potentielles détectées
- 4 étoiles connues identifiées (2 EWs, 1 CV, 1 source X-ray)

**Paloma J0524+4244** (XLO 0.85m, 182 images, 3.3h, Grade-C) :
- 641 étoiles avec courbes de lumière optimales
- 14 courbes avec variations potentielles détectées
- 19 étoiles connues identifiées (16 RGB/HB, 2 variables ATLAS, 1 CV)

**Classification des 32 variations détectées** :
- **9 périodiques** : Modulations avec périodes détectées (Lomb-Scargle periodogram)
- **11 transitoires** : 6 brightening (humps) et 5 darkening (dips)
- **12 peculiares** : Variations monotones, transitions de luminosité, ou modulations incomplètes

**Exemples notables** :
- **No. 130 ATOJ081.1876+42.8659** : Variable δ Scuti confirmée (période 0.047 jours)
- **No. 641 Paloma J0524+4244** : CV à éclipse avec dip profond (-1.43 mag, 75 min)
- **No. 183 RX J2102.0+3359** : CV period-gap avec modulation ellipsoïdale
- **No. 26 J210141+340327** : Dip peu profond suspecté d'être un transit d'exoplanète

#### 5.5. Avantages de la Méthode

**Comparé aux pipelines traditionnels** :
- ✅ **Maximise l'utilisation des données** : Toutes les étoiles sont analysées
- ✅ **Détection sérendipitaire** : Découverte de variables non ciblées
- ✅ **Automatisation élevée** : Réduction minimale de l'intervention manuelle
- ✅ **Robuste** : Gère les excursions d'image et les variations de qualité
- ✅ **Compatible** : Fonctionne avec n'importe quel télescope petit/moyen (pas spécifique à un survey)

**Applications** :
- Accumulation de données pour variables connues
- Détection de transients optiques sérendipitaires
- Découverte de nouvelles variables
- Validation de classifications existantes
- Études de variabilité stellaire générale

#### 5.6. Limitations et Défis

**Challenges techniques** :
- Volume de données important : Nf × Na × Ncm × (Ncm-1)/2 courbes à calculer
- Mémoire et temps de calcul importants (Step 5 est le plus coûteux)
- Nécessite un matching robuste pour gérer les excursions d'image
- Classification automatique peut produire des faux positifs (vérification manuelle nécessaire)

**Dépendances** :
- Nécessite WCS dans les headers FITS ou utilisation d'Astrometry.net
- Qualité de la série temporelle affecte le nombre d'étoiles matchées
- Images de mauvaise qualité (<20% Nmax) sont automatiquement exclues

### Implémentation Proposée pour NPOAP :

1. **Module de photométrie full-frame** :
   - Intégrer la méthode SPDE dans le pipeline de photométrie existant
   - Ajouter une option pour extraire toutes les étoiles au lieu de seulement T1+comparateurs
   - Utiliser `photutils` pour la détection automatique d'étoiles (DAOPHOT)

2. **Matching automatique** :
   - Implémenter l'algorithme de matching par triangle (Appendix C)
   - Gérer les excursions d'image automatiquement
   - Mapping coordonnées pixel → célestes

3. **Analyse automatique des courbes** :
   - Module de classification morphologique (périodique/transitoire/peculiar)
   - Détection automatique de variations significatives
   - Génération de rapports avec identifications SIMBAD/VizieR

4. **Interface utilisateur** :
   - Option pour activer le mode "full-frame"
   - Affichage des courbes de toutes les étoiles détectées
   - Filtrage et tri des courbes selon différents critères
   - Export des résultats pour analyse ultérieure

5. **Optimisations** :
   - Traitement par sections pour éviter l'épuisement mémoire
   - Parallélisation du calcul des courbes de lumière
   - Sauvegarde/restauration pour reprise après interruption

---

# Améliorations Proposées pour NPOAP

## 1. Implémentation de la Loi de Limb-Darkening "Power-2"

### Contexte :
L'article de Morello et al. (2017) recommande fortement l'utilisation de la loi "power-2" pour le limb-darkening, particulièrement pour les étoiles froides (types M). Cette loi surpasse les autres lois à deux coefficients (quadratique, square-root) dans la plupart des cas.

### Loi Power-2 (Équation 4 de l'article) :
```
I(μ) / I(1) = 1 - c * (1 - μ^α)
```
où :
- `μ = cos(θ)` avec θ l'angle entre la normale à la surface et la ligne de visée
- `μ = √(1 - r²)` où r est la coordonnée radiale projetée normalisée
- `c` et `α` sont les deux coefficients à ajuster
- `I(1)` est l'intensité au centre du disque (μ=1)

**Note** : Cette loi est un sous-ensemble de la loi claret-4 seulement pour α = 3/2 ou α = 2.

### Avantages de la loi power-2 :
- **Précision** : Erreurs moyennes de 0.1% - 1.0% (vs 1% - 6% pour quadratique)
- **Performance** : Surpasse quadratique et square-root, surtout pour étoiles M
- **Robustesse** : Dans certains cas, surpasse même claret-4 à quatre coefficients
- **Simplicité** : Seulement 2 coefficients à ajuster (vs 4 pour claret-4)

### Implémentation proposée :
1. **Ajouter la loi power-2 dans `pylightcurve` ou créer un module dédié**
   - La loi power-2 a été implémentée dans PYLIGHTCURVE (https://github.com/ucl-exoplanets/pylightcurve)
   - Vérifier si `pylightcurve` supporte déjà cette loi
   - Sinon, implémenter directement dans `lightcurve_fitting.py`

2. **Ajouter une option dans l'interface utilisateur** pour choisir la loi :
   - Quadratique (actuelle)
   - Square-root
   - Power-2 ⭐ **Recommandée**
   - Claret-4 (pour précision maximale)

3. **Permettre l'ajustement des coefficients** :
   - Coefficients théoriques depuis modèles d'atmosphères stellaires
   - Coefficients empiriques (ajustés aux données)
   - Avec priors sur a/R* et i pour faciliter la convergence (claret-4)

4. **Afficher les statistiques de qualité** :
   - Erreurs résiduelles après ajustement
   - Comparaison entre différentes lois
   - Avertissements si les biais potentiels sont élevés (>30 ppm)

## 2. Ajustement des Coefficients de Limb-Darkening avec Priors

### Contexte :
L'article démontre qu'un ajustement des 4 coefficients de claret-4 échoue souvent à converger à cause de dégénérescences. La solution optimale est d'utiliser des priors gaussiens sur a/R* et i obtenus depuis des observations infrarouges.

### Stratégie Optimale (Section 5.3 de l'article) :

1. **Mesurer a/R* et i dans l'infrarouge** :
   - Le limb-darkening est faible dans l'infrarouge
   - Les lois simples (power-2) sont suffisantes
   - Les paramètres orbitaux sont indépendants de la longueur d'onde

2. **Utiliser ces valeurs comme priors gaussiens** dans le visible :
   - Permet la convergence de l'ajustement claret-4
   - Réduit les barres d'erreur de ~45-115 ppm à ~25-50 ppm
   - Réduit les biais significativement

3. **Exemple de priors** (Table 4 de l'article) :
   - Pour b=0 : a/R* = 9.0042 ± 0.004, i = 90° ± 0.18°
   - Pour b=0.5 : a/R* = 9.0042 ± 0.006, i = 86.815° ± 0.01°

### Implémentation proposée :
1. **Récupération automatique des priors** :
   - Système de sources multiples avec fallback automatique :
     1. **pylightcurve** (rapide, local) - priorité 1
     2. **NASA Exoplanet Archive** (fiable, complet) - priorité 2
     3. **Extrasolar Planets Encyclopaedia** - priorité 3
     4. **AAVSO Exoplanet Database** - priorité 4
     5. **SIMBAD** - priorité 5 (dernier recours)
   - Si disponibles, utiliser des observations infrarouges précédentes
   - Permettre la saisie manuelle des priors si aucune source automatique ne fonctionne
   - Afficher la source utilisée pour la traçabilité

2. **Ajustement bayésien avec priors** :
   - Implémenter un ajustement MCMC avec priors gaussiens sur a/R* et i
   - Support pour ajustement claret-4 avec convergence garantie
   - Afficher les distributions a posteriori des paramètres

3. **Interface utilisateur** :
   - Option pour activer/désactiver les priors
   - Affichage des valeurs de priors utilisées
   - Comparaison des résultats avec/sans priors

## 3. Amélioration de la Précision des Courbes de Lumière

### Contexte :
L'article démontre qu'une précision absolue de **≤30 ppm** peut être atteinte dans la profondeur de transit modélisée, avec une précision relative de **≤10 ppm** sur la bande HST/WFC3, selon le type stellaire.

### Résultats Spécifiques de l'Article :

**Avec coefficients théoriques (plane-parallel)** :
- Biais intrinsèque : ~30 ppm pour la plupart des étoiles hôtes (F-M)
- Erreurs jusqu'à 100 ppm pour F0V dans le visible
- Erreurs plus petites dans l'infrarouge (<45 ppm à 8 μm)

**Avec coefficients empiriques** :
- Power-2 : Biais généralement <45 ppm (sauf quelques cas problématiques)
- Claret-4 : Biais <30 ppm (le plus précis)
- Quadratique : Biais jusqu'à 200-225 ppm à 0.4 μm pour naines M

**Avec priors sur a/R* et i** :
- Réduction des barres d'erreur : ~45-115 ppm → ~25-50 ppm
- Réduction des biais : +15 à -7 ppm (au lieu de biais plus importants)
- Convergence réussie de claret-4

### Implémentation proposée :
1. **Détection et correction des effets systématiques** :
   - Airmass, FWHM, position (déjà partiellement implémenté)
   - Granulation stellaire, oscillations
   - Gravity darkening pour étoiles en rotation rapide
   - Spots stellaires (peuvent changer les coefficients "effectifs")

2. **Méthodes de binning temporel** :
   - L'article montre qu'un temps d'intégration de ~1 min (comme Kepler) n'affecte pas la précision comparé à des temps plus courts
   - Implémenter un binning optimal selon le temps d'exposition

3. **Statistiques de qualité détaillées** :
   - **Red noise** : Détecter les résidus corrélés temporellement
   - **Autocorrélation** : Analyser les résidus pour détecter des biais systématiques
   - **Résidus corrélés** : Les amplitudes des résidus corrélés sont dans les gammes :
     - 97-456 ppm avec quadratique
     - 8-105 ppm avec power-2
     - 11-75 ppm avec claret-4
   - Afficher ces métriques dans l'interface utilisateur

4. **Validation des modèles** :
   - Comparer les profondeurs de transit à différentes longueurs d'onde
   - Détecter les biais systématiques (>30 ppm)
   - Avertir l'utilisateur si les biais potentiels sont élevés

## 4. Intégration des Courbes de Lumière Analytiques (Mandel & Agol)

### Contexte :
Les formules analytiques de Mandel & Agol permettent un calcul rapide et précis des courbes de lumière.

### Implémentation proposée :
- Vérifier que `pylightcurve` utilise bien les formules analytiques
- Ajouter une option pour utiliser directement les formules de Mandel & Agol si disponible
- Optimiser le calcul des modèles pour les grandes séries temporelles

## 5. Amélioration de l'Estimation des Paramètres Stellaires (Enoch et al. 2010)

### Contexte :
Une meilleure estimation des masses stellaires améliore la précision des paramètres planétaires. La méthode d'Enoch et al. permet d'obtenir la masse stellaire directement depuis la densité photométrique, évitant ainsi la dépendance aux modèles évolutifs.

### Avantages de la méthode :
- ✅ **Indépendance des modèles** : Pas besoin de tracks évolutives ou isochrones
- ✅ **Précision** : Scatter de seulement 0.023 dex en log M et 0.009 dex en log R
- ✅ **Robustesse** : La masse est robuste même avec une photométrie médiocre
- ✅ **Intégration MCMC** : La masse devient un paramètre dérivé, plus robuste

### Implémentation proposée :
1. **Calcul de la densité stellaire** :
   - Utiliser l'équation de Seager & Mallén-Ornelas (2003) déjà implémentée
   - Calculer log ρ depuis les paramètres de transit (profondeur, durée, impact parameter, période)

2. **Calibration masse/rayon** :
   - Implémenter les équations (4) et (5) d'Enoch et al. avec les coefficients de la Table 1
   - Créer `core/enoch_stellar_mass.py` :
     - `calculate_stellar_mass(teff, log_rho, feh)` : Retourne M en M☉
     - `calculate_stellar_radius(teff, log_rho, feh)` : Retourne R en R☉
     - Propagation d'incertitudes pour les erreurs

3. **Intégration dans l'analyse** :
   - Calculer automatiquement la densité depuis le transit
   - Utiliser T_eff et [Fe/H] depuis la spectroscopie (ou archives)
   - Afficher la masse et le rayon calculés dans l'interface
   - Comparer avec les valeurs théoriques si disponibles

4. **Contrainte Main Sequence** :
   - Option pour activer la contrainte R ∝ M^0.8 pour les étoiles non-évoluées
   - Détection automatique des étoiles évoluées (relâcher la contrainte)

5. **Vérifications de cohérence** :
   - Comparer les paramètres stellaires calculés avec ceux des archives
   - Détecter les incohérences (ex: WASP-10 avec haute activité)
   - Avertir si la photométrie est insuffisante pour un bon estimateur de rayon

## 6. Traitement Multi-Bande et Analyse Spectrale

### Contexte :
L'analyse des transits à plusieurs longueurs d'onde permet la caractérisation des atmosphères et la validation des modèles.

### Utilité de la comparaison bleu/rouge dans le visible :

**Avantages** :
1. **Validation des modèles** : Détecter les biais systématiques dus au limb-darkening
   - Les biais peuvent atteindre 100-200 ppm si la loi de limb-darkening est mal choisie
   - Comparer les profondeurs entre filtres permet de vérifier la cohérence du modèle
   - Si les profondeurs diffèrent de >30 ppm, cela peut indiquer un problème de modélisation

2. **Contrôle qualité** : S'assurer que les ajustements sont robustes
   - Les profondeurs devraient être cohérentes (à quelques dizaines de ppm près) si le modèle est correct
   - Détecter les problèmes de calibration ou de traitement des données

3. **Détection de biais** : Identifier les problèmes de modélisation du limb-darkening
   - Le limb-darkening varie fortement dans le visible (plus fort en bleu qu'en rouge)
   - Les variations de profondeur sont principalement dues au limb-darkening, pas à l'atmosphère planétaire

**Limitations** :
1. **Caractérisation atmosphérique limitée** :
   - Dans le visible, les effets atmosphériques sont souvent masqués par le limb-darkening stellaire
   - La précision requise est très élevée (10-30 ppm) et difficile à atteindre depuis le sol
   - L'infrarouge est préférable pour la caractérisation atmosphérique (limb-darkening plus faible)

2. **Effets confondants** :
   - Spots stellaires, granulation, bruit rouge peuvent créer des variations apparentes
   - Ces effets peuvent masquer les vraies signatures atmosphériques

3. **Précision requise** :
   - Pour détecter des signatures atmosphériques : ~10-30 ppm
   - Pour valider les modèles : ~30-100 ppm
   - Depuis le sol, la précision typique est souvent >100 ppm

### Implémentation proposée :
- Ajouter le support pour l'analyse simultanée de plusieurs filtres
- Implémenter une analyse comparative des profondeurs de transit en fonction de la longueur d'onde
- Générer des rapports comparatifs multi-bandes
- **Fonctionnalité de validation** :
  - Comparer les profondeurs mesurées entre différents filtres
  - Calculer les différences de profondeur (Δδ = δ_bleu - δ_rouge)
  - Avertir si les différences sont >30 ppm (biais potentiel)
  - Afficher un graphique des profondeurs en fonction de la longueur d'onde
  - Calculer les biais attendus dus au limb-darkening pour comparaison

## 7. Validation et Tests de Robustesse

### Contexte :
Pour garantir la précision, il faut valider les méthodes sur des données connues.

### Implémentation proposée :
1. **Tests unitaires avec courbes de lumière synthétiques** :
   - Module `test_seager_ornelas.py` existant (à améliorer)
   - Génération de données synthétiques avec différents niveaux de bruit
   - Tests de récupération de paramètres avec différentes lois de limb-darkening
   - Validation sur des cas limites (transits partiels, très profonds, etc.)

2. **Tests de récupération de paramètres connus** :
   - Module `core/quality_diagnostics.py` créé
   - Fonction `validate_parameter_recovery()` pour comparer paramètres récupérés vs attendus
   - Tests avec différentes précisions (bruit faible, moyen, élevé)
   - Statistiques sur plusieurs essais (moyenne, écart-type, biais, RMSE)

3. **Diagnostics de qualité automatiques** :
   - Classe `QualityDiagnostics` dans `core/quality_diagnostics.py`
   - Validation automatique des paramètres (profondeur, paramètres orbitaux)
   - Vérification de la qualité des résidus (normalité, autocorrélation)
   - Détection de biais dus au limb-darkening (comparaison bleu/rouge)
   - Génération de rapports de diagnostic automatiques
   - Intégration dans l'interface utilisateur pour affichage en temps réel

### Fonctionnalités implémentées :

**Module `core/quality_diagnostics.py`** :
- `validate_transit_depth()` : Valide que la profondeur est dans une plage raisonnable
- `validate_orbital_parameters()` : Vérifie la cohérence des paramètres orbitaux
- `check_residuals_quality()` : Analyse la qualité des résidus (normalité, autocorrélation)
- `check_chi2_quality()` : Vérifie la qualité du chi2 réduit
- `check_limb_darkening_bias()` : Détecte les biais en comparant profondeurs bleu/rouge
- `validate_parameter_recovery()` : Valide la récupération depuis données synthétiques
- `generate_report()` : Génère un rapport de diagnostic formaté

**Module `test_quality_diagnostics.py`** :
- Tests unitaires pour toutes les fonctions de diagnostic
- Validation avec données synthétiques
- Tests de cas limites et d'erreurs

## 8. Interface Utilisateur Améliorée

### Contexte :
Une interface claire facilite l'utilisation des méthodes avancées.

### Implémentation proposée :
1. **Options pour choisir la loi de limb-darkening** :
   - ✅ Implémenté : Combobox avec choix entre pylightcurve, power-2, quadratique, square-root
   - ✅ Paramètres power-2 (c et α) affichés conditionnellement

2. **Affichage des coefficients de limb-darkening ajustés** :
   - ✅ Implémenté : Label affichant les coefficients de la loi sélectionnée
   - ✅ Mise à jour automatique après ajustement empirique
   - ✅ Affichage formaté (ex: "Coefficients power-2: c=0.5234, α=0.4567")

3. **Comparaison entre différentes lois de limb-darkening** :
   - ✅ Implémenté : Fenêtre de comparaison avec 4 graphiques :
     - Courbes de lumière superposées
     - Résidus par loi
     - Histogramme des résidus
     - Autocorrélation des résidus
   - ✅ Bouton "📊 Comparer les Lois" dans la section Limb-Darkening

4. **Graphiques de diagnostic** :
   - ✅ Implémenté : Fenêtre dédiée avec 6 graphiques :
     - Résidus vs Temps
     - Histogramme des résidus (avec ajustement gaussien)
     - Q-Q Plot (test de normalité)
     - Autocorrélation (ACF avec seuils ±0.2)
     - Résidus vs Modèle
     - Résidus vs AIRMASS (si disponible)
   - ✅ Bouton "📈 Graphiques de Diagnostic" dans la zone graphique
   - ✅ Graphiques interactifs avec matplotlib

### Fonctionnalités ajoutées :

**Fenêtre de comparaison des lois** (`compare_limb_darkening_laws`) :
- Compare visuellement pylightcurve et power-2 (si disponible)
- Affiche les courbes de lumière, résidus, histogrammes et autocorrélation
- Permet d'évaluer visuellement quelle loi s'ajuste le mieux aux données

**Fenêtre de graphiques de diagnostic** (`show_diagnostic_plots`) :
- Analyse complète de la qualité des résidus
- Tests de normalité (Q-Q plot, histogramme avec gaussienne)
- Détection de corrélations (autocorrélation, résidus vs variables)
- Aide à identifier les problèmes systématiques (dépendance à l'airmass, etc.)

---

# Priorités d'Implémentation

1. **Haute priorité** :
   - Implémentation de la loi power-2 pour le limb-darkening
   - Amélioration de la gestion des effets systématiques
   - Validation des méthodes sur données synthétiques

2. **Priorité moyenne** :
   - Ajustement des coefficients de limb-darkening avec priors
   - Amélioration des statistiques de qualité
   - Interface utilisateur pour les options de limb-darkening

3. **Priorité basse** :
   - Analyse multi-bande
   - Intégration des méthodes d'Enoch et al.
   - Optimisations avancées

---

# Bibliographie

## Articles Principaux

1. **Morello, G., Tsiaras, A., Howarth, I. D., & Homeier, D.** (2017)  
   "High-precision Stellar Limb-darkening in Exoplanetary Transits"  
   *The Astronomical Journal*, 154, 111 (27pp)  
   DOI: https://doi.org/10.3847/1538-3881/aa8405  
   Fichier: `bibliographie/Exoplanètes/High-precision Stellar Limb-darkening in Exoplanetary Transits.pdf`

2. **Mandel, K., & Agol, E.** (2002)  
   "Analytic Light Curves for Planetary Transit Searches"  
   *The Astrophysical Journal Letters*, 580, L171-L175  
   DOI: https://doi.org/10.1086/345520  
   Fichier: `bibliographie/Exoplanètes/ANALYTICLIGHTCURVESFORPLANETARYTRANSITSEARCHES KAISEY MANDEL1,2 AND ERIC AGOL1,3.pdf`  
   **Résumé** : Présente des formules analytiques exactes pour calculer les courbes de lumière de transit planétaire. Utilise des intégrales elliptiques pour calculer la fraction de flux occulté. Supporte plusieurs lois de limb-darkening (linéaire, quadratique, racine carrée, logarithmique). Méthode rapide et précise pour la génération de modèles de transit.

3. **Enoch, B., Collier Cameron, A., Parley, N. R., & Hebb, L.** (2010)  
   "An Improved Method for Estimating the Masses of Stars with Transiting Planets"  
   *Astronomy & Astrophysics*, 510, A21  
   DOI: https://doi.org/10.1051/0004-6361/200912675  
   arXiv: 1004.1991 [astro-ph.EP]  
   Fichier: `bibliographie/Exoplanètes/An Improved Method for Estimating the Masses of Stars with Transiting Planets. B.Enoch1, A.Collier Cameron1, N.R.Parley1, and L.Hebb2.pdf`  
   **Résumé** : Développe une méthode en une seule étape pour déterminer les masses des étoiles hôtes d'exoplanètes à partir de T_eff, [Fe/H] et log ρ (densité stellaire). La densité stellaire est obtenue directement depuis la photométrie de transit (Seager & Mallén-Ornelas 2003), évitant ainsi la dépendance aux modèles évolutifs. Calibration basée sur 38 étoiles de binaires spectroscopiques (Torres et al. 2009). Application réussie à 17 étoiles hôtes SuperWASP avec excellent accord avec les analyses isochrones. Intégration dans l'analyse MCMC où la masse devient un paramètre dérivé. La calibration de masse est robuste même avec une photométrie médiocre, mais le rayon nécessite une bonne qualité de photométrie pour mesurer précisément l'ingress/egress.

4. **Seager, S., & Mallén-Ornelas, G.** (2003)  
   "A Unique Solution of Planet and Star Parameters from an Extrasolar Planet Transit Light Curve"  
   *The Astrophysical Journal*, 585, 1038-1055  
   DOI: https://doi.org/10.1086/346105  
   Fichier: `bibliographie/Exoplanètes/Seager_Ormelas_2003.pdf`  
   **Résumé** : Démontre qu'une courbe de lumière de transit unique peut fournir une solution unique pour les paramètres planétaires et stellaires, sous certaines conditions. Développe les équations analytiques reliant la profondeur du transit, les durées, et les paramètres orbitaux. Méthode déjà implémentée dans `core/seager_ornelas_transit.py`.

5. **Dai, F., et al.** (2023)  
   "High-precision time-series photometry for the discovery and characterization of exoplanets"  
   *Research in Astronomy and Astrophysics*, 23, 055011  
   Fichier: `bibliographie/Exoplanètes/Dai_2023_Res._Astron._Astrophys._23_055011.pdf`  
   **Résumé** : Présente des techniques récentes de photométrie de haute précision pour la découverte et la caractérisation d'exoplanètes. Couvre les méthodes de traitement des données temporelles, la détection de transits, et l'analyse des courbes de lumière.

6. **[Auteur à compléter]** (Année)  
   "High-precision time-series photometry for the discovery and characterization of exoplanets"  
   Fichier: `bibliographie/Exoplanètes/High-precision time-series photometry for the discovery and chara.pdf`  
   **Note** : Article à analyser pour compléter les détails

## Références Complémentaires

- **Claret, A., & Bloemen, S.** (2011)  
  "Gravity and limb-darkening coefficients for the Kepler mission"  
  *Astronomy & Astrophysics*, 529, A75

- **Kreidberg, L.** (2015)  
  "batman: BAsic Transit Model cAlculatioN in Python"  
  *Publications of the Astronomical Society of the Pacific*, 127, 1161

- **Kipping, D. M.** (2013)  
  "Efficient, uninformative sampling of limb darkening coefficients for two-parameter laws"  
  *Monthly Notices of the Royal Astronomical Society*, 435, 2152-2160

- **Parviainen, H., & Aigrain, S.** (2015)  
  "PYLIGHTCURVE: A Python package for the analysis of exoplanet transit light curves"  
  *Monthly Notices of the Royal Astronomical Society*, 453, 3821-3826

## Notes

- Les fichiers PDF sont stockés dans le répertoire `bibliographie/Exoplanètes/` du workspace
- Les références DOI permettent d'accéder aux versions en ligne des articles
- Les articles ont été organisés par thème dans des sous-répertoires (Exoplanètes, Astéroïdes, Étoiles doubles, etc.)
- Pour une analyse complète, il est recommandé de lire directement les PDF avec un lecteur approprié
