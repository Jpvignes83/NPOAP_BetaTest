# Analyse de l'Installation et Fonctionnalités de SPAN

**Date** : 2025-01-10
**Version SPAN analysée** : 7.4.1 (dernière version disponible)

---

## 1. Installation et Dépendances

### 1.1 Installation
```bash
pip install span-gui
```

**Requis** : Python 3.10 ou supérieur

### 1.2 Dépendances Principales

D'après l'analyse `pip install --dry-run`, SPAN nécessite :

**Bibliothèques Astronomiques :**
- `astropy` (>=6.1.0, <=7.1.0)
- `emcee` (3.1.6) - **MCMC pour inférence bayésienne**
- `ppxf` (9.4.2) - **Penalized Pixel-Fitting (POPSTAR)**
- `plotbin` (3.1.8) - Visualisation de cubes de données
- `vorbin` (3.1.7) - Voronoi binning
- `capfit` (2.7.1) - Ajustement de courbes
- `powerbin` (1.1.10) - Binning adaptatif

**Bibliothèques Scientifiques :**
- `numpy` (2.2.6)
- `scipy` (1.16.0)
- `scikit-learn` (1.7.0) - Machine learning
- `scikit-image` (0.26.0) - Traitement d'images

**Bibliothèques Visualisation/Données :**
- `matplotlib` (>=3.10.0)
- `pandas` (>=2.2.3)

**Autres :**
- `joblib` - Parallélisation
- `networkx` - Graphes
- `PyWavelets` - Transformées en ondelettes
- `ImageIO`, `tifffile` - Traitement d'images

---

## 2. Fonctionnalités Identifiées

### 2.1 Fonctionnalités Principales (d'après la documentation)

1. **Visualisation Interactive**
   - Zoom et panoramique
   - Affichage temps réel des longueurs d'onde et flux
   - Outils de manipulation interactifs

2. **Analyse de Spectres 1D**
   - Estimation manuelle du redshift (alignement avec lignes de référence)
   - Ajustement de spectres
   - Mesure de largeur équivalente (EW)
   - Détection de pics
   - Calcul du rapport signal/bruit (SNR)

3. **Analyse de Populations Stellaires**
   - Utilisation de **PPXF** (Penalized Pixel-Fitting)
   - Ajustement de templates stellaires
   - Décomposition en populations stellaires
   - Analyse SFH (Star Formation History)

4. **Cinématique Stellare et Gaz**
   - Analyse de la cinématique des étoiles
   - Analyse de la cinématique du gaz

5. **Support Multi-Formats**
   - Compatible avec formats : IRAF, SDSS, IRTF, SAURON, X-Shooter, JWST, MUSE, CALIFA, WEAVE LIFU
   - Support cubes de données JWST NIRSpec IFU

6. **Voronoï Binning**
   - Support via `vorbin` pour cubes de données IFU
   - Binning adaptatif pour améliorer SNR

---

## 3. Différences Clés avec Prospector

### 3.1 Approche Méthodologique

| Aspect | SPAN | Prospector |
|--------|------|------------|
| **Méthode d'ajustement** | PPXF (Penalized Pixel-Fitting) | Inférence bayésienne MCMC complète |
| **Inférence** | Ajustement de templates stellaires | Inférence de propriétés physiques (âge, métallicité, etc.) |
| **Statistiques** | Maximum de vraisemblance (via PPXF) | Bayesienne (distributions postérieures) |
| **Incertitudes** | Approximatives (via PPXF) | Robustes (via MCMC) |

### 3.2 Fonctionnalités Uniques

**SPAN offre :**
- ✅ Interface graphique dédiée (GUI complète)
- ✅ PPXF intégré (excellent pour décomposition de populations)
- ✅ Support cubes IFU (avec Voronoï binning)
- ✅ Visualisation interactive temps réel
- ✅ Estimation manuelle de redshift interactive

**Prospector offre :**
- ✅ Inférence bayésienne complète des propriétés stellaires
- ✅ Combinaison rigoureuse photométrie + spectres
- ✅ Modèles SFH flexibles (paramétriques ou non-paramétriques)
- ✅ Support SED (Spectral Energy Distribution)
- ✅ Calibration spectroscopique polynomiale

### 3.3 Complémentarité

**SPAN et Prospector sont complémentaires :**

1. **SPAN** : Idéal pour :
   - Exploration visuelle de spectres
   - Ajustement rapide avec PPXF
   - Décomposition de populations stellaires
   - Estimation interactive de redshift
   - Analyse de cubes IFU

2. **Prospector** : Idéal pour :
   - Inférence statistique robuste
   - Analyse de SED complètes
   - Combinaison photométrie + spectres
   - Publications scientifiques (incertitudes robustes)
   - Catalogues de galaxies

---

## 4. Points Forts et Faiblesses

### 4.1 SPAN - Points Forts
✅ Interface graphique intuitive
✅ Installation simple (`pip install`)
✅ PPXF intégré (outil très performant)
✅ Support multi-formats étendu
✅ Visualisation interactive
✅ Support cubes IFU (Voronoï binning)
✅ Estimation manuelle de redshift interactive

### 4.2 SPAN - Points Faibles
⚠️ Pas d'inférence bayésienne complète (utilise PPXF seulement)
⚠️ Incertitudes moins robustes que MCMC bayésien
⚠️ Pas de support SED photométrique (seulement spectres)
⚠️ GUI dédiée (moins flexible pour intégration)
⚠️ Nécessite Python 3.10+ (contrainte de version)

