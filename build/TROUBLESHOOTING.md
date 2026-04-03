# Guide de Dépannage - Système de Build NPOAP

## Problèmes courants et solutions

### 1. `build.bat ne marche pas`

#### Problème : "Python n'est pas trouvé dans le PATH"

**Solution 1 : Vérifier que Python est installé**
```cmd
python --version
```
Si cela ne fonctionne pas, essayez :
```cmd
py --version
```
ou
```cmd
python3 --version
```

**Solution 2 : Utiliser le script PowerShell**
```powershell
cd build
.\build.ps1 exoplanets
```

**Solution 3 : Exécuter directement Python**
```cmd
cd build
python build_distribution.py exoplanets
```

Si Python n'est pas installé, installez-le depuis [python.org](https://www.python.org/downloads/)

---

#### Problème : "build_distribution.py non trouvé"

**Solution :**
Vérifiez que vous êtes dans le bon répertoire :
```cmd
cd build
dir build_distribution.py
```

Si le fichier n'existe pas, vérifiez que tous les fichiers du système de build sont présents :
- `build_distribution.py`
- `dependency_analyzer.py`
- `profiles.json`

---

#### Problème : "Module dependency_analyzer not found"

**Solution :**
Vérifiez que `dependency_analyzer.py` existe dans le répertoire `build/` :
```cmd
cd build
dir dependency_analyzer.py
```

Si le fichier n'existe pas, recréez-le depuis le code source.

---

#### Problème : "profiles.json non trouvé"

**Solution :**
Vérifiez que le fichier `profiles.json` existe :
```cmd
cd build
dir profiles.json
```

Si le fichier n'existe pas, vérifiez que vous êtes dans le bon répertoire (`build/`) et que le fichier a été créé.

---

### 2. Erreurs lors de l'exécution

#### Problème : "Profile 'xxx' non trouvé"

**Solution :**
Vérifiez les profils disponibles dans `profiles.json` :
```json
{
  "exoplanets": { ... },
  "asteroids": { ... },
  "full": { ... }
}
```

Utilisez un profil valide :
- `exoplanets`
- `asteroids`
- `binary_stars`
- `spectroscopy`
- `full`

---

#### Problème : "Erreur lors de l'analyse de dépendances"

**Cause possible :** Syntaxe Python incorrecte dans un fichier source.

**Solution :**
1. Vérifiez que tous les fichiers Python sont valides :
```cmd
python -m py_compile gui/*.py
python -m py_compile core/*.py
```

2. Vérifiez les logs d'erreur pour identifier le fichier problématique.

---

#### Problème : "Fichier manquant après le build"

**Cause possible :** Dépendance non détectée automatiquement.

**Solution :**
1. Ajoutez le fichier explicitement dans `profiles.json` :
```json
{
  "exoplanets": {
    "required_core_modules": [
      "photometry_pipeline",
      "mon_module_manquant"  // Ajoutez ici
    ]
  }
}
```

2. Vérifiez que le fichier existe dans le répertoire source.

---

### 3. Tests et débogage

#### Tester l'analyseur de dépendances
```cmd
cd build
python test_build.py
```

#### Tester un profil spécifique
```cmd
cd build
python build_distribution.py exoplanets
```

#### Vérifier les fichiers générés
```cmd
cd build\distributions\exoplanets
dir /s
```

---

### 4. Messages d'erreur spécifiques

#### "UnicodeDecodeError" ou problèmes d'encodage

**Solution :**
Assurez-vous que tous les fichiers Python sont en UTF-8 :
```python
# En haut de chaque fichier
# -*- coding: utf-8 -*-
```

---

#### "Permission denied" lors de la création d'archive

**Solution :**
1. Fermez toute application qui pourrait utiliser les fichiers (explorateur Windows, etc.)
2. Vérifiez les permissions du répertoire `build/distributions/`
3. Exécutez en tant qu'administrateur si nécessaire

---

#### "ImportError: No module named 'ast'"

**Solution :**
Mettez à jour Python. Le module `ast` fait partie de la bibliothèque standard depuis Python 2.6 :
```cmd
python --version
```
Utilisez Python 3.6 ou supérieur.

---

## Commandes utiles

### Lister tous les fichiers du répertoire build
```cmd
cd build
dir /s
```

### Vérifier la structure des répertoires
```
build/
├── build_distribution.py
├── dependency_analyzer.py
├── profiles.json
├── build.bat
├── build.ps1
└── __init__.py
```

### Vérifier que Python fonctionne
```cmd
python -c "import sys; print(sys.version)"
```

---

## Support

Si le problème persiste :

1. Vérifiez les logs d'erreur complets
2. Vérifiez que tous les fichiers nécessaires sont présents
3. Vérifiez la version de Python (`python --version`)
4. Essayez de reconstruire tous les fichiers depuis le code source
