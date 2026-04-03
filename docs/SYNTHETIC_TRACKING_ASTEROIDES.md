# Synthetic Tracking et amélioration de la détection des astéroïdes

## 1. Article iTelescope (Daniel Parrott, 16 mars 2019)

### Contexte
- Session du **8 septembre 2018**, iTelescope T9 (réfracteur 127 mm), **50 poses de 3 minutes**.
- Objectif : optimiser un programme basé sur le **Synthetic Tracking** pour la détection d’astéroïdes.

### Technique conventionnelle
- **3 à 4 poses** à intervalle régulier pour repérer les mouvements cohérents.
- **Limites** : le SNR reste celui d’**une seule pose** (pas de sommation) ; champs stellaires denses difficiles à traiter.
- Dans le jeu de données test : **53 astéroïdes**, **magnitude limite 18,9**.

### Synthetic Tracking
- Sommer les poses selon **toutes les combinaisons pertinentes** de vecteurs de mouvement (vitesse + PA), puis repérer les objets qui ressortent ? détection **aveugle** (sans connaître le mouvement à l’avance).
- Accéléré par **GPU** (~15–20 min par jeu de données).
- **Résultats** : **281 astéroïdes**, **magnitude limite 20,8** ; détection du **NEO 2018 RB**, manqué par la technique conventionnelle.

| Méthode            | Astéroïdes détectés | Magnitude limite |
|-------------------|---------------------|------------------|
| Conventionnelle   | 53                  | 18,9             |
| Synthetic Tracking| 281                 | 20,8             |

---

## 2. Tycho : logiciel GPU Synthetic Tracker (Parrott, 3 février 2019)

### Résumé
**Tycho** est un logiciel de détection **aveugle** de NEOs et MBAs par Synthetic Tracking. Il est décrit comme le **premier** à combiner :
- **GPU** (accélération graphique),
- **grandes images** (ex. 16 Mpx, traitement en ~20 min),

alors que les travaux antérieurs utilisaient soit de petites images (Shao 2013, 0,26 Mpx) soit de très grandes images sans GPU (Heinze 2015, 144 Mpx, ~50 jours de calcul).

### Métrique « trial pixels » (Heinze)
- **Trial stack** = une somme d’images selon un **vecteur d’essai** (vitesse + angle).
- **Trial pixels** = nombre d’images × nombre de vecteurs × largeur × hauteur, pour comparer équitablement les logiciels.

### Comparaison des trackers Synthetic Tracking (Table 1 du document Tycho)

|          | Heinze   | Shao/Zhai | Tycho    |
|----------|----------|-----------|----------|
| Images   | 256      | 1500      | 50       |
| Vecteurs d’essai | 28 086 | 10 000    | 19 881   |
| Dimensions (px)  | 12 000×12 000 | 512×512 | 1536×1024 |
| Temps    | 1 200 h  | 0,025 h   | 0,0319 h |
| **VP/h** | 8,63e11  | 1,57e14   | **4,90e13** |
| Matériel | 32-core Xeon | NVIDIA Tesla K20c | **NVIDIA GTX 970** |

? Un **GPU grand public** (GTX 970) rend le Synthetic Tracking utilisable en temps raisonnable pour des images de taille modérée (16 Mpx, ~20 min).

### SNR et nombre de poses (courbes ROC)
- Plus le **nombre de poses** augmente, plus la probabilité de détection (Pd) à faux alarme fixe s’améliore.
- Exemple (données simulées, télescope 500 mm) :
  - **11 poses** : V?19,8 quasi 100 %, V?20,6 seulement ~11 %.
  - **25 poses** : V?20,6 à ~55 %.
  - **50 poses** : V?20,6 quasi 100 %, V?21,0 à ~26 %.

### Cibles simulées : Tycho vs technique conventionnelle (Table 3)
- 100 cibles injectées, 50 poses, vitesse 1,40 "/min.
- **Technique conventionnelle** : 73 % à V18,2 ; 37 % à V18,9 ; **0 % à partir de V19,7**.
- **Tycho (Synthetic Tracking)** : **100 % jusqu’à V20,0** ; 98 % à V20,4 ; 74 % à V21,0 ; 70 % à V21,2.

### Données réelles – NEOs (Table 4)
- **9 NEOs** testés : **Tycho 7/9** en recherche aveugle, **technique conventionnelle 1/9** (2018 RP8 uniquement).
- Ex. **2018 ST1** : 57 "/min, 20 poses × 4 s ; à l’image seule le NEO est à peine visible ; après stacking selon le bon vecteur, SNR nettement amélioré ; Tycho l’a classé **1er** en ~7 min.

