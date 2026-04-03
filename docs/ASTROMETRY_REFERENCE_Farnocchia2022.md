# Référence Technique : Farnocchia et al. 2022
## International Asteroid Warning Network Timing Campaign: 2019 XS

**Référence complète :**  
Farnocchia, D., et al. 2022, *Planetary Science Journal*, 3:156 (13pp)  
DOI: https://doi.org/10.3847/PSJ/ac7224

---

## 1. Contexte et Objectifs

Cet article présente les résultats d'une campagne de timing astrométrique pour l'astéroïde 2019 XS dans le cadre du réseau IAWN (International Asteroid Warning Network). Cette campagne implique de nombreux observatoires et utilise des méthodes d'analyse astrométrique avancées.

### Points clés :
- Campagne de timing coordonnée multi-observatoires
- Analyse astrométrique précise pour objets proches de la Terre (NEO)
- Utilisation du catalogue Gaia (DR3) comme référence astrométrique

---

## 2. Références Techniques Importantes

### 2.1 Méthodes d'Ajustement Orbital et Incertitudes

**Références clés identifiées :**

1. **Chesley et al. 2010, Icarus, 210, 158**
   - Méthodes d'estimation d'incertitude astrométrique
   - Ajustement orbital avec observations astrométriques

2. **Baer et al. 2011, Icarus, 212, 438**
   - Amélioration des incertitudes astrométriques
   - Traitement des observations de précision

3. **Carpino et al. 2003, Icarus, 166, 248**
   - Méthodes de calcul des incertitudes dans l'ajustement orbital
   - Propagation d'erreurs astrométriques

4. **Farnocchia et al. 2015, Icarus, 245, 94**
   - Validation des observations astrométriques
   - Analyse de résidus astrométriques

### 2.2 Catalogues Astrométriques

- **Gaia DR3** (Gaia Collaboration, 2021, A&A, 649, A1)
  - Catalogue de référence pour l'astrométrie moderne
  - Précision sub-milliarcseconde pour les étoiles brillantes
  - Utilisé comme système de référence pour les observations

- **UCAC4/5** (Zacharias et al. 2010, 2013)
  - Catalogue astrométrique complémentaire
  - Précision de l'ordre de 10-20 mas

---

## 3. Implications Techniques pour Notre Pipeline Astrométrique

### 3.1 Utilisation du Catalogue Gaia

**Recommandations :**
- Utiliser **Gaia DR3** comme référence principale (déjà implémenté)
- Vérifier la magnitude limite : Gaia DR3 couvre jusqu'à ~21 mag
- Utiliser les coordonnées ICRS (RA_ICRS, DE_ICRS) directement

**Améliorations possibles :**
```python
# Vérifier la version du catalogue Gaia utilisée
# S'assurer d'utiliser les coordonnées ICRS (système de référence standard)
# Considérer les incertitudes propres aux étoiles Gaia dans le matching
```

### 3.2 Calcul des Incertitudes Astrométriques

**Points à considérer :**

1. **Résidus astrométriques (O-C) :**
   - Calculer les résidus observés - calculés pour chaque étoile de référence
   - Analyser la distribution des résidus (RMS, médiane)
   - Identifier les outliers (résidus > 3σ)

2. **Propagation d'incertitudes :**
   - Incertitudes du catalogue (Gaia)
   - Incertitudes de mesure (centroïde, WCS)
   - Incertitudes systématiques (distorsions optiques, réfraction atmosphérique)

3. **Validation de la qualité :**
   - Nombre minimum d'étoiles de référence : ≥ 10 (idéalement ≥ 20)
   - RMS astrométrique : < 0.5" pour observations de qualité
   - Distribution des résidus : normale (test de normalité)

### 3.3 Méthodes d'Extrapolation Zero-Aperture

**Concept :**
- L'extrapolation zero-aperture est une méthode pour estimer l'erreur systématique
- Teste plusieurs apertures et extrapole vers aperture = 0
- Permet de corriger les biais systématiques liés à la taille d'aperture

**Implémentation actuelle :**
- Déjà implémentée avec 4 apertures
- Extrapolation linéaire : RMS = a × aperture + b
- Validation : zero_rms doit être positif et raisonnable

**Améliorations possibles :**
- Considérer une extrapolation quadratique pour meilleure précision
- Ajouter des vérifications de qualité (R² du fit)
- Comparer avec méthode classique et choisir la meilleure

---

## 4. Bonnes Pratiques Identifiées

### 4.1 Sélection des Étoiles de Référence

