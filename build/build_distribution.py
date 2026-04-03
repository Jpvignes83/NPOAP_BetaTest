"""
Script de build pour créer des distributions partielles de NPOAP.
Exclut physiquement les fichiers non nécessaires selon le profil choisi.
"""
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Set

# Import relatif depuis le même répertoire
try:
    from .dependency_analyzer import DependencyAnalyzer
except (ImportError, ValueError):
    # Si exécuté directement depuis build/
    import sys
    from pathlib import Path
    # Ajouter le répertoire build au path
    build_dir = Path(__file__).parent
    if str(build_dir) not in sys.path:
        sys.path.insert(0, str(build_dir))
    try:
        from dependency_analyzer import DependencyAnalyzer
    except ImportError as e:
        print(f"Erreur: Impossible d'importer dependency_analyzer: {e}")
        print(f"Vérifiez que dependency_analyzer.py existe dans {build_dir}")
        sys.exit(1)


class DistributionBuilder:
    """Construit une distribution NPOAP selon un profil donné."""
    
    def __init__(self, base_path: Path, profiles_file: Path):
        self.base_path = base_path
        self.profiles_file = profiles_file
        self.profiles = self._load_profiles()
        self.analyzer = DependencyAnalyzer(base_path)
    
    def _load_profiles(self) -> Dict:
        """Charge les profils depuis le fichier JSON."""
        with open(self.profiles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _generate_main_window(self, profile_config: dict, output_path: Path):
        """Génère un main_window.py adapté au profil."""
        enabled_tabs = profile_config.get('enabled_tabs', {})
        
        tab_mapping = {
            'home': ('HomeTab', 'gui.home_tab', 'HomeTab', False),
            'ephemerides': ('NightObservationTab', 'gui.night_observation_tab', 'NightObservationTab', True),
            'photometry_exoplanets': ('PhotometryExoplanetsTab', 'gui.photometry_exoplanets_tab', 'PhotometryExoplanetsTab', False),
            'data_reduction': ('CCDProcGUI', 'gui.data_reduction_tab', 'CCDProcGUI', False),
            'asteroid_photometry': ('AsteroidPhotometryTab', 'gui.asteroid_photometry_tab', 'AsteroidPhotometryTab', False),
            'transient_photometry': ('TransientPhotometryTab', 'gui.transient_photometry_tab', 'TransientPhotometryTab', False),
            'data_analysis': ('DataAnalysisTab', 'gui.data_analysis_tab', 'DataAnalysisTab', False),
            'binary_stars': ('BinaryStarsTab', 'gui.binary_stars_tab', 'BinaryStarsTab', False),
            'easy_lucky_imaging': ('EasyLuckyImagingTab', 'gui.easy_lucky_imaging_tab', 'EasyLuckyImagingTab', True),
            'spectroscopy': ('SpectroscopyTab', 'gui.spectroscopy_tab', 'SpectroscopyTab', False),
            'catalogues': ('CataloguesTab', 'gui.catalogues_tab', 'CataloguesTab', True),
        }
        
        tab_labels = {
            'home': '🏠 Accueil',
            'ephemerides': '🌙 Observation de la Nuit',
            'photometry_exoplanets': '🔭 Photométrie Exoplanètes',
            'data_reduction': '🛠️ Réduction de Données',
            'asteroid_photometry': '🛰️ Photométrie Astéroïdes',
            'transient_photometry': '💥 Photométrie Transitoires',
            'data_analysis': '📈 Analyse des Données',
            'binary_stars': '⭐ Étoiles Binaires',
            'easy_lucky_imaging': '✨ Easy Lucky Imaging',
            'spectroscopy': '🔬 Spectroscopie',
            'catalogues': '📚 Catalogues',
        }
        
        # Générer les imports
        imports = []
        imports.append("import tkinter as tk")
        imports.append("from tkinter import ttk")
        imports.append("")
        
        # Imports conditionnels
        for tab_key, (class_name, module_path, import_name, is_optional) in tab_mapping.items():
            if enabled_tabs.get(tab_key, False):
                if is_optional:
                    # Imports avec try/except pour les modules optionnels
                    imports.append(f"try:")
                    imports.append(f"    from {module_path} import {import_name}")
                    imports.append(f"    {class_name.upper()}_AVAILABLE = True")
                    imports.append(f"except ImportError as e:")
                    imports.append(f"    {class_name.upper()}_AVAILABLE = False")
                    imports.append(f"    {import_name} = None")
                    imports.append(f"    print(f'Warning: {import_name} non disponible: {{e}}')")
                else:
                    imports.append(f"from {module_path} import {import_name}")
        
        # Générer le code de la classe
        class_code = [
            "",
            "",
            "class MainWindow:",
            "    def __init__(self, root):",
            "        self.root = root",
            "        self.root.title(\"NPOAP\")",
            "        self.root.geometry(\"1600x1000\")",
            "",
            "        self.notebook = ttk.Notebook(self.root)",
            "        self.notebook.pack(fill=tk.BOTH, expand=True)",
            "",
            "        # ---------------------------",
            "        # Initialisation des onglets",
            "        # ---------------------------",
            ""
        ]
        
        # Initialisation des onglets
        for tab_key, (class_name, _, import_name, is_optional) in tab_mapping.items():
            if enabled_tabs.get(tab_key, False):
                if is_optional:
                    class_code.append(f"        if {class_name.upper()}_AVAILABLE:")
                    class_code.append(f"            self.{tab_key}_tab = {import_name}(self.notebook)")
                    class_code.append(f"        else:")
                    class_code.append(f"            self.{tab_key}_tab = None")
                elif tab_key == 'data_reduction':
                    class_code.append(f"        self.data_reduction_tab = {import_name}(self.notebook)")
                elif tab_key == 'asteroid_photometry':
                    class_code.append(f"        self.asteroid_photometry_tab = {import_name}(self.notebook)")
                else:
                    if tab_key == 'photometry_exoplanets':
                        class_code.append(f"        self.{tab_key}_tab = {import_name}(self.notebook, base_dir=None)")
                    elif tab_key == 'easy_lucky_imaging':
                        class_code.append(f"        self.{tab_key}_tab = {import_name}(self.notebook)")
                    else:
                        class_code.append(f"        self.{tab_key}_tab = {import_name}(self.notebook)")
        
        class_code.append("")
        class_code.append("        # ---------------------------")
        class_code.append("        # Ajout dans le Notebook")
        class_code.append("        # ---------------------------")
        class_code.append("")
        
        # Ajout des onglets au notebook
        for tab_key, (class_name, _, _, is_optional) in tab_mapping.items():
            if enabled_tabs.get(tab_key, False):
                label = tab_labels[tab_key]
                if is_optional:
                    class_code.append(f"        if self.{tab_key}_tab is not None:")
                    class_code.append(f"            self.notebook.add(self.{tab_key}_tab, text=\"{label}\")")
                elif tab_key == 'data_reduction':
                    class_code.append(f"        self.notebook.add(self.data_reduction_tab.frame, text=\"{label}\")")
                elif tab_key == 'asteroid_photometry':
                    class_code.append(f"        self.notebook.add(self.asteroid_photometry_tab.frame, text=\"{label}\")")
                elif tab_key == 'data_analysis':
                    class_code.append(f"        self.notebook.add(self.data_analysis_tab.main_frame, text=\"{label}\")")
                else:
                    class_code.append(f"        self.notebook.add(self.{tab_key}_tab, text=\"{label}\")")
        
        class_code.extend([
            "",
            "        # Gestion fermeture propre",
            "        self.root.protocol(\"WM_DELETE_WINDOW\", self.on_quit)",
            "",
            "    def on_quit(self):",
            "        self.root.destroy()",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    root = tk.Tk()",
            "    app = MainWindow(root)",
            "    root.mainloop()"
        ])
        
        # Écrire le fichier
        output_file = output_path / 'gui' / 'main_window.py'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(imports + class_code))
        
        print(f"[OK] Genere {output_file}")
    
    def _generate_tabs_config(self, profile_config: dict, output_path: Path):
        """Génère le fichier de configuration des onglets."""
        config_dir = output_path / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / 'tabs_config.py'
        
        content = [
            "# Configuration des onglets activés",
            "# Ce fichier est généré automatiquement lors du build",
            "",
            "ENABLED_TABS = {"
        ]
        
        for tab_key, enabled in profile_config.get('enabled_tabs', {}).items():
            content.append(f"    '{tab_key}': {enabled},")
        
        content.append("}")
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"[OK] Genere {config_file}")
    
    def _generate_utils_init(self, utils_files: Set[Path], output_path: Path):
        """Génère un utils/__init__.py adapté qui n'importe que les modules disponibles."""
        utils_dir = output_path / 'utils'
        init_file = utils_dir / '__init__.py'
        
        # Mapping des noms de modules vers leurs exports
        module_exports = {
            'file_handler': [('FileHandler', 'FileHandler')],
            'logging_handler': [('setup_logging', 'setup_logging'), ('TextHandler', 'TextHandler')],
            'progress_manager': [('ProgressManager', 'ProgressManager')],
        }
        
        # Déterminer quels modules sont disponibles
        available_modules = {}
        for util_file in utils_files:
            module_name = util_file.stem  # Nom sans extension
            if module_name != '__init__' and module_name in module_exports:
                available_modules[module_name] = module_exports[module_name]
        
        # Générer le contenu
        imports = ['# utils/__init__.py', '# Ce fichier est généré automatiquement lors du build', '']
        all_exports = []
        
        # Imports conditionnels
        if 'file_handler' in available_modules:
            imports.append('from .file_handler import FileHandler')
            all_exports.append('"FileHandler"')
        
        if 'logging_handler' in available_modules:
            imports.append('from .logging_handler import setup_logging, TextHandler')
            all_exports.extend(['"setup_logging"', '"TextHandler"'])
        
        if 'progress_manager' in available_modules:
            imports.append('from .progress_manager import ProgressManager')
            all_exports.append('"ProgressManager"')
        
        # __all__
        imports.append('')
        imports.append('__all__ = [')
        if all_exports:
            for export in all_exports[:-1]:
                imports.append(f'    {export},')
            imports.append(f'    {all_exports[-1]},')
        imports.append(']')
        
        # Écrire le fichier
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(imports))
        
        print(f"  [OK] Genere {init_file}")
    
    def _generate_launch_script(self, output_path: Path, profile_name: str):
        """Génère un script lancement.bat pour lancer l'application."""
        script_path = output_path / 'lancement.bat'
        
        content = [
            "@echo off",
            "chcp 65001 >nul",
            "REM ============================================================",
            f"REM Script de lancement NPOAP - {profile_name}",
            "REM Obligatoire : environnement conda « astroenv » (Python 3.11+).",
            "REM Installation : INSTALLER_NPOAP_ASTROENV_WINDOWS.bat",
            "REM ============================================================",
            "",
            "title NPOAP - Lancement",
            "",
            "cd /d \"%~dp0\"",
            "",
            "set \"CONDA_ROOT=\"",
            "where conda >nul 2>&1",
            "if %ERRORLEVEL% EQU 0 (",
            "    for /f \"delims=\" %%i in ('conda info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT if exist \"%USERPROFILE%\\miniconda3\\Scripts\\conda.exe\" (",
            "    for /f \"delims=\" %%i in ('\"%USERPROFILE%\\miniconda3\\Scripts\\conda.exe\" info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT if exist \"%USERPROFILE%\\anaconda3\\Scripts\\conda.exe\" (",
            "    for /f \"delims=\" %%i in ('\"%USERPROFILE%\\anaconda3\\Scripts\\conda.exe\" info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT (",
            "    echo ERREUR: conda introuvable. Installez Miniconda puis creez astroenv :",
            "    echo   INSTALLER_NPOAP_ASTROENV_WINDOWS.bat",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "if not exist \"%CONDA_ROOT%\\Scripts\\activate.bat\" (",
            "    echo ERREUR: activate.bat introuvable.",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "call \"%CONDA_ROOT%\\Scripts\\activate.bat\" astroenv",
            "if errorlevel 1 (",
            "    echo ERREUR: impossible d'activer astroenv.",
            "    echo Executez INSTALLER_NPOAP_ASTROENV_WINDOWS.bat dans ce dossier.",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "echo Lancement de NPOAP...",
            "echo.",
            "",
            "if not exist \"main.py\" (",
            "    echo Erreur: main.py non trouve.",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "if not exist \"logs\" mkdir logs",
            "",
            "python main.py",
            "",
            "if errorlevel 1 (",
            "    echo.",
            "    echo Erreur lors du lancement ^(code %ERRORLEVEL%^).",
            "    echo Dependances : pip install -r requirements.txt dans astroenv",
            "    pause",
            ")",
            ""
        ]
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"  [OK] Genere lancement.bat")
    
    def _generate_astroenv_launch_script(self, output_path: Path, profile_name: str):
        """Génère lancement_astroenv.bat pour les distributions nécessitant PHOEBE."""
        script_path = output_path / 'lancement_astroenv.bat'
        content = [
            "@echo off",
            "chcp 65001 >nul",
            "REM ============================================================",
            f"REM Lancement NPOAP - {profile_name} (avec environnement astroenv)",
            "REM PHOEBE et autres dépendances sont dans conda astroenv",
            "REM Double-cliquez sur ce fichier pour lancer avec le bon Python",
            "REM ============================================================",
            "",
            "title NPOAP - Lancement (astroenv)",
            "",
            "cd /d \"%~dp0\"",
            "",
            "echo Activation de l'environnement astroenv...",
            "set \"CONDA_ROOT=\"",
            "where conda >nul 2>&1",
            "if %ERRORLEVEL% EQU 0 (",
            "    for /f \"delims=\" %%i in ('conda info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT if exist \"%USERPROFILE%\\miniconda3\\Scripts\\conda.exe\" (",
            "    for /f \"delims=\" %%i in ('\"%USERPROFILE%\\miniconda3\\Scripts\\conda.exe\" info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT if exist \"%USERPROFILE%\\anaconda3\\Scripts\\conda.exe\" (",
            "    for /f \"delims=\" %%i in ('\"%USERPROFILE%\\anaconda3\\Scripts\\conda.exe\" info --base 2^>nul') do set \"CONDA_ROOT=%%i\"",
            ")",
            "if not defined CONDA_ROOT (",
            "    echo ERREUR: conda introuvable.",
            "    pause",
            "    exit /b 1",
            ")",
            "call \"%CONDA_ROOT%\\Scripts\\activate.bat\" astroenv",
            "if errorlevel 1 (",
            "    echo.",
            "    echo ERREUR: Impossible d'activer astroenv.",
            "    echo Executez INSTALLER_NPOAP_ASTROENV_WINDOWS.bat dans ce dossier.",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "echo Lancement de NPOAP...",
            "echo.",
            "",
            "if not exist \"main.py\" (",
            "    echo Erreur: main.py non trouve.",
            "    pause",
            "    exit /b 1",
            ")",
            "",
            "if not exist \"logs\" (mkdir logs)",
            "",
            "python main.py",
            "",
            "if errorlevel 1 (",
            "    echo.",
            "    echo Erreur lors du lancement.",
            "    pause",
            ")",
            ""
        ]
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"  [OK] Genere lancement_astroenv.bat (pour PHOEBE)")
    
    def _generate_requirements_txt(self, profile_name: str, output_dir: Path) -> None:
        """Génère un requirements.txt limité aux dépendances du profil (build/requirements_profiles.json)."""
        req_profiles_path = self.base_path / 'build' / 'requirements_profiles.json'
        out_file = output_dir / 'requirements.txt'
        if req_profiles_path.exists():
            try:
                for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
                    try:
                        with open(req_profiles_path, 'r', encoding=enc) as f:
                            req_profiles = json.load(f)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise OSError("requirements_profiles.json: encodage non reconnu")
                lines = req_profiles.get(profile_name)
                if isinstance(lines, list):
                    content = '\n'.join(line for line in lines if not line.strip().startswith('_'))
                    with open(out_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  [OK] Genere requirements.txt ({len(lines)} lignes, profil {profile_name})")
                    return
            except (json.JSONDecodeError, OSError) as e:
                print(f"  [WARN] requirements_profiles.json invalide ou illisible: {e}, copie du requirements global")
        # Fallback: copier le requirements global
        requirements_file = self.base_path / 'requirements.txt'
        if requirements_file.exists():
            shutil.copy2(requirements_file, out_file)
            print(f"  [OK] Copie requirements.txt (global)")

    def _write_distribution_gitignore(self, output_dir: Path) -> None:
        """Pour publication Git : ignorer config locale, données et caches."""
        content = """# Local / secrets
config.json
.astrometry_api_key
.env
.venv/
venv/

# Données utilisateur et sorties
output/
*.fits
*.fit
*.log
logs/*.log
!logs/.gitkeep

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db
"""
        p = output_dir / ".gitignore"
        p.write_text(content, encoding="utf-8")
        print(f"  [OK] Ecrit {p.name} (pret pour depot Git de la distribution)")

    def _copy_full_installation_toolkit(self, output_dir: Path) -> None:
        """
        Profil full uniquement : copie a la racine de la distribution les scripts
        d'installation du depot (tests et options WSL, MSVC, Prospector, etc.).
        """
        root_names = [
            'config.example.json',
            'installation.bat',
            'INSTALLER_PROSPECTOR_COMPLET_WINDOWS.bat',
            'INSTALLER_PROSPECTOR_COMPLET_WINDOWS.ps1',
            'install_kbmod_wsl.bat',
            'install_astrometry_wsl.bat',
            'install_ubuntu_wsl.bat',
            'install_wsl.bat',
            'install_cmake.bat',
            'install_msvc_build_tools.bat',
            'installer_ccdproc.bat',
            'normalize_requirements_utf8.ps1',
            'installation_miniconda_download.ps1',
            'LISTE_INSTALL_OPTIONNELS.txt',
            'README_INSTALLATION.md',
            'test_installation.py',
        ]
        print("\nCopie du kit d'installation (profil full)...")
        for name in root_names:
            src = self.base_path / name
            dst = output_dir / name
            if src.is_file():
                shutil.copy2(src, dst)
                print(f"  [OK] Copie {name}")
            else:
                print(f"  [WARN] Fichier d'installation absent: {name}")
    
    def build(self, profile_name: str, output_dir: Path = None) -> Path:
        """
        Construit une distribution selon le profil spécifié.
        
        Args:
            profile_name: Nom du profil (exoplanets, asteroids, full, ...)
            output_dir: Répertoire de sortie (par défaut: build/distributions/{profile_name})
        
        Returns:
            Chemin vers le répertoire de build
        """
        if profile_name not in self.profiles:
            raise ValueError(f"Profil '{profile_name}' non trouvé. Profils disponibles: {list(self.profiles.keys())}")
        
        profile_config = self.profiles[profile_name]
        print(f"\n{'='*60}")
        print(f"Construction de la distribution: {profile_config['name']}")
        print(f"Description: {profile_config['description']}")
        print(f"{'='*60}\n")
        
        # Déterminer le répertoire de sortie
        if output_dir is None:
            output_dir = self.base_path / 'build' / 'distributions' / profile_name
        else:
            output_dir = Path(output_dir)
        
        # Nettoyer le répertoire de sortie
        if output_dir.exists():
            try:
                # Fermer tous les handles de fichiers avant suppression
                import gc
                import time
                gc.collect()
                # Essayer plusieurs fois avec des délais
                for attempt in range(3):
                    try:
                        shutil.rmtree(output_dir)
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(1)
                        else:
                            # Dernière tentative: renommer le répertoire au lieu de le supprimer
                            backup_dir = output_dir.parent / f"{output_dir.name}_old_{int(time.time())}"
                            try:
                                output_dir.rename(backup_dir)
                                print(f"  [INFO] Ancien repertoire renomme en: {backup_dir.name}")
                            except Exception:
                                print(f"\n[ERREUR] Impossible de supprimer ou renommer le repertoire: {output_dir}")
                                print(f"Le repertoire contient des fichiers verrouilles.")
                                print(f"Veuillez fermer tous les fichiers ouverts et reessayer.")
                                raise
            except PermissionError as e:
                print(f"\n[ERREUR] Erreur lors de la suppression du repertoire existant: {e}")
                print(f"Le repertoire {output_dir} est peut-etre ouvert dans l'Explorateur Windows.")
                print(f"Veuillez fermer l'Explorateur et reessayer.")
                raise
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyser les dépendances
        print("Analyse des dépendances...")
        dependencies = self.analyzer.analyze_profile(profile_config, self.base_path)
        
        print(f"\nFichiers identifiés:")
        print(f"  - GUI: {len(dependencies['gui'])} fichiers")
        print(f"  - Core: {len(dependencies['core'])} fichiers")
        print(f"  - Utils: {len(dependencies['utils'])} fichiers")
        print(f"  - Root: {len(dependencies['root'])} fichiers")
        
        # Copier les fichiers
        print("\nCopie des fichiers...")
        
        def safe_copy(src, dst, relative_path=""):
            """Copie un fichier en gérant les erreurs de permission."""
            try:
                if not dst.exists():
                    shutil.copy2(src, dst)
                    print(f"  [OK] {relative_path or dst.name}")
                else:
                    # Si le fichier existe, vérifier s'il faut le remplacer
                    import filecmp
                    if not filecmp.cmp(src, dst, shallow=False):
                        # Les fichiers sont différents, remplacer
                        dst.unlink()
                        shutil.copy2(src, dst)
                        print(f"  [OK] {relative_path or dst.name} (remplace)")
                    else:
                        print(f"  [OK] {relative_path or dst.name} (deja a jour)")
            except PermissionError as e:
                print(f"  [ERREUR] Erreur de permission pour {relative_path or dst.name}: {e}")
                print(f"     Le fichier est peut-etre ouvert. Fermez-le et reessayez.")
                raise
            except Exception as e:
                print(f"  [ERREUR] Erreur lors de la copie de {relative_path or dst.name}: {e}")
                raise
        
        # Fichiers racine
        for file_path in dependencies['root']:
            if file_path.exists():
                safe_copy(file_path, output_dir / file_path.name)
        
        # Fichiers GUI
        gui_dir = output_dir / 'gui'
        gui_dir.mkdir(exist_ok=True)
        for file_path in dependencies['gui']:
            if file_path.exists():
                safe_copy(file_path, gui_dir / file_path.name, f"gui/{file_path.name}")
        
        # Fichiers Core
        core_dir = output_dir / 'core'
        core_dir.mkdir(exist_ok=True)
        for file_path in dependencies['core']:
            if file_path.exists():
                safe_copy(file_path, core_dir / file_path.name, f"core/{file_path.name}")
        
        # Fichiers Utils
        utils_dir = output_dir / 'utils'
        utils_dir.mkdir(exist_ok=True)
        for file_path in dependencies['utils']:
            if file_path.exists() and file_path.name != '__init__.py':
                # Ne pas copier __init__.py maintenant, il sera généré plus tard
                safe_copy(file_path, utils_dir / file_path.name, f"utils/{file_path.name}")
        
        # Générer main_window.py adapté
        print("\nGénération de main_window.py...")
        self._generate_main_window(profile_config, output_dir)
        
        # Générer tabs_config.py
        print("\nGénération de tabs_config.py...")
        self._generate_tabs_config(profile_config, output_dir)
        
        # Générer utils/__init__.py adapté
        print("\nGénération de utils/__init__.py...")
        self._generate_utils_init(dependencies['utils'], output_dir)
        
        # Scripts CLI utilisés par l'onglet Catalogues (TESS → LcTools, etc.)
        if profile_config.get('enabled_tabs', {}).get('catalogues'):
            scripts_src = self.base_path / 'scripts'
            if scripts_src.is_dir():
                scripts_dst = output_dir / 'scripts'
                shutil.copytree(scripts_src, scripts_dst, dirs_exist_ok=True)
                print(f"  [OK] Copie scripts/ (profil avec onglet Catalogues)")

        # HOPS embarqué : fournir l'archive locale pour installation hors-ligne.
        hops_zip_src = self.base_path / 'external_apps' / 'hops' / 'HOPS-modified.zip'
        if hops_zip_src.is_file():
            hops_zip_dst_dir = output_dir / 'external_apps' / 'hops'
            hops_zip_dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(hops_zip_src, hops_zip_dst_dir / 'HOPS-modified.zip')
            print("  [OK] Copie external_apps/hops/HOPS-modified.zip")
        else:
            print("  [WARN] HOPS-modified.zip absent (installation HOPS dépendra d'un ZIP externe)")

        # Passbands personnalisés (Gaia) fournis avec la distribution.
        filters_src = self.base_path / 'resources' / 'filters'
        if filters_src.is_dir():
            filters_dst = output_dir / 'resources' / 'filters'
            shutil.copytree(filters_src, filters_dst, dirs_exist_ok=True)
            print("  [OK] Copie resources/filters/")
        else:
            print("  [WARN] Dossier resources/filters absent")
        
        # Créer le répertoire logs pour les logs d'erreurs
        logs_dir = output_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        # Créer un fichier .gitkeep pour que le répertoire soit créé même vide
        (logs_dir / '.gitkeep').touch()
        print(f"  [OK] Cree logs/")
        
        # Créer le script lancement.bat
        print("\nGeneration de lancement.bat...")
        self._generate_launch_script(output_dir, profile_name)
        
        # Pour binary_stars et full : ajouter lancement_astroenv.bat (PHOEBE)
        if profile_name in ('binary_stars', 'full'):
            self._generate_astroenv_launch_script(output_dir, profile_name)
        
        # Générer requirements.txt limité au profil (build/requirements_profiles.json)
        self._generate_requirements_txt(profile_name, output_dir)

        # Installateur Windows unifié (conda astroenv + requirements.txt du profil)
        astro_inst = self.base_path / 'build' / 'installer_distribution_astroenv_windows.bat'
        if astro_inst.is_file():
            shutil.copy2(astro_inst, output_dir / 'INSTALLER_NPOAP_ASTROENV_WINDOWS.bat')
            print(f"  [OK] Copie INSTALLER_NPOAP_ASTROENV_WINDOWS.bat")
            # Rétro-compatibilité pour les habitudes « full »
            full_wrap = self.base_path / 'build' / 'installer_distribution_full_windows.bat'
            if full_wrap.is_file():
                shutil.copy2(full_wrap, output_dir / 'INSTALLER_DISTRIBUTION_FULL_WINDOWS.bat')
                print(f"  [OK] Copie INSTALLER_DISTRIBUTION_FULL_WINDOWS.bat (delegue astroenv)")
        else:
            print(f"  [WARN] installer_distribution_astroenv_windows.bat absent")
        
        # Copier les fichiers de documentation essentiels
        docs_dir = output_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        essential_docs = ['MANUEL_INSTALLATION.md', 'MANUEL_UTILISATEUR.md', 'ACKNOWLEDGEMENTS.md']
        if profile_name == 'full':
            essential_docs.extend([
                'PROTOCOLE_INSTALLATION_PROSPECTOR_WINDOWS.md',
                'INSTALL_KBMOD_WSL.md',
            ])
        for doc in essential_docs:
            doc_file = self.base_path / 'docs' / doc
            if doc_file.exists():
                shutil.copy2(doc_file, docs_dir / doc)
            elif profile_name == 'full':
                print(f"  [WARN] Doc demandee pour full absente: docs/{doc}")

        if profile_name == 'full':
            self._copy_full_installation_toolkit(output_dir)
            self._write_distribution_gitignore(output_dir)

        print(f"\n{'='*60}")
        print(f"[OK] Distribution '{profile_name}' construite avec succes!")
        print(f"  Repertoire: {output_dir}")
        print(f"{'='*60}\n")
        
        return output_dir
    
    def create_archive(self, build_dir: Path, archive_format: str = 'zip') -> Path:
        """
        Crée une archive à partir du répertoire de build.
        
        Args:
            build_dir: Répertoire de build
            archive_format: Format d'archive ('zip', 'tar', 'tar.gz')
        
        Returns:
            Chemin vers l'archive créée
        """
        archive_name = build_dir.name
        archive_path = build_dir.parent / f"{archive_name}.{archive_format}"
        
        print(f"Création de l'archive {archive_path}...")
        
        if archive_format == 'zip':
            shutil.make_archive(str(archive_path.with_suffix('')), 'zip', build_dir.parent, build_dir.name)
        elif archive_format in ['tar', 'tar.gz']:
            shutil.make_archive(str(archive_path.with_suffix('')), archive_format.replace('tar.', ''), 
                             build_dir.parent, build_dir.name)
        else:
            raise ValueError(f"Format d'archive non supporté: {archive_format}")
        
        print(f"[OK] Archive creee: {archive_path}")
        return archive_path


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage: python build_distribution.py <profile_name> [output_dir]")
        print("\nProfils disponibles:")
        print("  - exoplanets: Distribution spécialisée exoplanètes")
        print("  - asteroids: Distribution spécialisée astéroïdes")
        print("  - binary_stars: Distribution étoiles doubles (Binaires + ELI)")
        print("  - spectroscopy: Distribution spectroscopie")
        print("  - catalogues: Distribution extraction de catalogues (Vizier, Gaia, MAST, TESS…)")
        print("  - full: Distribution complète")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Chemins
    base_path = Path(__file__).parent.parent
    profiles_file = base_path / 'build' / 'profiles.json'
    
    if not profiles_file.exists():
        print(f"Erreur: Fichier de profils non trouvé: {profiles_file}")
        sys.exit(1)
    
    # Construire la distribution
    builder = DistributionBuilder(base_path, profiles_file)
    build_dir = builder.build(profile_name, output_dir)
    
    # Créer l'archive
    archive_path = builder.create_archive(build_dir, 'zip')
    
    print(f"\n{'='*60}")
    print(f"[OK] Distribution terminee!")
    print(f"  Repertoire: {build_dir}")
    print(f"  Archive: {archive_path}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
