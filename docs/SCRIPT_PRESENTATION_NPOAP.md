# Script de pr�sentation � Projet NPOAP

**NPOAP � Nouvelle Plateforme d'Observation et d'Analyse Photom�trique**

---

## 1. Introduction (30�45 s)

� NPOAP est la **Nouvelle Plateforme d'Observation et d'Analyse Photom�trique**. C�est une application compl�te, gratuite et open-source, d�di�e � la **r�duction**, � la **photom�trie** et � l�**analyse** d�observations astronomiques. Elle couvre un large spectre : exoplan�tes, ast�ro�des, transitoires, �toiles binaires et spectroscopie. L�objectif est de fournir un outil unifi� pour les amateurs, de la calibration des images brutes jusqu�� l�analyse avanc�e des courbes de lumi�re et des syst�mes multiples. �

---

## 2. Les diff�rentes fonctions (2�3 min)

### 2.1 Accueil

� L�onglet **Accueil** est le point d�entr�e. On y configure le **nom de l�observatoire**, la **latitude**, la **longitude** et l�**�l�vation**, utilis�s pour l�astrom�trie et la photom�trie. On y saisit aussi la **cl� API Astrometry.net** pour le plate-solving en ligne, et un **calculateur d��chelle de pixel** permet d�obtenir l��chelle en secondes d�arc par pixel � partir de la taille du pixel et de la focale. �

---

### 2.2 R�duction de donn�es

� L�onglet **R�duction de donn�es** g�re le traitement des images brutes. On d�finit un r�pertoire de travail, on charge les **bias**, **darks**, **flats** et **lights**. NPOAP cr�e automatiquement les **masters** (bias, dark, flat), calibre les images scientifiques et les enregistre dans un dossier d�di�. Ensuite, l�**astrom�trie** peut �tre faite **en ligne** via Astrometry.net (NOVA) ou **localement** avec WSL (solve-field) ou **Watney** : une fois les catalogues t�l�charg�s, Watney permet un plate-solving enti�rement **hors ligne** et rapide. Un **alignement** optionnel des images est aussi propos�. �

---

### 2.3 Photom�trie Exoplan�tes

� L�onglet **Photom�trie Exoplan�tes** est d�di� aux transits. On charge des images FITS r�duites, on s�lectionne la **cible T1** et NPOAP interroge **Gaia DR3** pour proposer des **�toiles de comparaison**, en excluant les variables. La photom�trie diff�rentielle est calcul�e automatiquement avec apertures, annulus et normalisation. Un module d�**ajustement de mod�le** permet d�optimiser **Rp/Rs**, **T0** et des d�trendings (airmass, FWHM, fond de ciel, position). Des indicateurs de qualit� en temps r�el (Chi� r�duit, Shapiro-Wilk, ACF, RMS, SNR, O-C) aident � valider l�observation avant export et soumission. �

---

### 2.4 Photom�trie Ast�ro�des

� L�onglet **Photom�trie Ast�ro�des** sert � la **photom�trie** et � l�**astrom�trie** des ast�ro�des et com�tes. Les **�ph�m�rides** sont r�cup�r�es via **JPL Horizons** (num�ro MPC, d�signation ou nom). Deux m�thodes d�astrom�trie sont disponibles : **classique** (FWHM), rapide, et **zero-aperture** (extrapolation � rayon nul), plus pr�cise, avec statistiques d�taill�es et mots-cl�s FITS pour la qualit�. La photom�trie peut �tre lanc�e image par image ou en **batch**. Pour les objets sans ID, l�astrom�trie et la s�lection manuelle de T1 restent possibles. Les rapports sont g�n�r�s au format **ADES** pour soumission MPC. Une d�tection par **KBMOD** (Synthetic Tracking) est disponible via WSL pour proposer des candidats comme cible T1. �

---

### 2.5 Photom�trie Transitoires

� L�onglet **Photom�trie Transitoires** est pens� pour les **�v�nements transitoires** : novae, supernovae, variables. Le workflow est proche de celui des ast�ro�des : chargement d�images, astrom�trie, s�lection de la cible et des comparateurs, photom�trie diff�rentielle et export en CSV. Un cadre de recherche **TNS** (Transient Name Server) permet de configurer l�API, de chercher des objets par nom ou coordonn�es et de r�cup�rer les d�tails (photom�trie, spectres) pour alimenter l�analyse. �

---

### 2.6 Analyse de donn�es

� L�onglet **Analyse de donn�es** regroupe quatre sous-onglets. **A � D�termination de p�riode** : chargement d�une courbe de lumi�re, p�riodogrammes **Lomb-Scargle**, **BLS** et **Plavchan**, extraction des **mid-times** de transit pour l�analyse TTV. **B � Recherche et analyse TTV** : chargement des mid-times, calcul des **O-C**, affichage de la courbe TTV, ajustement **MCMC sinuso�dal** et g�n�ration d�un **rapport TTV** (amplitude, p�riode, BIC, pr�dictions de r�sonances). **C � Analyse syst�me multiple** : chargement de plusieurs rapports TTV, comparaison des plan�tes (ratios de p�riodes, phases, r�sonances) et **transfert vers la simulation N-body**. **D � Simulation N-body** : avec **rebound**, simulation gravitationnelle du syst�me, extraction des TTV simul�s et comparaison aux observations ; un fitting N-body optionnel (ultranest) permet d�ajuster les param�tres. �

---

