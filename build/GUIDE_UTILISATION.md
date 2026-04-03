# Guide d'Utilisation - Système de Build NPOAP

## 📍 Où exécuter les commandes ?

### Répertoire de base : `NPOAP/`

Vous devez être dans le **répertoire racine du projet NPOAP** pour exécuter les commandes.

```
C:\Users\docke\OneDrive\Documents\NPOAP\
├── main.py
├── config.py
├── build\          ← ICI est le système de build
│   ├── build.bat
│   ├── build.ps1
│   ├── build_distribution.py
│   └── ...
├── gui\
├── core\
└── utils\
```

## ✅ Méthode 1 : Depuis le répertoire racine (RECOMMANDÉ)

### Étape 1 : Ouvrir une invite de commande

**Windows :**
- Ouvrez l'Explorateur Windows
- Naviguez vers `C:\Users\docke\OneDrive\Documents\NPOAP`
- Maintenez `Shift` + Clic droit dans le dossier
- Sélectionnez "Ouvrir la fenêtre PowerShell ici" ou "Ouvrir dans le terminal"

**Ou depuis n'importe où :**
```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
```

### Étape 2 : Vérifier que vous êtes au bon endroit

```cmd
dir main.py
```
Vous devriez voir `main.py` dans la liste.

### Étape 3 : Aller dans le répertoire build et exécuter

```cmd
cd build
build.bat exoplanets
```

**OU** directement depuis la racine :

```cmd
build\build.bat exoplanets
```

---

## ✅ Méthode 2 : Depuis PowerShell

### Ouvrir PowerShell dans le répertoire NPOAP

```powershell
cd C:\Users\docke\OneDrive\Documents\NPOAP
```

### Exécuter le script PowerShell

```powershell
cd build
.\build.ps1 exoplanets
```

**OU** directement depuis la racine :

```powershell
build\build.ps1 exoplanets
```

---

## ✅ Méthode 3 : Exécution directe avec Python

### Depuis le répertoire racine NPOAP

```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
cd build
python build_distribution.py exoplanets
```

**OU** directement depuis la racine :

```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
python build\build_distribution.py exoplanets
```

---

## 🔍 Vérifications avant d'exécuter

### 1. Vérifier que vous êtes au bon endroit

```cmd
dir
```

Vous devriez voir :
- `main.py`
- `config.py`
- `build\` (dossier)
- `gui\` (dossier)
- `core\` (dossier)
- `utils\` (dossier)

### 2. Vérifier que build.bat existe

```cmd
dir build\build.bat
```

Vous devriez voir le fichier `build.bat`.

### 3. Vérifier que Python est disponible

```cmd
python --version
```

ou

```cmd
py --version
```

Vous devriez voir la version de Python (3.6 ou supérieur).

---

## 📝 Commandes complètes (copier-coller)

### Option A : Batch depuis racine (Windows CMD)

```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
cd build
build.bat exoplanets
```

### Option B : PowerShell depuis racine

```powershell
cd C:\Users\docke\OneDrive\Documents\NPOAP
cd build
.\build.ps1 exoplanets
```

### Option C : Python direct

```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
cd build
python build_distribution.py exoplanets
```

---

## 🎯 Exemple complet pas à pas

1. **Ouvrir l'Explorateur Windows**
   - Aller à `C:\Users\docke\OneDrive\Documents\NPOAP`

2. **Ouvrir PowerShell ou CMD dans ce dossier**
   - `Shift` + Clic droit → "Ouvrir la fenêtre PowerShell ici"

3. **Vérifier votre position**
   ```cmd
   dir main.py
   ```
   Si vous voyez `main.py`, vous êtes au bon endroit !

4. **Aller dans build**
   ```cmd
   cd build
   ```

5. **Exécuter le build**
   ```cmd
   build.bat exoplanets
   ```

---

## ⚠️ Erreurs courantes

### "Le chemin d'accès spécifié est introuvable"
→ Vous n'êtes pas dans le bon répertoire. Utilisez `cd C:\Users\docke\OneDrive\Documents\NPOAP` d'abord.

### "build.bat n'est pas reconnu comme une commande"
→ Vous n'êtes pas dans le répertoire `build`. Utilisez `cd build` d'abord.

### "Python n'est pas reconnu comme une commande"
→ Python n'est pas installé ou pas dans le PATH. Utilisez `py` au lieu de `python`.

---

## 📂 Structure attendue

```
NPOAP/                          ← VOUS DEVEZ ÊTRE ICI
│
├── main.py                     ← Vérifiez que ce fichier existe
├── config.py
│
├── build/                      ← Puis allez ici
│   ├── build.bat               ← Script Windows
│   ├── build.ps1               ← Script PowerShell
│   ├── build_distribution.py   ← Script Python principal
│   ├── dependency_analyzer.py
│   ├── profiles.json
│   └── ...
│
├── gui/
├── core/
└── utils/
```

---

## 💡 Astuce : Créer un raccourci

Créez un fichier `BUILD.bat` à la racine de NPOAP :

```batch
@echo off
cd /d %~dp0
cd build
build.bat %1
```

Ensuite, vous pouvez exécuter depuis n'importe où :
```cmd
cd C:\Users\docke\OneDrive\Documents\NPOAP
BUILD.bat exoplanets
```
