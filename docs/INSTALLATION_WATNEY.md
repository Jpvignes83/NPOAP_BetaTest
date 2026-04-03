# Installation de Watney Astrometry pour NPOAP

## 📍 Où installer Watney ?

NPOAP utilise le **CLI Watney** (`watney-solve.exe`) pour l'astrométrie locale. Pas besoin de service API, le CLI s'exécute directement.

### Structure d'installation recommandée

Créez un dossier dédié pour Watney, par exemple :

```
C:\watney\
├── watney-solve.exe        ← Exécutable CLI Watney (NÉCESSAIRE)
├── db\                      ← Base de données de quads (catalogues)
│   ├── index-*.db
│   └── ...
└── README.txt              ← Notes personnelles
```

### 📥 Étape 1 : Télécharger le CLI Watney

1. **Allez sur** : https://github.com/Jusas/WatneyAstrometry/releases
2. **Dans la liste des releases**, cherchez la version la plus récente
3. **Cherchez dans les "Assets"** (fichiers téléchargeables) :
   - Le fichier pour Windows peut s'appeler :
     - `WatneyAstrometry.SolverApp-win-x64.zip` (ou `.tar.gz`)
     - `watney-solve-win-x64.exe`
     - `SolverApp-win-x64.zip`
   - Cherchez celui qui contient **"SolverApp"** ou **"solve"** dans le nom
   - **Évitez** les fichiers avec **"WebApi"** ou **"Desktop"** dans le nom
4. **Téléchargez** le fichier
5. **Extrayez** le fichier ZIP (si nécessaire)
6. **Trouvez** `watney-solve.exe` dans le contenu extrait
7. **Copiez** `watney-solve.exe` dans un dossier accessible, par exemple :
   - `C:\watney\` (recommandé)
   - `C:\Program Files\Watney\`
   - Ou n'importe quel autre emplacement

**Note** : Si vous ne trouvez pas `watney-solve.exe` directement, cherchez un fichier `.exe` dans le dossier extrait. Il peut s'appeler `SolverApp.exe` ou simplement être dans un sous-dossier.

### 🔍 Comment tester que l'installation est correcte

Une fois que vous avez `watney-solve.exe`, ouvrez une **invite de commande Windows** et exécutez :

```cmd
cd C:\watney
watney-solve.exe --help
```

**OU** si vous l'avez installé ailleurs :

```cmd
cd "chemin\vers\votre\dossier"
watney-solve.exe --help
```

Si cela affiche l'aide (liste des options), l'installation est correcte ✅

**Si vous obtenez une erreur "fichier introuvable"** :
- Vérifiez que vous êtes dans le bon dossier (où se trouve `watney-solve.exe`)
- Ou utilisez le chemin complet : `C:\watney\watney-solve.exe --help`

### 📥 Étape 2 : Télécharger la base de données de quads

1. **Allez sur** : https://github.com/Jusas/WatneyAstrometry/releases/tag/watneyqdb3
2. **Téléchargez** les fichiers de la base de données (`.db` files)
3. **Créez un dossier** pour la base, par exemple : `C:\watney\db\`
4. **Décompressez** tous les fichiers `.db` dans ce dossier

**Note** : La base de données peut être volumineuse (plusieurs Go). Assurez-vous d'avoir suffisamment d'espace disque.

### ⚙️ Étape 3 : Configuration dans NPOAP

Ouvrez `config.py` et configurez les chemins :

```python
# Dans config.py
WATNEY_SOLVE_EXE = Path("C:/watney/watney-solve.exe")  # Chemin vers le CLI
WATNEY_QUAD_DB_PATH = Path("C:/watney/db")              # Chemin vers la base de données
```

**Note** : Si `watney-solve.exe` est dans le PATH système, vous pouvez laisser `WATNEY_SOLVE_EXE = None`.

### ✅ Étape 4 : Vérifier l'installation

Testez l'installation dans une invite de commande :

```cmd
cd C:\watney
watney-solve.exe --help
```

Si cela affiche l'aide, l'installation est correcte.

### ✅ Étape 5 : Utiliser dans NPOAP

Dans NPOAP :
1. Allez dans l'onglet **"Réduction de données"**
2. Cliquez sur **"🔷 Watney (API REST locale)"** (le nom du bouton reste à jour)
3. L'astrométrie commence directement, **pas besoin de démarrer de service**

## 📝 Notes importantes

- **Pas besoin de service** : Le CLI s'exécute directement, pas besoin de démarrer un service API
- **Pas besoin d'internet** : Une fois les catalogues téléchargés, tout fonctionne hors ligne
- **Exécution directe** : NPOAP appelle `watney-solve.exe` pour chaque image à résoudre
- **Fonctionnement natif Windows** : Pas besoin de WSL ou Ubuntu, tout est natif Windows

## 🆘 Dépannage

### Erreur "watney-solve.exe introuvable"

- Vérifiez que `watney-solve.exe` est bien dans le dossier indiqué
- Vérifiez le chemin dans `config.py` : `WATNEY_SOLVE_EXE`
- Ou ajoutez `watney-solve.exe` au PATH système Windows

### Erreur "Base de données introuvable"

- Vérifiez que tous les fichiers `.db` sont dans le dossier `db\`
- Vérifiez le chemin dans `config.py` : `WATNEY_QUAD_DB_PATH`
- Vérifiez que les fichiers `.db` ne sont pas dans un sous-dossier

### Erreur lors de la résolution

- Vérifiez les logs dans NPOAP pour voir les messages d'erreur détaillés
- Testez manuellement : `watney-solve.exe --input image.fits --quad-db C:\watney\db`
- Consultez la documentation Watney : https://github.com/Jusas/WatneyAstrometry/wiki
