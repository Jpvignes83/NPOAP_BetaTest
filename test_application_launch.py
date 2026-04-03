"""
Script de test pour vérifier le lancement de l'application NPOAP
et détecter les anomalies à corriger.

Ce script teste :
- Les imports des modules principaux
- Les dépendances externes
- L'initialisation des composants GUI
- Les fonctions critiques
- Les intégrations récentes (Enoch et al., quality diagnostics, etc.)
"""

import sys
import traceback
from pathlib import Path

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def test_imports():
    """Teste les imports des modules principaux."""
    print_header("TEST 1: IMPORTS DES MODULES")
    
    modules_to_test = [
        ("tkinter", "tkinter"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("astropy", "astropy"),
        ("scipy", "scipy"),
        ("pylightcurve", "pylightcurve"),
        ("core.seager_ornelas_transit", "core.seager_ornelas_transit"),
        ("core.enoch_stellar_mass", "core.enoch_stellar_mass"),
        ("core.quality_diagnostics", "core.quality_diagnostics"),
        ("core.limb_darkening_power2", "core.limb_darkening_power2"),
        ("core.exoplanet_priors_sources", "core.exoplanet_priors_sources"),
        ("gui.photometry_exoplanets_tab", "gui.photometry_exoplanets_tab"),
        ("gui.lightcurve_fitting", "gui.lightcurve_fitting"),
    ]
    
    results = {"success": [], "failed": []}
    
    for module_name, import_path in modules_to_test:
        try:
            __import__(import_path)
            print_success(f"Import réussi: {module_name}")
            results["success"].append(module_name)
        except ImportError as e:
            print_error(f"Import échoué: {module_name} - {e}")
            results["failed"].append((module_name, str(e)))
        except Exception as e:
            print_error(f"Erreur lors de l'import de {module_name}: {e}")
            results["failed"].append((module_name, str(e)))
    
    return results

def test_core_functions():
    """Teste les fonctions principales des modules core."""
    print_header("TEST 2: FONCTIONS CORE")
    
    results = {"success": [], "failed": []}
    
    # Test seager_ornelas_transit
    try:
        from core.seager_ornelas_transit import (
            calculate_transit_depth,
            calculate_transit_durations,
            solve_transit_parameters
        )
        import numpy as np
        
        # Test simple
        flux = np.array([1.0, 1.0, 0.95, 0.95, 0.95, 1.0, 1.0])
        depth = calculate_transit_depth(flux)
        assert depth > 0, "Profondeur doit être positive"
        print_success("seager_ornelas_transit: calculate_transit_depth OK")
        results["success"].append("calculate_transit_depth")
    except Exception as e:
        print_error(f"seager_ornelas_transit: {e}")
        results["failed"].append(("seager_ornelas_transit", str(e)))
    
    # Test enoch_stellar_mass
    try:
        from core.enoch_stellar_mass import (
            calculate_stellar_mass,
            calculate_stellar_radius,
            rho_to_log_rho
        )
        
        # Test avec valeurs solaires
        rho_solar = 1.41  # g/cm³
        log_rho = rho_to_log_rho(rho_solar)
        teff = 5778  # K (Soleil)
        feh = 0.0  # [Fe/H] solaire
        
        mass = calculate_stellar_mass(teff, log_rho, feh)
        radius = calculate_stellar_radius(teff, log_rho, feh)
        
        # Vérifier que les valeurs sont raisonnables (proches de 1.0 pour le Soleil)
        assert 0.5 < mass < 2.0, f"Masse solaire attendue ~1.0, obtenue {mass}"
        assert 0.5 < radius < 2.0, f"Rayon solaire attendu ~1.0, obtenu {radius}"
        
        print_success(f"enoch_stellar_mass: M={mass:.4f} M☉, R={radius:.4f} R☉ (valeurs solaires)")
        results["success"].append("enoch_stellar_mass")
    except Exception as e:
        print_error(f"enoch_stellar_mass: {e}")
        traceback.print_exc()
        results["failed"].append(("enoch_stellar_mass", str(e)))
    
    # Test quality_diagnostics
    try:
        from core.quality_diagnostics import QualityDiagnostics
        import numpy as np
        
        diag = QualityDiagnostics()
        diag.validate_transit_depth(0.015)
        diag.check_residuals_quality(np.random.normal(0, 0.001, 100), 0.001)
        report = diag.generate_report()
        assert len(report) > 0, "Rapport doit être non vide"
        
        print_success("quality_diagnostics: QualityDiagnostics OK")
        results["success"].append("quality_diagnostics")
    except Exception as e:
        print_error(f"quality_diagnostics: {e}")
        traceback.print_exc()
        results["failed"].append(("quality_diagnostics", str(e)))
    
    # Test limb_darkening_power2
    try:
        from core.limb_darkening_power2 import (
            power2_intensity,
            transit_lightcurve_quadratic,
            transit_lightcurve_square_root,
        )
        import numpy as np
        
        mu = np.linspace(0.1, 1.0, 10)
        intensity = power2_intensity(mu, 0.5, 0.5)
        assert len(intensity) == len(mu), "Intensité doit avoir même longueur que mu"
        assert np.all(intensity >= 0) and np.all(intensity <= 1), "Intensité doit être entre 0 et 1"
        t = np.linspace(2460000.0, 2460000.05, 50)
        lcq = transit_lightcurve_quadratic(t, 3.0, 2460000.025, 0.1, 8.0, 87.0, n_annuli=400)
        lcs = transit_lightcurve_square_root(t, 3.0, 2460000.025, 0.1, 8.0, 87.0, n_annuli=400)
        assert len(lcq) == len(t) and np.all(lcq > 0) and np.all(lcq <= 1.01)
        assert len(lcs) == len(t) and np.all(lcs > 0) and np.all(lcs <= 1.01)
        
        print_success("limb_darkening_power2: power2_intensity + quad/sqrt transit OK")
        results["success"].append("limb_darkening_power2")
    except Exception as e:
        print_error(f"limb_darkening_power2: {e}")
        traceback.print_exc()
        results["failed"].append(("limb_darkening_power2", str(e)))
    
    # Test exoplanet_priors_sources
    try:
        from core.exoplanet_priors_sources import get_priors_from_all_sources
        
        # Test avec un nom de planète (peut échouer si pas de connexion, c'est OK)
        priors = get_priors_from_all_sources("WASP-12 b")
        # Ne pas échouer si None (pas de connexion)
        print_success("exoplanet_priors_sources: get_priors_from_all_sources OK (peut retourner None)")
        results["success"].append("exoplanet_priors_sources")
    except Exception as e:
        print_warning(f"exoplanet_priors_sources: {e} (peut être normal si pas de connexion)")
        results["failed"].append(("exoplanet_priors_sources", str(e)))
    
    return results

def test_gui_initialization():
    """Teste l'initialisation des composants GUI (sans afficher la fenêtre)."""
    print_header("TEST 3: INITIALISATION GUI")
    
    results = {"success": [], "failed": []}
    
    # Test photometry_exoplanets_tab
    try:
        import tkinter as tk
        from gui.photometry_exoplanets_tab import PhotometryExoplanetsTab
        
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
        tab = PhotometryExoplanetsTab(root)
        
        # Vérifier que les attributs essentiels existent
        assert hasattr(tab, 'planetary_period'), "planetary_period doit exister"
        assert hasattr(tab, 'planetary_teff'), "planetary_teff doit exister"
        assert hasattr(tab, 'planetary_feh'), "planetary_feh doit exister"
        assert hasattr(tab, 'calculate_planetary_parameters'), "calculate_planetary_parameters doit exister"
        
        root.destroy()
        
        print_success("photometry_exoplanets_tab: Initialisation OK")
        results["success"].append("photometry_exoplanets_tab")
    except Exception as e:
        print_error(f"photometry_exoplanets_tab: {e}")
        traceback.print_exc()
        results["failed"].append(("photometry_exoplanets_tab", str(e)))
    
    # Test lightcurve_fitting
    try:
        import tkinter as tk
        from gui.lightcurve_fitting import LightcurveFitting
        
        root = tk.Tk()
        root.withdraw()
        
        window = LightcurveFitting(root)
        
        # Vérifier que les attributs essentiels existent
        assert hasattr(window, 'quality_diagnostics'), "quality_diagnostics doit exister"
        assert hasattr(window, 'calculate_quality_indicators'), "calculate_quality_indicators doit exister"
        
        root.destroy()
        
        print_success("lightcurve_fitting: Initialisation OK")
        results["success"].append("lightcurve_fitting")
    except Exception as e:
        print_error(f"lightcurve_fitting: {e}")
        traceback.print_exc()
        results["failed"].append(("lightcurve_fitting", str(e)))
    
    return results

def test_integrations():
    """Teste les intégrations récentes."""
    print_header("TEST 4: INTÉGRATIONS RÉCENTES")
    
    results = {"success": [], "failed": []}
    
    # Test intégration Enoch dans photometry_exoplanets_tab
    try:
        import tkinter as tk
        from gui.photometry_exoplanets_tab import PhotometryExoplanetsTab
        from core.enoch_stellar_mass import calculate_stellar_mass_and_radius
        
        root = tk.Tk()
        root.withdraw()
        tab = PhotometryExoplanetsTab(root)
        
        # Vérifier que les imports sont présents
        import inspect
        source = inspect.getsource(tab.calculate_planetary_parameters)
        assert 'enoch_stellar_mass' in source or 'calculate_stellar_mass' in source, \
            "calculate_planetary_parameters doit utiliser enoch_stellar_mass"
        
        root.destroy()
        
        print_success("Intégration Enoch dans photometry_exoplanets_tab: OK")
        results["success"].append("integration_enoch")
    except Exception as e:
        print_error(f"Intégration Enoch: {e}")
        traceback.print_exc()
        results["failed"].append(("integration_enoch", str(e)))
    
    # Test intégration quality_diagnostics dans lightcurve_fitting
    try:
        import tkinter as tk
        from gui.lightcurve_fitting import LightcurveFitting
        
        root = tk.Tk()
        root.withdraw()
        window = LightcurveFitting(root)
        
        # Vérifier que quality_diagnostics est initialisé
        assert window.quality_diagnostics is not None, "quality_diagnostics doit être initialisé"
        
        root.destroy()
        
        print_success("Intégration quality_diagnostics dans lightcurve_fitting: OK")
        results["success"].append("integration_quality_diagnostics")
    except Exception as e:
        print_error(f"Intégration quality_diagnostics: {e}")
        traceback.print_exc()
        results["failed"].append(("integration_quality_diagnostics", str(e)))
    
    return results

def test_file_structure():
    """Vérifie que les fichiers essentiels existent."""
    print_header("TEST 5: STRUCTURE DES FICHIERS")
    
    results = {"success": [], "failed": []}
    
    files_to_check = [
        "main.py",
        "core/seager_ornelas_transit.py",
        "core/enoch_stellar_mass.py",
        "core/quality_diagnostics.py",
        "core/limb_darkening_power2.py",
        "core/exoplanet_priors_sources.py",
        "gui/photometry_exoplanets_tab.py",
        "gui/lightcurve_fitting.py",
        "config.py",
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print_success(f"Fichier existe: {file_path}")
            results["success"].append(file_path)
        else:
            print_error(f"Fichier manquant: {file_path}")
            results["failed"].append(file_path)
    
    return results

def test_dependencies():
    """Vérifie les dépendances externes."""
    print_header("TEST 6: DÉPENDANCES EXTERNES")
    
    results = {"success": [], "failed": []}
    
    dependencies = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("astropy", "astropy"),
        ("scipy", "scipy"),
        ("pylightcurve", "pylightcurve"),
    ]
    
    optional_dependencies = [
        ("astroquery", "astroquery"),
        ("statsmodels", "statsmodels"),
    ]
    
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            version = __import__(import_name).__version__ if hasattr(__import__(import_name), '__version__') else "?"
            print_success(f"{dep_name}: {version}")
            results["success"].append(dep_name)
        except ImportError:
            print_error(f"{dep_name}: NON INSTALLÉ")
            results["failed"].append(dep_name)
    
    for dep_name, import_name in optional_dependencies:
        try:
            __import__(import_name)
            version = __import__(import_name).__version__ if hasattr(__import__(import_name), '__version__') else "?"
            print_info(f"{dep_name} (optionnel): {version}")
            results["success"].append(dep_name)
        except ImportError:
            print_warning(f"{dep_name} (optionnel): NON INSTALLÉ")
    
    return results

def main():
    """Fonction principale qui lance tous les tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("  TEST DE LANCEMENT DE L'APPLICATION NPOAP")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    all_results = {}
    
    # Exécuter tous les tests
    all_results["imports"] = test_imports()
    all_results["core_functions"] = test_core_functions()
    all_results["gui"] = test_gui_initialization()
    all_results["integrations"] = test_integrations()
    all_results["file_structure"] = test_file_structure()
    all_results["dependencies"] = test_dependencies()
    
    # Résumé final
    print_header("RÉSUMÉ DES TESTS")
    
    total_success = sum(len(r["success"]) for r in all_results.values())
    total_failed = sum(len(r["failed"]) for r in all_results.values())
    
    print(f"\n{Colors.BOLD}Total des tests réussis: {Colors.GREEN}{total_success}{Colors.RESET}")
    print(f"{Colors.BOLD}Total des tests échoués: {Colors.RED}{total_failed}{Colors.RESET}\n")
    
    if total_failed > 0:
        print(f"{Colors.RED}{Colors.BOLD}DÉTAILS DES ÉCHECS:{Colors.RESET}\n")
        for test_name, result in all_results.items():
            if result["failed"]:
                print(f"{Colors.YELLOW}{test_name.upper()}:{Colors.RESET}")
                for item in result["failed"]:
                    if isinstance(item, tuple):
                        print(f"  - {item[0]}: {item[1]}")
                    else:
                        print(f"  - {item}")
                print()
    
    # Recommandations
    if total_failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Tous les tests sont passés avec succès !{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Certains tests ont échoué. Vérifiez les détails ci-dessus.{Colors.RESET}\n")
    
    return total_failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrompu par l'utilisateur.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Erreur fatale: {e}{Colors.RESET}")
        traceback.print_exc()
        sys.exit(1)