### Données réelles – MBAs (Table 5)
- **11 MBAs** (500 mm, Siding Spring, 20 poses × 120 s) : **Tycho 11/11**, **technique conventionnelle 5/11**.

### Conclusions du document Tycho
- Le Synthetic Tracking permet de détecter des astéroïdes **faibles et rapides** inaccessibles en conventionnel.
- Une **GTX 970 ou équivalent** suffit pour un usage amateur (découverte de NEOs, pas seulement suivi).
- Les **champs encombrés** (ex. Voie lactée) sont mieux gérés par le Synthetic Tracking que par les algorithmes classiques (ex. type Catalina).
- **Tycho** = grandes images + GPU ? adapté à des **campagnes de survey** avec temps de traitement court.

---

## 3. Lien avec NPOAP

### Ce que fait NPOAP aujourd’hui
- **Photométrie d’astéroïdes déjà connus** : cible T1 + étoiles de comparaison (C1, C2, …), flux en ouverture, fond de ciel, flux relatif, éventuellement zéro photométrique Gaia.
- **Une image de référence** définit les positions ; T1 est suivi par éphémérides ou positions astrométriques image par image.
- Pas de **détection aveugle** ni de sommation selon des vecteurs de mouvement.

### Où Synthetic Tracking (et Tycho) peuvent aider
1. **En amont de NPOAP** : détecter plus d’astéroïdes (et plus faibles) dans une série de poses, puis fournir à NPOAP des cibles pour la photométrie différentielle.
2. **Stratégie d’observation** : privilégier **plus de poses** (12–50) sur un même champ si l’objectif est profondeur ou découverte ; un logiciel type **Tycho** ou **KBMOD** exploite ensuite ces données.
3. **Champs encombrés** : le Synthetic Tracking est plus robuste en champs denses (Voie lactée) que la technique conventionnelle.

---

## 4. Pistes d’évolution possibles

### Option A – Outils externes (recommandé à court terme)
- **Tycho** (Daniel Parrott, 2019) : Synthetic Tracking GPU, grandes images, démontré sur NEOs et MBAs ; à privilégier si le logiciel est disponible/distribué.
- **KBMOD** (Kernel Based Moving Object Detection) : framework GPU shift-and-stack pour objets en mouvement.
- **Workflow** : 1) Acquérir une série de poses (20–50). 2) Lancer Tycho ou KBMOD. 3) Exporter les détections et utiliser NPOAP pour la **photométrie différentielle** (T1 + comparateurs).

### Option B – Module « détection » dans NPOAP (moyen terme)
- Module optionnel : entrée = liste de FITS ; exploration de vecteurs (vitesse, PA) + shift-and-stack (idéalement GPU) ; sortie = liste de candidats pour le pipeline photométrie astéroïdes existant.

### Option C – Documentation et bonnes pratiques
- Dans la doc « astéroïdes » : rappeler que **plus de poses** (12–50) + logiciel Synthetic Tracking (Tycho, KBMOD) permettent d’aller **~2 mag plus profond** et de détecter bien plus d’objets (dont NEOs rapides).
- Références : article iTelescope Parrott (mars 2019), document Tycho Parrott (février 2019), Shao (arXiv), KBMOD, NASA NTRS.

---

## 5. Références

- Parrott, D. (2019), *One Refractor, One Field: 281 Asteroids, Limiting Magnitude 20.8*, iTelescope (16 mars 2019).
- Parrott, D. (2019), *Tycho: A GPU-Accelerated Synthetic Tracker for Blind Detection of NEOs, MBAs, and other Moving Objects* (3 février 2019).
- Shao, M. et al., *Finding Very Small Near-Earth Asteroids using Synthetic Tracking*, arXiv:1309.3248 (2013).
- Zhai, C. et al. (2014), follow-up to Shao – détails images et temps de traitement.
- Heinze, A. et al. (2015), Synthetic Tracking sur 144 Mpx, 215 MBAs, 32-core, 50 jours.
- KBMOD (Kernel Based Moving Object Detection), framework GPU.
- NASA NTRS, *Synthetic Tracking on a Small Telescope* (2021).

---

*Document mis à jour pour intégrer l’article iTelescope et le document technique Tycho (logiciel Synthetic Tracking GPU) aux pistes d’amélioration de la détection et de la photométrie des astéroïdes dans NPOAP.*
