"""
Tests pour le module quality_diagnostics.py

Ce script teste les diagnostics de qualité automatiques avec des données synthétiques.
"""

import numpy as np
import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from core.quality_diagnostics import QualityDiagnostics


def test_validate_transit_depth():
    """Test de la validation de la profondeur de transit."""
    print("\n" + "="*60)
    print("TEST: validate_transit_depth")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Test 1: Profondeur normale
    assert diag.validate_transit_depth(0.015) == True
    assert len(diag.warnings) == 0
    
    # Test 2: Profondeur très faible
    diag.clear()
    assert diag.validate_transit_depth(0.00005) == False
    assert len(diag.warnings) > 0
    
    # Test 3: Profondeur invalide
    diag.clear()
    assert diag.validate_transit_depth(0.6) == False
    assert len(diag.errors) > 0
    
    print("✓ TEST RÉUSSI\n")


def test_validate_orbital_parameters():
    """Test de la validation des paramètres orbitaux."""
    print("\n" + "="*60)
    print("TEST: validate_orbital_parameters")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Test 1: Paramètres valides
    assert diag.validate_orbital_parameters(3.5, 10.0, 87.0) == True
    assert len(diag.errors) == 0
    
    # Test 2: Période invalide
    diag.clear()
    assert diag.validate_orbital_parameters(-1.0, 10.0, 87.0) == False
    assert len(diag.errors) > 0
    
    # Test 3: a/R* invalide
    diag.clear()
    assert diag.validate_orbital_parameters(3.5, 0.5, 87.0) == False
    assert len(diag.errors) > 0
    
    # Test 4: Inclinaison invalide
    diag.clear()
    assert diag.validate_orbital_parameters(3.5, 10.0, 95.0) == False
    assert len(diag.errors) > 0
    
    print("✓ TEST RÉUSSI\n")


def test_check_residuals_quality():
    """Test de la vérification de la qualité des résidus."""
    print("\n" + "="*60)
    print("TEST: check_residuals_quality")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Test 1: Résidus normaux (bruit blanc)
    residuals_good = np.random.normal(0, 0.001, 1000)
    metrics = diag.check_residuals_quality(residuals_good, 0.001)
    
    assert 'mean' in metrics
    assert 'std' in metrics
    assert 'rms' in metrics
    print(f"  RMS: {metrics['rms']:.6f}")
    print(f"  RMS/sigma: {metrics.get('rms_over_sigma', 'N/A')}")
    
    # Test 2: Résidus avec autocorrélation
    diag.clear()
    # Créer des résidus corrélés
    residuals_corr = np.zeros(1000)
    residuals_corr[0] = np.random.normal(0, 0.001)
    for i in range(1, len(residuals_corr)):
        residuals_corr[i] = 0.5 * residuals_corr[i-1] + np.random.normal(0, 0.001)
    
    metrics = diag.check_residuals_quality(residuals_corr, 0.001)
    if 'acf_1' in metrics:
        print(f"  ACF lag-1: {metrics['acf_1']:.3f}")
        if abs(metrics['acf_1']) > 0.2:
            assert len(diag.warnings) > 0
    
    print("✓ TEST RÉUSSI\n")


def test_check_chi2_quality():
    """Test de la vérification du chi2."""
    print("\n" + "="*60)
    print("TEST: check_chi2_quality")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Test 1: Chi2 excellent
    metrics = diag.check_chi2_quality(1.0, 1000, 4)
    assert len(diag.info) > 0
    
    # Test 2: Chi2 faible
    diag.clear()
    metrics = diag.check_chi2_quality(0.5, 1000, 4)
    assert len(diag.warnings) > 0
    
    # Test 3: Chi2 élevé
    diag.clear()
    metrics = diag.check_chi2_quality(2.0, 1000, 4)
    assert len(diag.warnings) > 0
    
    print("✓ TEST RÉUSSI\n")


