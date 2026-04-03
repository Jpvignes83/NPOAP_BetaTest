# Format AAVSO Exosite pour les Observations d'Exoplanètes

**Source:** [AAVSO Exoplanet Database WebObs Documentation](https://apps.aavso.org/exosite/doc)

**Révision:** 1.0

**Date de référence:** Janvier 2026

---

## I. Introduction

Ce document décrit le format requis pour soumettre des observations d'exoplanètes à la base de données AAVSO Exoplanet Database via la page WebObs.

**Documents connexes disponibles sur <http://astrodennis.com>:**
1. "A Practical Guide to Exoplanet Observing"
2. "User Guide: AstroImageJ Macro for Creating an AAVSO Exoplanet Report"

**Note:** Veuillez consulter les [AAVSO Data Usage Guidelines](https://www.aavso.org/data-usage-guidelines).

---

## II. Page WebObs AAVSO Exosite

La page principale pour télécharger les données d'exoplanètes se trouve ici: [AAVSO Exosite WebObs](https://apps.aavso.org/exosite/webobs)

Il est nécessaire que l'utilisateur se soit d'abord connecté au site principal AAVSO avec son nom d'utilisateur et son mot de passe AAVSO pour utiliser la page WebObs Exosite.

### Éléments requis sur la page WebObs:

1. **Profils de site et d'équipement** associés à cette observation. Ces profils peuvent être définis sur la page: [Site & Equipment](https://apps.aavso.org/exosite/siteequipment)

2. **Localisation d'une ou plusieurs images** associées à cette observation, à télécharger vers la base de données. Au minimum, une image doit être téléchargée montrant un champ d'étoiles résolu (plate solved) qui inclut l'étoile cible et l'ensemble final d'étoiles de comparaison qui ont fait partie de l'observation d'exoplanète. Ces images peuvent être dans n'importe quel format d'image courant. Ne pas inclure plus de 10 fichiers et la taille totale de tous les fichiers soumis doit être inférieure à 2 Mb.

3. **Fichier ASCII** qui représente le "rapport" de l'observation d'exoplanète. Ce fichier doit suivre le format décrit ci-dessous.

---

## III. Format du Rapport Exoplanète

Le format du rapport d'exoplanète a deux composants: **paramètres** et **données**, où cette dernière représente une série de mesures prises pendant le temps de l'observation.

### A. Paramètres

Les paramètres sont spécifiés au début du fichier et sont utilisés pour décrire les données de mesure qui suivent. Les paramètres doivent commencer par un signe dièse (#) au début de la ligne.

**Les paramètres requis sont:**

| Paramètre | Description | Limite |
|-----------|-------------|--------|
| `#TYPE=` | Doit être **EXOPLANET** | - |
| `#OBSCODE=` | Le code d'observateur officiel AAVSO pour l'observateur principal des données soumises | 5 caractères |
| `#SOFTWARE=` | Nom et version du logiciel utilisé pour créer l'observation. Si c'est un logiciel privé, mettre une description ici. Exemple: `#SOFTWARE=AIJ Version 3.2` | 255 caractères |
| `#DELIM=` | Le délimiteur utilisé pour séparer les champs dans la section données du rapport. Délimiteurs autorisés: `,` `;` `\|` `:` `!` `/` `?`. Vous pouvez utiliser une tabulation comme délimiteur, en indiquant ce choix avec le mot 'tab'. | - |
| `#DATE_TYPE=` | Le type de référence temporelle pour les dates/heures utilisées dans la section données du fichier. Les temps sont au milieu de l'observation. Les données à une précision de millisecondes (i.e., 8 décimales) sont acceptables. Valeurs valides: `JD_UTC`, `HJD_UTC`, `BJD_UTC`, `BJD_TT`, `BJD_TDB` | - |
| `#OBSTYPE=` | Le type d'équipement utilisé pour faire les mesures dans le fichier de données. Peut être **CCD** ou **DSLR**. Si vous utilisez une caméra CMOS, soumettez ce champ comme CCD et notez le type réel de caméra dans la section NOTES ci-dessous. | - |
| `#STAR_NAME=` | Nom de l'étoile hôte autour de laquelle l'exoplanète orbite. L'étoile **doit** être reconnue dans MAST. Cela inclura toutes les cibles trouvées dans les diverses campagnes d'exoplanètes telles que Kepler, TESS, etc. Idéalement, ce sera un AUID AAVSO ou le nom d'une étoile reconnue par VSX. | 100 caractères |
| `#EXOPLANET_NAME=` | Le nom de l'exoplanète. Idéalement, ce devrait être le Nom de l'Étoile avec un suffixe en minuscule 'b', 'c', 'd', etc. Cependant, cela peut aussi être le nom arbitraire d'une exoplanète utilisée dans une campagne d'exoplanètes. | 100 caractères |
| `#BINNING=` | 1x1, 2x2, 3x3, ou 4x4. C'est le binning utilisé par la caméra d'imagerie. | - |
| `#EXPOSURE_TIME=` | Le temps d'exposition en secondes. | ≤ 600 secondes |
| `#FILTER=` | Désignation de filtre AAVSO valide. Doit être un des noms courts de 2-3 lettres de la liste des désignations de filtres AAVSO (voir Annexe B). Certaines observations d'exoplanètes peuvent également être faites en utilisant un CBB (Clear Blue Blocking ou filtre dit Exoplanet). Si un filtre n'est pas utilisé, ou si un filtre clair est utilisé, alors le type de filtre CV doit être utilisé. | - |
| `#DETREND_PARAMETERS=` | Une liste séparée par des virgules nommant les paramètres de détendance dont les données sont incluses dans les enregistrements de données suivants. Vous pouvez lister 0 à 4 noms ici et vous devez ensuite avoir le nombre correspondant de colonnes à la fin de chaque ligne dans vos enregistrements de données ci-dessous pour contenir les données de détendance réelles pour chaque mesure. | 100 caractères |
| `#MEASUREMENT_TYPE=` | Une indication de la façon dont chaque mesure dans les enregistrements de données doit être interprétée. **Rnflux** indique un flux normalisé relatif. La normalisation est effectuée par référence aux données en dehors du transit observé (non prédit), à la fois avant et après le transit, et le résultat est attendu nominalement à 1.0 car vous divisez le flux brut par cette moyenne prise des données en dehors du transit. **Dmag**, magnitude différentielle, doit être normalisée de manière similaire et est attendue nominalement à 0.0 car vous prenez la moyenne des données en dehors du transit et la soustrayez de toutes les données brutes. Notez que les données sont censées être des données brutes, sans la série de détendance appliquée. La logique est que vous fournissez les données de détendance que vous avez trouvées utiles dans votre analyse du transit. Mais d'autres personnes pourraient avoir des modèles différents, qui appliqueront les données de détendance différemment. Cette base de données est censée fournir des données brutes pour leur propre analyse. | - |

**Paramètres optionnels:**

| Paramètre | Description | Limite |
|-----------|-------------|--------|
| `#SECONDARY_OBSCODES=` | Une liste séparée par des virgules des codes d'observateur officiels AAVSO pour tout observateur secondaire associé à cette observation. | 60 caractères |
| `#PRIORS=` | Champ libre pour noter les "priors" utilisés pour modéliser ce transit d'exoplanète - par exemple, période, rayon de l'étoile hôte, coefficients d'assombrissement du limbe | 250 caractères |
| `#RESULTS=` | Champ libre pour noter les résultats d'observation, incluant, par exemple, (Rp/R*)^2, a/R*, Tc, et inclinaison. | 250 caractères |
| `#NOTES=` | Description libre de cette observation. Cela pourrait inclure une description des conditions météorologiques, des systématiques associées à cette observation, d'autres anomalies, déviation de pixel d'image, etc. | Aucune limite |

**Note importante:** Le format des paramètres est sensible à la casse, comme montré dans l'exemple de l'Annexe A.

Les commentaires personnels peuvent également être ajoutés tant qu'ils suivent un signe dièse (#). Ces commentaires divers seront ignorés par le logiciel WebObs et ne seront pas chargés dans la base de données. Cependant, ils seront conservés lorsque le fichier complet sera stocké dans les archives permanentes AAVSO.

### B. Données

Les données de mesure observationnelle réelles suivent les paramètres. Il devrait y avoir une mesure par ligne et les champs devraient être séparés par le même caractère que celui défini dans le champ de paramètre DELIM. Un "na" ou "n/a" devrait être placé dans les champs d'Erreur de Mesure ou Données de Détendance si aucune donnée n'existe pour le champ respectif, bien que laisser le champ de données vide soit également acceptable.

**La liste des champs de données dans chaque ligne de données:**

1. **Date:** La date de la mesure, du type spécifié dans le paramètre d'en-tête DATE.
2. **Measurement Data:** La valeur de la mesure différentielle du type spécifié dans le paramètre d'en-tête MEASUREMENT_TYPE. Champ décimal (15,8). Notez que ces données ne sont pas détendues. C'est-à-dire, ce sont des données brutes; les données de détendance qui suivent n'ont pas été appliquées.
3. **Measurement Error:** Incertitude photométrique associée aux données de mesure. Champ décimal (12, 6). Si non disponible, mettre "na", "n/a", ou laisser vide.
4. **Detrend data_1:** La première de jusqu'à quatre (4) paramètres de détendance dans le même ordre et autant qu'il y en a dans le champ DETREND_PARAMETERS de l'en-tête. Champ décimal (12, 6). Si non utilisé, mettre "na", "n/a", ou laisser vide. Cela s'applique également aux autres champs Detrend ci-dessous.
5. **Detrend data_2:** La deuxième de jusqu'à quatre (4) paramètres de détendance.
6. **Detrend data_3:** La troisième de jusqu'à quatre (4) paramètres de détendance.
7. **Detrend data_4:** La quatrième de jusqu'à quatre (4) paramètres de détendance.

---

## IV. Annexe A: Exemple de Rapport Exoplanète

```
#TYPE=EXOPLANET
#OBSCODE=CDEC
#SOFTWARE=AstroImageJ
#DELIM=,
#DATE_TYPE=BJD_TDB
#OBSTYPE=CCD
#STAR_NAME=Wasp-12
#EXOPLANET_NAME=Wasp-12b
#BINNING=2x2
#EXPOSURE_TIME=45
#FILTER=V
#DETREND_PARAMETERS=Airmass
#MEASUREMENT_TYPE=Rnflux
#SECONDARY_OBSCODES=CDEC1,CDEC2
#PRIORS=Period=1.09142,R*=1.63,u1=0.391,u2=0.3027
#RESULTS=Depth=0.0128,a/R*=3.2165.Tc=24557393.601332
#NOTES=Seeing was very good, no known systematics
# DATE DIFF MERR DETREND_1 DETREND_2 DETREND_3 DETREND_4
2457393.50269,0.515620,0.001884,1.867946,n/a,n/a,n/a
2457393.50327,0.508506,0.001858,1.859892,n/a,n/a,n/a
2457393.50384,0.508466,0.001848,1.851973,n/a,n/a,n/a
2457393.50442,0.515412,0.001864,1.844246,n/a,n/a,n/a
2457393.50500,0.512654,0.001854,1.836449,n/a,n/a,n/a
2457393.50557,0.510856,0.001856,1.828740,n/a,n/a,n/a
```

---

## V. Annexe B: Liste des Noms de Filtres Standards AAVSO

La liste de référence complète est disponible sur: https://vsx.aavso.org/index.php?view=api.bands

Voici une liste courte des filtres les plus susceptibles d'être utilisés:

| Code | Nom | Description |
|------|-----|-------------|
| CV | Clear | Pas de filtre |
| CBB | Clear Blue Blocking | Parfois appelé filtre 'Exoplanet' |
| U | Johnson U | - |
| B | Johnson B | - |
| V | Johnson V | - |
| R | Cousins R | - |
| I | Cousins I | - |
| SZ | Sloan z | - |
| SU | Sloan u | - |
| SG | Sloan g | - |
| SR | Sloan r | - |
| SI | Sloan i | - |
| TG | Green Filter | Tri-color green. Communément le 'canal vert' dans une caméra DSLR ou CCD couleur. |
| TB | Blue Filter | Tri-color blue. Communément le 'canal bleu' dans une caméra DSLR ou CCD couleur. |
| TR | Red Filter | Tri-color red. Communément le 'canal rouge' dans une caméra DSLR ou CCD couleur. |
| O | Other | Autre filtre non listé ci-dessus, doit décrire dans Notes |

---

## VI. Notes d'Implémentation pour NPOAP

Cette documentation peut être utilisée pour:

1. **Créer une fonction d'export AAVSO** dans l'onglet de photométrie d'exoplanètes (`gui/photometry_exoplanets_tab.py`)
2. **Valider les données** avant l'export pour s'assurer qu'elles respectent le format AAVSO
3. **Générer automatiquement les paramètres requis** à partir des métadonnées d'observation
4. **Convertir les données normalisées** au format Rnflux ou Dmag selon les spécifications AAVSO

### Exemple de fonction d'export (pseudocode):

```python
def export_to_aavso_format(observation_data, metadata):
    """
    Exporte les données d'observation d'exoplanète au format AAVSO Exosite.
    
    Parameters:
    -----------
    observation_data : DataFrame
        Données contenant: timestamp, flux_normalise, erreur, detrend_params
    metadata : dict
        Dictionnaire contenant tous les paramètres requis (#TYPE, #OBSCODE, etc.)
    
    Returns:
    --------
    str : Contenu du fichier formaté selon les spécifications AAVSO
    """
    # Générer les en-têtes de paramètres
    # Formater les données selon le délimiteur spécifié
    # Retourner le contenu du fichier
```

---

## Références

- [Documentation officielle AAVSO Exosite](https://apps.aavso.org/exosite/doc)
- [Page WebObs AAVSO Exosite](https://apps.aavso.org/exosite/webobs)
- [Site & Equipment Profiles](https://apps.aavso.org/exosite/siteequipment)
- [AAVSO Filter Bands API](https://vsx.aavso.org/index.php?view=api.bands)
- [AAVSO Data Usage Guidelines](https://www.aavso.org/data-usage-guidelines)

