"""
Analyseur de dépendances pour identifier tous les fichiers nécessaires
à partir d'un ensemble de fichiers de départ.
"""
import ast
import os
from pathlib import Path
from typing import Set, Dict, List
import re


class DependencyAnalyzer:
    """Analyse les imports dans les fichiers Python pour identifier les dépendances."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.visited_files: Set[Path] = set()
        self.local_imports: Dict[str, Set[str]] = {}
        
    def normalize_module_path(self, module_path: str) -> Path:
        """
        Convertit un chemin de module Python en chemin de fichier.
        Ex: 'gui.home_tab' -> Path('gui/home_tab.py')
        Ex: 'core.api_key_dialog' -> Path('core/api_key_dialog.py')
        """
        # Remplacer les points par des slashes
        parts = module_path.split('.')
        
        # Si le premier élément est gui, core ou utils
        if len(parts) > 0 and parts[0] in ['gui', 'core', 'utils']:
            prefix = parts[0]
            
            # Cas simple : un seul élément après le préfixe (ex: 'core.api_key_dialog')
            if len(parts) == 2:
                module_name = parts[1]
                potential_path = self.base_path / prefix / f"{module_name}.py"
                if potential_path.exists():
                    return potential_path
            
            # Cas avec sous-modules (ex: 'gui.something.submodule')
            if len(parts) > 1:
                # Essayer avec le nom du dernier élément seulement
                module_name = parts[-1]
                potential_path = self.base_path / prefix / f"{module_name}.py"
                if potential_path.exists():
                    return potential_path
                
                # Essayer avec le chemin complet (sans le premier élément)
                sub_path = '/'.join(parts[1:])
                potential_path = self.base_path / prefix / f"{sub_path}.py"
                if potential_path.exists():
                    return potential_path
                
                # Essayer comme répertoire avec __init__.py
                potential_path = self.base_path / prefix / sub_path / '__init__.py'
                if potential_path.exists():
                    return potential_path
        
        # Chercher dans tous les préfixes possibles
        for prefix in ['gui', 'core', 'utils']:
            if len(parts) > 0:
                module_name = parts[-1]
                potential_path = self.base_path / prefix / f"{module_name}.py"
                if potential_path.exists():
                    return potential_path
        
        return None
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extrait tous les imports locaux d'un fichier Python."""
        imports = set()
        
        try:
            # Lire le fichier en gérant le BOM UTF-8
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Parser l'AST
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        # Filtrer les imports locaux (gui., core., utils.)
                        if module.startswith(('gui.', 'core.', 'utils.')):
                            imports.add(module)
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith(('gui.', 'core.', 'utils.')):
                        imports.add(node.module)
                        
        except Exception as e:
            print(f"Warning: Erreur lors de l'analyse de {file_path}: {e}")
        
        return imports
    
    def find_dependencies_recursive(self, start_files: List[Path], max_depth: int = 10) -> Set[Path]:
        """
        Trouve récursivement tous les fichiers dépendants.
        
        Args:
            start_files: Liste des fichiers de départ
            max_depth: Profondeur maximale de récursion
            
        Returns:
            Ensemble de tous les fichiers nécessaires
        """
        all_files = set(start_files)
        to_process = list(start_files)
        depth = 0
        
        while to_process and depth < max_depth:
            current_level = list(to_process)
            to_process = []
            
            for file_path in current_level:
                if file_path in self.visited_files:
                    continue
                    
                self.visited_files.add(file_path)
                
                # Extraire les imports
                imports = self.extract_imports(file_path)
                
                # Trouver les fichiers correspondants
                for module_path in imports:
                    dep_file = self.normalize_module_path(module_path)
                    if dep_file and dep_file.exists() and dep_file not in all_files:
                        all_files.add(dep_file)
                        to_process.append(dep_file)
                    elif dep_file is None:
                        # Debug: imprimer les modules non trouvés
                        print(f"  [WARN] Module non trouve: {module_path}")
            
            depth += 1
        
        return all_files
    
    def analyze_profile(self, profile_config: dict, base_path: Path) -> Dict[str, Set[Path]]:
        """
        Analyse un profil de distribution pour identifier tous les fichiers nécessaires.
        
        Returns:
            Dict avec 'gui', 'core', 'utils' contenant les fichiers nécessaires
        """
        result = {
            'gui': set(),
            'core': set(),
            'utils': set(),
            'root': set()
        }
        
        # Fichiers de base toujours nécessaires
        result['root'].add(base_path / 'main.py')
        result['root'].add(base_path / 'config.py')
        
        # Analyser les onglets GUI activés
        tab_mapping = {
            'home': 'home_tab.py',
            'ephemerides': 'night_observation_tab.py',
            'photometry_exoplanets': 'photometry_exoplanets_tab.py',
            'data_reduction': 'data_reduction_tab.py',
            'asteroid_photometry': 'asteroid_photometry_tab.py',
            'transient_photometry': 'transient_photometry_tab.py',
            'data_analysis': 'data_analysis_tab.py',
            'binary_stars': 'binary_stars_tab.py',
            'easy_lucky_imaging': 'easy_lucky_imaging_tab.py',
            'cluster_analysis': 'cluster_analysis_tab.py',
            'spectroscopy': 'spectroscopy_tab.py',
            'catalogues': 'catalogues_tab.py',
        }
        
        start_files = []
        
        # Ajouter les fichiers GUI activés
        for tab_key, enabled in profile_config.get('enabled_tabs', {}).items():
            if enabled and tab_key in tab_mapping:
                gui_file = base_path / 'gui' / tab_mapping[tab_key]
                if gui_file.exists():
                    start_files.append(gui_file)
                    result['gui'].add(gui_file)
        
        # NE PAS ajouter gui/main_window.py source:
        # il importe tous les onglets (dont des modules optionnels hors profil),
        # ce qui génère des warnings inutiles pour les distributions spécialisées.
        # main_window.py est généré dynamiquement par build_distribution.py
        # à partir des tabs activés du profil.
        
        # Ajouter les modules GUI supplémentaires listés dans required_gui_modules (ou tous si "all")
        req_gui = profile_config.get('required_gui_modules', [])
        if req_gui == 'all':
            for gui_file in (base_path / 'gui').glob('*.py'):
                if gui_file.name != '__pycache__':
                    if gui_file not in result['gui']:
                        start_files.append(gui_file)
                        result['gui'].add(gui_file)
        else:
            for module_name in req_gui:
                gui_file = base_path / 'gui' / f"{module_name}.py"
                if gui_file.exists() and gui_file not in result['gui']:
                    start_files.append(gui_file)
                    result['gui'].add(gui_file)
        
        # Ajouter les modules core explicitement listés
        if profile_config.get('required_core_modules') == 'all':
            # Inclure tous les fichiers core
            for core_file in (base_path / 'core').glob('*.py'):
                if core_file.name != '__pycache__':
                    result['core'].add(core_file)
                    start_files.append(core_file)
        else:
            for module_name in profile_config.get('required_core_modules', []):
                core_file = base_path / 'core' / f"{module_name}.py"
                if core_file.exists():
                    result['core'].add(core_file)
                    start_files.append(core_file)
        
        # Ajouter les modules utils explicitement listés
        if profile_config.get('required_utils') == 'all':
            for util_file in (base_path / 'utils').glob('*.py'):
                if util_file.name != '__pycache__':
                    result['utils'].add(util_file)
                    start_files.append(util_file)
        else:
            for util_name in profile_config.get('required_utils', []):
                util_file = base_path / 'utils' / f"{util_name}.py"
                if util_file.exists():
                    result['utils'].add(util_file)
                    start_files.append(util_file)
        
        # Analyser récursivement les dépendances
        self.visited_files.clear()
        all_deps = self.find_dependencies_recursive(start_files)
        
        # Classer les dépendances trouvées (utiliser parts : portable Windows / POSIX)
        for dep_file in all_deps:
            try:
                rel_path = dep_file.relative_to(base_path)
            except ValueError:
                continue
            parts = rel_path.parts
            if not parts:
                continue
            top = parts[0]
            if top == 'gui':
                result['gui'].add(dep_file)
            elif top == 'core':
                result['core'].add(dep_file)
            elif top == 'utils':
                result['utils'].add(dep_file)
        
        # Ajouter les fichiers __init__.py nécessaires
        for category in ['gui', 'core', 'utils']:
            category_path = base_path / category
            init_file = category_path / '__init__.py'
            if init_file.exists():
                result[category].add(init_file)
        
        return result