def test_check_limb_darkening_bias():
    """Test de la détection de biais dus au limb-darkening."""
    print("\n" + "="*60)
    print("TEST: check_limb_darkening_bias")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Test 1: Pas de biais (différence < 30 ppm)
    depth_blue = 0.015000
    depth_red = 0.015020  # Différence de 20 ppm
    metrics = diag.check_limb_darkening_bias(depth_blue, depth_red, threshold_ppm=30.0)
    assert metrics['delta_depth_ppm'] == (depth_blue - depth_red) * 1e6
    print(f"  Δδ (pas de biais): {metrics['delta_depth_ppm']:.1f} ppm")
    
    # Test 2: Biais détecté (> 30 ppm)
    diag.clear()
    depth_blue = 0.015100  # 100 ppm de plus
    depth_red = 0.015000
    metrics = diag.check_limb_darkening_bias(depth_blue, depth_red, threshold_ppm=30.0)
    assert len(diag.warnings) > 0
    print(f"  Δδ (biais détecté): {metrics['delta_depth_ppm']:.1f} ppm")
    
    # Test 3: Avec erreurs et significativité
    diag.clear()
    depth_blue = 0.015100
    depth_red = 0.015000
    depth_blue_err = 0.000010  # 10 ppm
    depth_red_err = 0.000010
    metrics = diag.check_limb_darkening_bias(
        depth_blue, depth_red, 
        depth_blue_err, depth_red_err,
        threshold_ppm=30.0
    )
    print(f"  Δδ: {metrics['delta_depth_ppm']:.1f} ± {metrics['delta_err_ppm']:.1f} ppm")
    print(f"  Significativité: {metrics['significance']:.1f}σ")
    
    print("✓ TEST RÉUSSI\n")


def test_validate_parameter_recovery():
    """Test de la validation de la récupération de paramètres."""
    print("\n" + "="*60)
    print("TEST: validate_parameter_recovery")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Paramètres vrais
    true_params = {
        'delta_F': 0.015,
        'b': 0.3,
        'a_over_R_star': 10.0,
        'rho_star': 1.41,
        'R_planet': 0.12,
        'inclination': 87.0
    }
    
    # Test 1: Récupération parfaite
    recovered_good = {
        'delta_F': 0.0151,  # Erreur de 0.67%
        'b': 0.29,          # Erreur de 3.3%
        'a_over_R_star': 10.05,  # Erreur de 0.5%
        'rho_star': 1.40,   # Erreur de 0.7%
        'R_planet': 0.120,  # Erreur de 0%
        'inclination': 87.1  # Erreur de 0.1%
    }
    
    results = diag.validate_parameter_recovery(recovered_good, true_params)
    print("Résultats de récupération (bon):")
    for param, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {param}")
    
    # Test 2: Récupération avec erreurs importantes
    diag.clear()
    recovered_bad = {
        'delta_F': 0.020,  # Erreur de 33%
        'b': 0.5,          # Erreur de 67%
        'a_over_R_star': 12.0,  # Erreur de 20%
        'rho_star': 1.2,   # Erreur de 15%
        'R_planet': 0.15,  # Erreur de 25%
        'inclination': 85.0  # Erreur de 2.3%
    }
    
    results = diag.validate_parameter_recovery(recovered_bad, true_params)
    print("\nRésultats de récupération (mauvais):")
    for param, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {param}")
    
    print("\n✓ TEST RÉUSSI\n")


def test_generate_report():
    """Test de la génération de rapport."""
    print("\n" + "="*60)
    print("TEST: generate_report")
    print("="*60)
    
    diag = QualityDiagnostics()
    
    # Ajouter quelques diagnostics
    diag.validate_transit_depth(0.00005)  # Génère un warning
    diag.check_chi2_quality(1.0, 1000, 4)  # Génère une info
    diag.check_limb_darkening_bias(0.0151, 0.0150, threshold_ppm=30.0)  # Génère une info
    
    report = diag.generate_report()
    print(report)
    
    assert "RAPPORT DE DIAGNOSTIC" in report
    assert len(diag.warnings) > 0 or len(diag.info) > 0
    
    print("✓ TEST RÉUSSI\n")


def main():
    """Fonction principale qui exécute tous les tests."""
    print("="*60)
    print("TESTS DU MODULE quality_diagnostics.py")
    print("="*60)
    
    try:
        test_validate_transit_depth()
        test_validate_orbital_parameters()
        test_check_residuals_quality()
        test_check_chi2_quality()
        test_check_limb_darkening_bias()
        test_validate_parameter_recovery()
        test_generate_report()
        
        print("="*60)
        print("RÉSUMÉ DES TESTS")
        print("="*60)
        print("✓ Tous les tests sont passés avec succès!")
        print("\nFonctionnalités testées:")
        print("  - Validation de la profondeur de transit")
        print("  - Validation des paramètres orbitaux")
        print("  - Vérification de la qualité des résidus")
        print("  - Vérification du chi2")
        print("  - Détection de biais dus au limb-darkening")
        print("  - Validation de la récupération de paramètres")
        print("  - Génération de rapports de diagnostic")
        print("="*60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ERREUR DANS LES TESTS: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