1. **Critères de qualité :**
   - Magnitude : limite selon le catalogue (Gaia: ~21 mag)
   - Nombre : minimum 10-20 étoiles bien distribuées
   - Distribution spatiale : couvrir tout le champ
   - Qualité photométrique : SNR suffisant

2. **Rejet des outliers :**
   - Identifier les étoiles avec résidus > 3σ
   - Itérer le fit WCS en excluant les outliers
   - Considérer les doubles étoiles non résolues

### 4.2 Traitement des Observations Multi-Observatoires

**Points clés :**
- Harmonisation des systèmes de référence
- Correction des effets systématiques (réfraction, parallaxe)
- Validation croisée entre observatoires

**Pour notre cas (observatoire unique) :**
- S'assurer de la cohérence temporelle
- Vérifier la stabilité du WCS entre images
- Analyser les tendances dans les résidus

### 4.3 Reporting et Documentation

**Métadonnées importantes :**
- Catalogue utilisé (Gaia DR3)
- Nombre d'étoiles de référence
- RMS astrométrique (RA, Dec, total)
- Méthode utilisée (classique, zero-aperture)
- Incertitudes estimées

---

## 5. Recommandations d'Amélioration pour Notre Code

### 5.1 Calcul des Résidus et Statistiques

**À implémenter :**
```python
# Calcul des résidus pour chaque étoile
residuals_ra = (calc_ra - catalog_ra) * np.cos(np.radians(catalog_dec))
residuals_dec = calc_dec - catalog_dec
residuals_total = np.sqrt(residuals_ra**2 + residuals_dec**2)

# Statistiques
rms_ra = np.sqrt(np.mean(residuals_ra**2))
rms_dec = np.sqrt(np.mean(residuals_dec**2))
rms_total = np.sqrt(np.mean(residuals_total**2))
median_residual = np.median(residuals_total)

# Identification des outliers
outlier_mask = residuals_total > 3 * np.std(residuals_total)
```

### 5.2 Validation de Qualité Avancée

**Ajouter :**
- Test de normalité des résidus (Shapiro-Wilk ou Anderson-Darling)
- Analyse des résidus en fonction de la position (distorsions)
- Analyse des résidus en fonction de la magnitude (biais photométrique)
- Calcul du chi² réduit

### 5.3 Amélioration de l'Extrapolation Zero-Aperture

**Considérer :**
- Extrapolation quadratique : RMS = a × aperture² + b × aperture + c
- Validation du fit (R², erreur standard)
- Comparaison avec fit linéaire
- Choix automatique de la meilleure méthode

### 5.4 Documentation des Résultats

**Ajouter au header FITS :**
```python
header['ASTREF'] = ('Gaia DR3', 'Astrometric reference catalog')
header['ASTNREF'] = (n_matches, 'Number of reference stars')
header['ASTRRMSR'] = (rms_ra, 'Astrometric RMS RA (arcsec)')
header['ASTRRMSD'] = (rms_dec, 'Astrometric RMS Dec (arcsec)')
header['ASTRRMS'] = (rms_total, 'Astrometric RMS total (arcsec)')
header['ASTRMED'] = (median_residual, 'Median residual (arcsec)')
header['ASTMETHOD'] = ('zero-aperture' or 'classical', 'Method used')
```

---

## 6. Références Bibliographiques Clés

1. **Gaia Collaboration (2021)** - Gaia DR3 catalogue
2. **Chesley et al. (2010)** - Méthodes d'incertitude astrométrique
3. **Farnocchia et al. (2015)** - Validation d'observations astrométriques
4. **Baer et al. (2011)** - Amélioration des incertitudes
5. **Carpino et al. (2003)** - Propagation d'incertitudes orbitales

---

## 7. Notes d'Implémentation

### Statut actuel :
- ✅ Utilisation de Gaia via astroquery
- ✅ Méthode zero-aperture implémentée
- ✅ Méthode classique implémentée
- ✅ Calcul RMS de base
- ✅ Cache Gaia pour performance

### À améliorer :
- ⚠️ Calcul séparé RMS RA/Dec
- ⚠️ Statistiques avancées (médiane, outliers)
- ⚠️ Validation de qualité (tests statistiques)
- ⚠️ Documentation complète dans header FITS
- ⚠️ Extrapolation quadratique optionnelle

---

**Date de création :** 2025-01-02  
**Dernière mise à jour :** 2025-01-02  
**Référence originale :** Farnocchia et al. 2022, PSJ, 3:156







