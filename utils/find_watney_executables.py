#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script utilitaire pour trouver les exécutables Watney dans le code source.

Ce script cherche les fichiers .exe, .dll ou les projets .csproj dans une arborescence
pour aider à localiser les exécutables Watney Astrometry.
"""

import os
from pathlib import Path
import sys


def find_executables(root_dir: Path):
    """Cherche les exécutables Watney dans une arborescence."""
    root_dir = Path(root_dir)
    
    print("=" * 80)
    print("RECHERCHE DES EXÉCUTABLES WATNEY")
    print("=" * 80)
    print(f"Répertoire de recherche : {root_dir}")
    print()
    
    # Chercher les fichiers .exe
    print("🔍 Recherche des fichiers .exe...")
    exe_files = list(root_dir.rglob("*.exe"))
    watney_exes = [f for f in exe_files if any(keyword in f.name.lower() for keyword in 
                                                ['watney', 'gaia', 'star', 'extractor', 'quad', 'builder', 'solver'])]
    
    if watney_exes:
        print(f"✅ {len(watney_exes)} exécutable(s) trouvé(s) :")
        for exe in sorted(watney_exes):
            print(f"   - {exe}")
    else:
        print("   ❌ Aucun fichier .exe trouvé")
    print()
    
    # Chercher les projets .csproj (C#)
    print("🔍 Recherche des projets C# (.csproj)...")
    csproj_files = list(root_dir.rglob("*.csproj"))
    watney_projects = [f for f in csproj_files if any(keyword in f.name.lower() for keyword in 
                                                      ['watney', 'gaia', 'star', 'extractor', 'quad', 'builder', 'solver'])]
    
    if watney_projects:
        print(f"✅ {len(watney_projects)} projet(s) C# trouvé(s) :")
        for proj in sorted(watney_projects):
            # Essayer de trouver le bin/Release correspondant
            bin_dir = proj.parent / "bin" / "Release"
            if bin_dir.exists():
                print(f"   - {proj.name}")
                print(f"     Chemin projet : {proj.parent}")
                print(f"     Dossier bin/Release : {bin_dir}")
                
                # Chercher les exécutables dans bin/Release
                for net_version in ["net6.0", "net7.0", "net8.0", "net9.0"]:
                    release_dir = bin_dir / net_version
                    if release_dir.exists():
                        exes_in_release = list(release_dir.glob("*.exe"))
                        if exes_in_release:
                            print(f"       → Exécutables trouvés dans {net_version}:")
                            for exe in exes_in_release:
                                print(f"         - {exe.name}")
            else:
                print(f"   - {proj.name} (dans {proj.parent}) - Pas encore compilé")
    else:
        print("   ❌ Aucun projet C# trouvé")
    print()
    
    # Chercher les fichiers .sln (Solution Visual Studio)
    print("🔍 Recherche des solutions Visual Studio (.sln)...")
    sln_files = list(root_dir.rglob("*.sln"))
    if sln_files:
        print(f"✅ {len(sln_files)} solution(s) trouvée(s) :")
        for sln in sorted(sln_files):
            print(f"   - {sln}")
    else:
        print("   ❌ Aucun fichier .sln trouvé")
    print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    if watney_exes:
        print("✅ Exécutables trouvés - Vous pouvez les utiliser directement")
        print("\n   Pour configurer dans config.py :")
        for exe in watney_exes:
            print(f"   WATNEY_GAIA_EXTRACTOR_EXE = Path(r\"{exe}\")")
            print(f"   # ou")
            print(f"   WATNEY_QUAD_BUILDER_EXE = Path(r\"{exe}\")")
    elif watney_projects:
        print("📝 Projets C# trouvés - Vous devez les compiler")
        print("\n   Pour compiler avec .NET CLI :")
        for proj in watney_projects[:3]:  # Afficher les 3 premiers
            print(f"   cd {proj.parent}")
            print(f"   dotnet build -c Release")
        print("\n   Ou ouvrez la solution .sln dans Visual Studio")
    else:
        print("❌ Aucun exécutable ou projet Watney trouvé")
        print("\n   Vérifiez que vous êtes dans le bon répertoire")
        print("   Téléchargez le code source depuis :")
        print("   https://github.com/Jusas/WatneyAstrometry")
    
    print("=" * 80)


def main():
    """Point d'entrée principal."""
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        # Demander interactivement
        print("Où se trouve le code source Watney Astrometry ?")
        print("(Entrez le chemin ou appuyez sur Entrée pour chercher dans le répertoire courant)")
        user_input = input("Chemin : ").strip()
        
        if user_input:
            root_dir = Path(user_input)
        else:
            root_dir = Path.cwd()
    
    if not root_dir.exists():
        print(f"❌ Erreur : Le répertoire '{root_dir}' n'existe pas")
        sys.exit(1)
    
    find_executables(root_dir)


if __name__ == "__main__":
    main()
