# Compilation et Obtention des Exécutables Watney

**IMPORTANT** : Watney Astrometry est un projet **C#/.NET**, pas C++. Si vous avez des fichiers C++, c'est peut-être un autre projet.

Si vous avez le code source C# de Watney Astrometry mais pas les exécutables, voici comment les obtenir.

## Option 1 : Télécharger les Exécutables Précompilés (RECOMMANDÉ)

Les exécutables précompilés sont disponibles dans les **releases GitHub** du projet :

### 📥 Télécharger depuis GitHub Releases

1. **Allez sur** : https://github.com/Jusas/WatneyAstrometry/releases

2. **Recherchez les exécutables suivants** dans les releases :

   - **`watney-solve.exe`** ou **`WatneyAstrometry.SolverApp-win-x64.zip`**
     - Pour l'astrométrie (déjà installé normalement)
     - Cherchez dans les assets de la release principale
   
   - **`WatneyAstrometry.GaiaStarExtractor.exe`** ou **`GaiaStarExtractor-win-x64.zip`**
     - Pour créer les fichiers `.db` à partir des CSV Gaia
     - Peut être dans une release séparée ou dans les assets
   
   - **`WatneyAstrometry.QuadBuilder.exe`** ou **`QuadBuilder-win-x64.zip`**
     - Pour créer les fichiers `.qdb` à partir des `.db`
     - Peut être dans une release séparée ou dans les assets

3. **Téléchargez et extrayez** les fichiers dans `C:\watney\`

### Structure recommandée après téléchargement

```
C:\watney\
├── watney-solve.exe                    ← Pour l'astrométrie
├── WatneyAstrometry.GaiaStarExtractor.exe  ← Pour créer .db (Section 5)
├── WatneyAstrometry.QuadBuilder.exe    ← Pour créer .qdb (Section 6)
└── db\
    └── (fichiers .qdb ou .db)
```

## Option 2 : Compiler depuis le Code Source C++

Si les exécutables ne sont pas disponibles en releases, vous devez compiler les projets C++.

### Prérequis pour la Compilation

1. **.NET SDK** (Version 6.0 ou supérieure - REQUIS)
   - Téléchargement : https://dotnet.microsoft.com/download
   - Vérifiez l'installation : `dotnet --version` dans une invite de commande

2. **Visual Studio 2022** (optionnel, mais recommandé)
   - Avec les composants .NET Desktop Development
   - Téléchargement : https://visualstudio.microsoft.com/

**Note** : Le projet est en C#/.NET, PAS en C++. Les fichiers que vous voyez avec `.cs` sont les fichiers sources C#.

### Structure des Projets Watney

Le projet Watney Astrometry est généralement organisé en plusieurs solutions/projets :

- **SolverApp** → Compile en `watney-solve.exe` ou `SolverApp.exe`
- **GaiaStarExtractor** → Compile en `WatneyAstrometry.GaiaStarExtractor.exe`
- **QuadBuilder** → Compile en `WatneyAstrometry.QuadBuilder.exe`

### Étapes de Compilation

#### 1. Télécharger le Code Source

```bash
git clone https://github.com/Jusas/WatneyAstrometry.git
cd WatneyAstrometry
```

#### 2. Compiler avec .NET CLI (RECOMMANDÉ - Plus Simple)

**Pour `GaiaStarExtractor` :**
```bash
cd WatneyAstrometry
cd WatneyAstrometry.GaiaStarExtractor
dotnet build -c Release
```
L'exécutable sera dans `bin\Release\net6.0\` ou `bin\Release\net8.0\`

**Pour `QuadBuilder` ou `GaiaQuadDatabaseCreator` :**
```bash
cd WatneyAstrometry
cd WatneyAstrometry.GaiaQuadDatabaseCreator  # Ou QuadBuilder selon le nom
dotnet build -c Release
```
L'exécutable sera dans `bin\Release\net6.0\` ou `bin\Release\net8.0\`

#### 3. Alternative : Ouvrir dans Visual Studio

- Ouvrez `WatneyAstrometry.sln` dans Visual Studio
- Cherchez les projets `.csproj` :
  - `WatneyAstrometry.GaiaStarExtractor.csproj`
  - `WatneyAstrometry.GaiaQuadDatabaseCreator.csproj` (ou `QuadBuilder.csproj`)
- Clic droit → **Build** ou **Rebuild**
- L'exécutable sera dans `bin\Release\net6.0\` ou `bin\Release\net8.0\`

#### 4. Copier les Exécutables

Une fois compilés, copiez les `.exe` dans `C:\watney\`

### Configuration Build Release

Pour de meilleures performances, compilez en **Release** (pas Debug) :

1. Dans Visual Studio, changez la configuration : **Build → Configuration Manager → Release**
2. Rebuild tous les projets
3. Les exécutables seront dans `bin\Release\` ou `x64\Release\`

## Option 3 : Chercher dans le Code Source Téléchargé

Si vous avez téléchargé le code source, les exécutables peuvent déjà être présents :

1. Cherchez dans les dossiers :
   - `bin/`
   - `build/`
   - `output/`
   - `artifacts/`
   - `WatneyAstrometry.GaiaStarExtractor/bin/`
   - `WatneyAstrometry.QuadBuilder/bin/`

2. Recherchez les fichiers `.exe` :
   ```powershell
   # Dans PowerShell, depuis la racine du projet
   Get-ChildItem -Recurse -Filter "*.exe" | Where-Object { $_.Name -like "*Gaia*" -or $_.Name -like "*Quad*" }
   ```

## Configuration dans config.py

Une fois que vous avez les exécutables, configurez-les dans `config.py` :

```python
from pathlib import Path

