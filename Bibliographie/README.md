# Bibliographie NPOAP

Ce répertoire contient les articles scientifiques utilisés pour l'amélioration des modules NPOAP.

## Étoiles doubles

- `Zasche_Wolf_2007_Combining_astrometry_LITE.pdf`  
  Zasche & Wolf (2007) - Astron. Nachr. 328, 928-937.  
  *Combining astrometry with the light-time effect: The case of VW Cep, ζ Phe and HT Vir.*  
  Méthode d'ajustement combiné astrométrie + LITE pour l'inférence orbitale du troisième corps.

## Transitoires

Voir le sous-répertoire **`transitoires/`** et son `README.md`.

- **`Alard_Lupton_1998_Optimal_Image_Subtraction.pdf`** (dans `transitoires/`)  
  Alard & Lupton (1998) – ApJ 503, 325.  
  *A Method for Optimal Image Subtraction.*  
  Référence pour la soustraction d’images (noyau optimal) utilisée dans NPOAP (`core/alard_lupton.py`).

## Astéroïdes

- `Whidden_2019_AJ_157_119.pdf`  
  Whidden et al. (2019) - The Astronomical Journal, 157, 119.  
  *Fast Algorithms for Slow Moving Asteroids: Constraints on the Distribution of Kuiper Belt Objects.*  
  Voir la fiche: `Bibliographie/Asteroides/Whidden_2019_AJ_157_119.md`

- `Smotherman_2021_Sifting_Through_the_Static.pdf`  
  Smotherman et al. (2021) - arXiv:2109.03296.  
  *Sifting Through the Static: Moving Object Detection in Difference Images.*  
  Voir la fiche: `Bibliographie/Asteroides/Smotherman_2021_arXiv_2109_03296.md`

## Exoplanètes / Transits

Articles à placer dans le sous-dossier Exoplanètes :

1. `High-precision Stellar Limb-darkening in Exoplanetary Transits.pdf`  
   Morello et al. (2017) - The Astronomical Journal

2. `ANALYTICLIGHTCURVESFORPLANETARYTRANSITSEARCHES KAISEY MANDEL1,2 AND ERIC AGOL1,3.pdf`  
   Mandel & Agol (2002) - The Astrophysical Journal Letters

3. `An Improved Method for Estimating the Masses of Stars with Transiting Planets. B.Enoch1, A.Collier Cameron1, N.R.Parley1, and L.Hebb2.pdf`  
   Enoch et al. (2010) - Astronomy & Astrophysics

4. `Dai_2023_Res._Astron._Astrophys._23_055011.pdf`  
   Dai et al. (2023) - Research in Astronomy and Astrophysics

5. `High-precision time-series photometry for the discovery and chara.pdf`  
   [Auteur et année à compléter]

6. `Seager_Ormelas_2003.pdf` (optionnel, si disponible)  
   Seager & Mallén-Ornelas (2003) - The Astrophysical Journal

## Utilisation

Ces articles sont référencés dans le document `docs/RESUME_ARTICLES_TRANSIT_ANALYSIS.md` qui contient :
- Des résumés des articles
- Des propositions d'améliorations pour NPOAP
- Des priorités d'implémentation