### 4.3 Prospector - Points Forts (rappel)
✅ Inférence bayésienne complète
✅ Support SED (spectres + photométrie)
✅ Incertitudes robustes (distributions postérieures)
✅ Modèles SFH flexibles
✅ Utilisé dans de nombreuses publications
✅ API Python (intégration flexible)

### 4.4 Prospector - Points Faibles (rappel)
⚠️ Installation complexe (FSPS requis)
⚠️ Pas d'interface graphique dédiée
⚠️ Courbe d'apprentissage plus élevée
⚠️ Performance dépendante du hardware

---

## 5. Recommandations pour NPOAP

### 5.1 Intégration SPAN comme Option Complémentaire

**SPAN serait utile pour :**

1. **Visualisation Interactive**
   - Interface graphique dédiée pour visualisation de spectres
   - Outils de zoom/pan interactifs
   - Aperçu temps réel des paramètres

2. **Ajustement Rapide avec PPXF**
   - Décomposition rapide de populations stellaires
   - Estimation de redshift via ajustement
   - Analyse cinématique

3. **Support Cubes IFU**
   - Analyse de cubes de données JWST NIRSpec IFU
   - Voronoï binning pour améliorer SNR
   - Visualisation de cartes 2D

4. **Workflow Complémentaire**
   - SPAN pour exploration/visualisation initiale
   - Prospector pour inférence statistique approfondie

### 5.2 Architecture d'Intégration Proposée

```
Onglet Spectroscopie NPOAP
├── Section 1: Chargement de Spectres (commun)
│   ├── Format FITS/ASCII
│   └── Support multi-formats
│
├── Section 2: Visualisation (via SPAN GUI optionnel)
│   ├── Mode 1: Visualisation SPAN (si installé)
│   │   ├── Interface graphique SPAN
│   │   ├── Zoom/Pan interactif
│   │   └── Exploration visuelle
│   │
│   └── Mode 2: Visualisation NPOAP (actuel)
│       └── Matplotlib intégré
│
├── Section 3: Analyse Rapide (via SPAN/PPXF optionnel)
│   ├── Ajustement PPXF (si SPAN installé)
│   ├── Décomposition populations stellaires
│   ├── Estimation redshift interactive
│   └── Analyse cinématique
│
└── Section 4: Inférence Avancée (via Prospector)
    ├── Inférence bayésienne (actuel)
    ├── Support SED
    └── Combinaison photométrie + spectres
```

### 5.3 Conditions d'Intégration

**Pour intégrer SPAN dans NPOAP :**

1. **Détection Optionnelle**
   ```python
   try:
       import span_gui
       SPAN_AVAILABLE = True
   except ImportError:
       SPAN_AVAILABLE = False
   ```

2. **Activation Conditionnelle**
   - Bouton "Ouvrir dans SPAN" (si SPAN installé)
   - Ou intégration widgets SPAN dans l'interface NPOAP

3. **Fonctionnalités Prioritaires à Intégrer**
   - Visualisation interactive SPAN (optionnel)
   - Ajustement PPXF via SPAN API
   - Estimation redshift interactive

4. **Workflow Recommandé**
   - Utiliser SPAN pour exploration/visualisation
   - Exporter résultats vers Prospector pour inférence approfondie

---

## 6. Test d'Installation

### 6.1 Test Réalisé

Commande : `pip install span-gui --dry-run`

**Résultat** : ✅ Installation possible sans conflit apparent

**Dépendances identifiées** : 20+ packages scientifiques
**Taille estimée** : ~200-300 MB (avec toutes les dépendances)

### 6.2 Compatibilité avec NPOAP

**Dépendances communes** :
- ✅ `astropy` - Déjà utilisé dans NPOAP
- ✅ `matplotlib` - Déjà utilisé dans NPOAP
- ✅ `numpy`, `scipy` - Déjà utilisés dans NPOAP

**Nouvelles dépendances** :
- `emcee` - MCMC (déjà utilisé par Prospector potentiellement)
- `ppxf` - Nouveau pour NPOAP
- `scikit-learn`, `scikit-image` - Nouveaux pour NPOAP

**Pas de conflit majeur identifié** ✅

---

## 7. Conclusion

### 7.1 SPAN est Complémentaire à Prospector

SPAN et Prospector ne sont **pas concurrents** mais **complémentaires** :

- **SPAN** : Outil interactif pour exploration et ajustement rapide
- **Prospector** : Outil statistique pour inférence approfondie

### 7.2 Recommandation Finale

**Intégrer SPAN comme option complémentaire** si :
1. ✅ Besoin de visualisation interactive avancée
2. ✅ Analyse de cubes IFU (JWST NIRSpec)
3. ✅ Ajustement rapide avec PPXF
4. ✅ Estimation interactive de redshift

**Conserver Prospector comme solution principale** pour :
1. ✅ Inférence bayésienne robuste
2. ✅ Analyse de SED complètes
3. ✅ Publications scientifiques
4. ✅ Catalogues de galaxies

### 7.3 Prochaines Étapes

1. **Installer SPAN** dans un environnement de test
2. **Tester l'API SPAN** pour intégration
3. **Implémenter détection optionnelle** dans `gui/spectroscopy_tab.py`
4. **Créer widgets** pour intégration SPAN
5. **Documenter workflow** SPAN → Prospector

---

**Prochain document** : Plan d'intégration technique de SPAN dans NPOAP
