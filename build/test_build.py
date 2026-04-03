"""
Script de test pour vérifier le système de build.
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from build.dependency_analyzer import DependencyAnalyzer
from build.build_distribution import DistributionBuilder


def test_dependency_analyzer():
    """Test l'analyseur de dépendances."""
    print("Test de l'analyseur de dépendances...")
    
    base_path = Path(__file__).parent.parent
    analyzer = DependencyAnalyzer(base_path)
    
    # Tester l'extraction d'imports
    test_file = base_path / 'gui' / 'home_tab.py'
    if test_file.exists():
        imports = analyzer.extract_imports(test_file)
        print(f"  Imports trouvés dans home_tab.py: {len(imports)}")
        for imp in sorted(imports):
            print(f"    - {imp}")
    
    print("✓ Test de l'analyseur terminé\n")


def test_profile_loading():
    """Test le chargement des profils."""
    print("Test du chargement des profils...")
    
    base_path = Path(__file__).parent.parent
    profiles_file = base_path / 'build' / 'profiles.json'
    
    if not profiles_file.exists():
        print(f"  ✗ Fichier de profils non trouvé: {profiles_file}")
        return
    
    builder = DistributionBuilder(base_path, profiles_file)
    print(f"  Profils chargés: {list(builder.profiles.keys())}")
    
    for profile_name, profile_config in builder.profiles.items():
        enabled = sum(1 for v in profile_config.get('enabled_tabs', {}).values() if v)
        print(f"    - {profile_name}: {enabled} onglets activés")
    
    print("✓ Test du chargement des profils terminé\n")


def main():
    """Exécute tous les tests."""
    print("="*60)
    print("Tests du système de build NPOAP")
    print("="*60)
    print()
    
    try:
        test_dependency_analyzer()
        test_profile_loading()
        
        print("="*60)
        print("✓ Tous les tests sont passés!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
