# NPOAP � Pr�sentation du logiciel

**Nouvelle Plateforme d'Observation et d'Analyse Photom�trique**

---

## Logique principale

NPOAP a pour objectif d�**agr�ger dans une seule plateforme** un ensemble de **fonctionnalit�s fond�es sur la photom�trie** pour l�**analyse des propri�t�s astrophysiques** d�objets tr�s vari�s : exoplan�tes, ast�ro�des, transitoires (novae, supernovae, variables), �toiles binaires, �toiles doubles, spectres d��toiles et de galaxies. De la **r�duction des images brutes** jusqu�� l�**analyse avanc�e** (courbes de lumi�re, TTV, mod�lisation, simulations N-body), une m�me interface permet de traiter des observations h�t�rog�nes et d�en extraire des grandeurs physiques (flux, magnitudes, param�tres orbitaux, propri�t�s stellaires). La plateforme est **�volutive et participative** : les astronomes amateurs qui le souhaitent peuvent **demander des am�liorations** et **d�velopper de nouvelles fonctionnalit�s** qui seront **int�gr�es** au projet, dans un esprit open-source et communautaire.

---

## Description des fonctionnalit�s

### Accueil
Configuration de l�observatoire (nom, latitude, longitude, �l�vation), cl� API Astrometry.net pour le plate-solving en ligne, et calculateur d��chelle de pixel (taille du pixel, focale ? secondes d�arc par pixel).

### R�duction de donn�es
Traitement des images brutes : chargement des bias, darks, flats et lights ; cr�ation automatique des masters ; calibration des images ; astrom�trie en ligne (NOVA) ou locale (WSL, solve-field) ; alignement WCS optionnel (reprojection sur une grille commune) ; empilement (median stack). Les images calibr�es, r�solues et align�es sont organis�es dans une arborescence claire (output/, science/, science/aligned/).

### Photom�trie exoplan�tes
Analyse des transits : chargement d�images FITS r�duites, s�lection de la cible et interrogation Gaia DR3 pour les �toiles de comparaison (variables exclues), photom�trie diff�rentielle (apertures, annulus, normalisation), ajustement de mod�le (Rp/Rs, T0, d�trendings), indicateurs de qualit� (Chi�, Shapiro-Wilk, ACF, RMS, O-C) et export pour soumission.

### Photom�trie ast�ro�des
Photom�trie et astrom�trie d�ast�ro�des et com�tes : �ph�m�rides JPL Horizons, astrom�trie classique ou zero-aperture, photom�trie image par image ou en batch, rapports ADES pour le MPC, d�tection KBMOD (Synthetic Tracking) via WSL pour proposer des candidats comme cible.

### Photom�trie transitoires
�v�nements transitoires (novae, supernovae, variables) : chargement d�images, astrom�trie, s�lection cible et comparateurs, photom�trie diff�rentielle, recherche et int�gration TNS (Transient Name Server), export CSV.

### Analyse de donn�es
- **D�termination de p�riode** : courbes de lumi�re, p�riodogrammes Lomb-Scargle, BLS, Plavchan, extraction des mid-times de transit.  
- **Recherche et analyse TTV** : O-C, courbe TTV, ajustement MCMC sinuso�dal, rapport TTV (amplitude, p�riode, BIC, r�sonances).  
- **Analyse syst�me multiple** : comparaison de plusieurs rapports TTV, ratios de p�riodes, phases, transfert vers simulation N-body.  
- **Simulation N-body** : int�gration gravitationnelle (rebound), TTV simul�s, comparaison aux observations, fitting N-body optionnel (ultranest).

### �toiles binaires
Mod�lisation de syst�mes binaires � �clipses avec PHOEBE2 : cr�ation de bundles, chargement de donn�es observ�es (CSV), ajustement p�riode/�poque/inclinaison, calcul du mod�le, optimisation des param�tres, visualisation 3D et animation du syst�me.

### Easy Lucky Imaging
Traitement d�images d��toiles doubles (m�thodes type REDUC) et mesure pr�cise de la **s�paration angulaire** et de l�**angle de position** (WDS), � partir d�images astrom�tr�es, avec affichage des directions N/E et de l��chelle de pixel.

### Catalogues
Extraction et gestion de donn�es : Gaia DR3, TESS EBS, Vizier (�toiles) ; MPC NEA et com�tes (ast�ro�des/com�tes) ; s�paration lin�aire Gaia pour binaires physiques (Laurent 2022), export NINA ; Exoplanet.eu et Vizier (exoplan�tes).

### Spectroscopie
Chargement et analyse de spectres (FITS, ASCII) : normalisation du continuum, r�gions spectrales, �quivalent de largeur, flux, centro�de, FWHM. Pour les galaxies, option Prospector (inf�rence bay�sienne : �ge, m�tallicit�, extinction, redshift) � partir du spectre ou d�une SED.

---

## Plateforme �volutive et participative

NPOAP est con�ue comme une **plateforme ouverte et �volutive**. Les astronomes amateurs peuvent :

- **Demander des am�liorations** : suggestions de fonctionnalit�s, corrections de bugs, am�lioration de l�ergonomie ou de la documentation.  
- **Proposer et d�velopper de nouvelles fonctionnalit�s** : le code est structur� pour permettre l�ajout de modules (onglets, outils d�analyse, connecteurs � de nouveaux catalogues ou services). Les contributions, sous r�serve de revue, peuvent �tre **int�gr�es** au logiciel pour en faire b�n�ficier toute la communaut�.

Cette d�marche participative vise � faire de NPOAP un outil vivant, adapt� aux pratiques r�elles des observateurs et align� sur l��volution des besoins (nouvelles missions, nouveaux catalogues, nouvelles m�thodes d�analyse).

---

## En r�sum�

NPOAP **rassemble dans une seule application** les �tapes qui vont de l�**acquisition** (r�duction, calibration, astrom�trie, alignement, empilement) � l�**analyse astrophysique** (photom�trie diff�rentielle, courbes de lumi�re, TTV, mod�lisation binaire, N-body, spectroscopie). La **photom�trie** est au c�ur du dispositif pour d�river des **propri�t�s astrophysiques** (magnitudes, param�tres de transit, orbites, propri�t�s stellaires). La plateforme reste **�volutive et participative** : demandes d�am�liorations et d�veloppements de nouvelles fonctionnalit�s par les amateurs sont les bienvenus et peuvent �tre int�gr�s au projet.

---

*Document de pr�sentation NPOAP � F�vrier 2026.*
