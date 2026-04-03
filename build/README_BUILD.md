# Système de Build pour Distributions Partielles NPOAP

Ce système permet de créer des distributions partielles de NPOAP en excluant physiquement les fichiers non nécessaires selon le profil choisi.

## Structure

```
build/
├── profiles.json              # Définition des profils de distribution
├── dependency_analyzer.py      # Analyseur de dépendances Python
├── build_distribution.py       # Script principal de build
├── build.bat                  # Script batch Windows
└── README_BUILD.md            # Ce fichier
```

## Profils Disponibles

### 1. `exoplanets`
Distribution spécialisée pour la photométrie d'exoplanètes :
- 🏠 Accueil
- 🌙 Éphémérides
- 🔭 Photométrie Exoplanètes
- 📈 Analyse de Données
- 🛠️ Réduction de Données

**Fichiers exclus** : Astéroïdes, Transitoires, Étoiles Binaires, Lucky Imaging, Spectroscopie

### 2. `asteroids` — Photométrie astéroïdes  
### 3. `binary_stars` — Étoiles doubles + Easy Lucky Imaging  
### 4. `spectroscopy` — Spectroscopie  
### 5. `full` — Distribution complète avec tous les modules.

## Utilisation

### Windows (Batch)

```cmd
cd build
build.bat exoplanets
```

### Python Direct

```bash
cd build
python build_distribution.py exoplanets
```

### Avec répertoire de sortie personnalisé

```bash
python build_distribution.py exoplanets C:\path\to\output
```

## Résultat

Le script génère :

1. **Répertoire de build** : `build/distributions/{profile_name}/`
   - Contient uniquement les fichiers nécessaires
   - Structure : `gui/`, `core/`, `utils/`, `config/`, `docs/`
   - `main_window.py` généré automatiquement selon le profil

2. **Archive ZIP** : `build/distributions/{profile_name}.zip`
   - Archive prête à distribuer

## Fonctionnement

### 1. Analyse des Dépendances

Le système :
- Identifie les onglets activés dans le profil
- Analyse récursivement tous les imports Python
- Trouve tous les fichiers `core/`, `gui/`, `utils/` nécessaires
- Évite les dépendances circulaires

### 2. Génération de `main_window.py`

Un `main_window.py` personnalisé est généré qui :
- Importe uniquement les onglets activés
- Initialise uniquement les onglets nécessaires
- Ajoute uniquement les onglets activés au notebook

### 3. Exclusion Physique

Les fichiers non nécessaires sont **physiquement exclus** de la distribution :
- Pas de fichiers `gui/*.py` pour les onglets désactivés
- Pas de fichiers `core/*.py` non utilisés
- Archive plus légère et plus sécurisée

## Personnalisation

### Ajouter un Nouveau Profil

Éditez `profiles.json` :

```json
{
  "mon_profil": {
    "name": "Mon Profil Personnalisé",
    "description": "Description du profil",
    "enabled_tabs": {
      "home": true,
      "ephemerides": true,
      ...
    },
    "required_core_modules": [
      "photometry_pipeline",
      ...
    ],
    "required_gui_modules": [
      "home_tab",
      ...
    ],
    "required_utils": [
      "logging_handler",
      ...
    ]
  }
}
```

### Modifier les Dépendances

Le système analyse automatiquement les imports, mais vous pouvez :
- Ajouter des modules explicitement dans `required_core_modules`
- Forcer l'inclusion de fichiers spécifiques

## Limitations

1. **Dépendances dynamiques** : Les imports dynamiques (`__import__()`, `importlib`) ne sont pas détectés
2. **Dépendances conditionnelles** : Les imports dans des blocs `if` peuvent être manqués
3. **Fichiers de données** : Les fichiers non-Python (images, données) ne sont pas gérés automatiquement

## Dépannage

### Erreur "Module not found"

Si un module manque après le build :
1. Vérifiez qu'il est listé dans `required_core_modules` ou `required_utils`
2. Vérifiez que le fichier existe dans le répertoire source
3. Ajoutez-le explicitement au profil

### Dépendances manquantes

Si des dépendances ne sont pas détectées :
1. Vérifiez les imports dans les fichiers source
2. Ajoutez les modules manquants explicitement dans le profil
3. Vérifiez la profondeur d'analyse (max_depth dans `dependency_analyzer.py`)

## Exemple de Sortie

```
============================================================
Construction de la distribution: NPOAP Minimal
Description: Distribution exoplanètes (photométrie, analyse, TTV)
============================================================

Analyse des dépendances...

Fichiers identifiés:
  - GUI: 5 fichiers
  - Core: 8 fichiers
  - Utils: 3 fichiers
  - Root: 2 fichiers

Copie des fichiers...
  ✓ main.py
  ✓ config.py
  ✓ gui/home_tab.py
  ✓ gui/night_observation_tab.py
  ✓ gui/photometry_exoplanets_tab.py
  ...

Génération de main_window.py...
✓ Généré build/distributions/exoplanets/gui/main_window.py

Génération de tabs_config.py...
✓ Généré build/distributions/exoplanets/config/tabs_config.py

============================================================
✓ Distribution 'exoplanets' construite avec succès!
  Répertoire: build/distributions/exoplanets
============================================================

Création de l'archive build/distributions/exoplanets.zip...
✓ Archive créée: build/distributions/exoplanets.zip
```