### 2.7 �toiles binaires

� L�onglet **�toiles binaires** utilise **PHOEBE2** pour mod�liser des **syst�mes binaires � �clipses**. On cr�e un bundle (binaire ou contact), on charge des donn�es observ�es (CSV : temps, flux, erreur), on ajuste p�riode, �poque et inclinaison, et on lance le calcul du mod�le. Un **ajustement des param�tres** optimise le fit, et une **visualisation 3D** interactive permet de voir les orbites et d�animer le syst�me. Les bundles peuvent �tre sauvegard�s et recharg�s. �

---

### 2.8 Easy Lucky Imaging

� L�onglet **Easy Lucky Imaging** permet de traiter des images d�**�toiles doubles** (m�thodes REDUC) et surtout de mesurer avec pr�cision la **s�paration angulaire** (?) et l�**angle de position** (?) entre deux �toiles. L�image doit �tre astrom�tri�e ; le Nord et l�Est c�lestes sont calcul�s via le WCS. On clique sur les deux �toiles, les centro�des sont affin�s, et les mesures sont affich�es avec une repr�sentation graphique (fl�ches N/E, ligne de s�paration, arc ?). L��chelle de pixel peut �tre celle configur�e � l�Accueil. �

---

### 2.9 Catalogues

� L�onglet **Catalogues** permet d�**extraire et g�rer** des donn�es depuis plusieurs sources. **�toiles** : Gaia DR3, TESS EBS, Vizier. **Ast�ro�des et com�tes** : t�l�chargement des catalogues MPC (NEA, com�tes), affichage et tri. **�toiles binaires** : � partir de CSV Gaia DR3, calcul de la **s�paration lin�aire** (m�thode Laurent 2022) pour identifier des couples physiques, avec export possible vers **NINA** (fichiers JSON). **Exoplan�tes** : extraction depuis Exoplanet.eu et sources via Vizier. �

---

### 2.10 Spectroscopie

� L�onglet **Spectroscopie** permet de charger, visualiser et analyser des **spectres** (FITS ou ASCII). Pour les �toiles : **normalisation du continuum**, s�lection de r�gions et mesure d�**�quivalent de largeur**, flux de raie, centro�de, FWHM. Pour les **galaxies**, l�option **Prospector** (optionnelle) permet d�inf�rer des propri�t�s stellaires (�ge, m�tallicit�, extinction, redshift) � partir du spectre ou d�une SED construite depuis la photom�trie, via inf�rence bay�sienne (MCMC). �

---

## 3. Synth�se du workflow (15�20 s)

� En r�sum�, le workflow type est : **R�duction de donn�es** pour calibrer et astrom�trier les images, puis **Photom�trie** selon le type d�objet (exoplan�tes, ast�ro�des, transitoires), et enfin **Analyse de donn�es** pour les p�riodes, TTV et simulations N-body. Les onglets Binaires, Easy Lucky Imaging, Catalogues et Spectroscopie compl�tent la cha�ne selon les besoins. �

---

## 4. Possibilit�s futures (45�60 s)

� Plusieurs �volutions sont envisag�es ou d�j� en cours.

- **Astrom�trie locale** : l�int�gration de **Watney** permet d�j� un plate-solving local sous Windows, sans internet ; l�utilisation de catalogues Gaia pr�par�s (Quad DB) rend le traitement rapide et fiable. Le support d�autres solveurs locaux peut �tre �tendu.

- **D�tection d�ast�ro�des** : la d�tection **KBMOD** (Synthetic Tracking) via WSL est en place ; les pistes d��volution incluent un module de d�tection plus int�gr� (exploration de vecteurs vitesse/position, shift-and-stack, id�alement GPU) pour proposer directement des candidats � la photom�trie, et une documentation sur les bonnes pratiques (nombre de poses, logiciels type Tycho/KBMOD) pour aller plus profond en magnitude.

- **Transitoires TNS** : un onglet d�di� � Transitoires TNS � pourrait offrir une recherche avanc�e (filtres magnitude, type, redshift), une gestion de listes et favoris, une visualisation des courbes de lumi�re et spectres TNS, et un lien direct avec l�onglet Photom�trie Transitoires pour pr�-remplir les coordonn�es.

- **Qualit� et pr�cision** : les r�f�rences document�es (Farnocchia et al., articles sur les transits) orientent des am�liorations continues : incertitudes astrom�triques, extrapolation zero-aperture, gestion des effets syst�matiques et indicateurs de qualit� des courbes de lumi�re.

- **Distributions cibl�es** : le syst�me de build permet d�j� de g�n�rer des distributions partielles (ex. profil � ast�ro�des �, � binaires �) pour des installations plus l�g�res selon l�usage. �

---

## 5. Conclusion (15�20 s)

� NPOAP vise � �tre une **plateforme unique** pour l�observation et l�analyse photom�trique, de la calibration � l�analyse avanc�e, avec une forte orientation **exoplan�tes**, **ast�ro�des** et **transitoires**, et des prolongements **binaires** et **spectroscopie**. Les �volutions pr�vues renforcent l�astrom�trie locale, la d�tection d�objets mobiles et l�int�gration avec les bases de donn�es professionnelles. Merci de votre attention. �

---

**Dur�e totale indicative : 5�7 minutes** (selon le d�bit et les d�monstrations � l��cran).

*Document g�n�r� pour la pr�sentation du projet NPOAP � F�vrier 2026.*