# Exécutables Watney
WATNEY_SOLVE_EXE = Path("C:/watney/watney-solve.exe")
WATNEY_GAIA_EXTRACTOR_EXE = Path("C:/watney/WatneyAstrometry.GaiaStarExtractor.exe")
WATNEY_QUAD_BUILDER_EXE = Path("C:/watney/WatneyAstrometry.QuadBuilder.exe")

# Base de données
WATNEY_QUAD_DB_PATH = Path("C:/watney/db")
```

## Vérification des Exécutables

Testez chaque exécutable dans une invite de commande :

```cmd
# Tester GaiaStarExtractor
C:\watney\WatneyAstrometry.GaiaStarExtractor.exe --help

# Tester QuadBuilder
C:\watney\WatneyAstrometry.QuadBuilder.exe --help
```

Si cela affiche l'aide (liste des options), l'exécutable fonctionne correctement ✅

## Dépannage

### Erreur "Exécutable introuvable"

- Vérifiez que les `.exe` sont bien dans `C:\watney\`
- Vérifiez les noms exacts des fichiers (peuvent varier selon la release)
- Vérifiez les chemins dans `config.py`

### Erreur de Compilation C++

- Vérifiez que Visual Studio est correctement installé
- Vérifiez que tous les packages NuGet sont restaurés (Build → Restore NuGet Packages)
- Consultez les erreurs de compilation dans la fenêtre Output de Visual Studio

### Noms Alternatifs d'Exécutables

Les exécutables peuvent avoir des noms différents selon les releases :
- `GaiaStarExtractor.exe` au lieu de `WatneyAstrometry.GaiaStarExtractor.exe`
- `QuadBuilder.exe` au lieu de `WatneyAstrometry.QuadBuilder.exe`
- `SolverApp.exe` au lieu de `watney-solve.exe`

Si nécessaire, renommez-les ou mettez à jour les chemins dans `config.py`.

## Liens Utiles

- **GitHub Watney Astrometry** : https://github.com/Jusas/WatneyAstrometry
- **Releases GitHub** : https://github.com/Jusas/WatneyAstrometry/releases
- **Documentation Watney** : https://github.com/Jusas/WatneyAstrometry/wiki
