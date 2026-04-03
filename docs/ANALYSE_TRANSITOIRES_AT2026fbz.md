# Analyse du fonctionnement – Transitoires (AT 2026fbz)

Analyse basée sur :
- **Image soustraite** : `subtracted_STACKED_AT 2026fbz_2026-03-10_FilterG_Exp300.00.fits`
- **Résultats photométrie** : `AT 2026fbz_2026-03-10.xlsm` (cible ligne 6)
- **Log** : `logs/npoap_10496.log`

---

## 1. Chaîne traitée (résumé log)

| Étape | Statut | Détail |
|-------|--------|--------|
| Chargement science | OK | Coordonnées champ RA=67.76°, Dec=-68.50° |
| Soustraction | OK | Méthode alternative (reproject), Zogy demandé → soustraction simple normalisée |
| Détection | OK | photutils_segmentation, seuils 100 puis 200 sigma |
| Photométrie (1re fois) | ⚠️ | "Pas assez d'étoiles de référence pour calibrer" |
| Photométrie (2e fois) | OK | Méthode PSF demandée → aperture (photutils.psf indisponible), calibration Gaia exécutée |
| Recherche TNS | ❌ | **401 Unauthorized** |

---

## 2. Image soustraite et soustraction

- **Échelles** : science 0,802"/pixel, référence 3,516"/pixel → ratio 4,39. Les échelles différentes obligent à utiliser la **méthode alternative** (reproject) au lieu de la soustraction STDPipe native.
- **Zogy** : demandé mais non utilisé ; le code bascule en "soustraction simple avec normalisation". Comportement cohérent si Zogy n’est pas disponible ou non applicable.
- Le fichier soustrait est bien créé à l’emplacement indiqué.

**Conclusion** : La soustraction fonctionne correctement dans ce contexte (rééchantillonnage de la référence vers la science).

---

## 3. Détection de transitoires

- **Méthode** : `photutils_segmentation`, FWHM 5 px, déblending activé.
- **Seuils utilisés** : 100 σ puis 200 σ. Ce sont des seuils **très élevés** (typiquement 3–5 σ en détection). Ils ne gardent que les sources les plus brillantes et réduisent les faux positifs au prix d’un risque de manquer des transitoires faibles.
- La cible apparaît à la **ligne 6** de vos résultats photométriques, donc elle a bien été détectée (probablement lors d’une des runs avec ces paramètres).

**Recommandation** : Pour des transitoires plus faibles, tester des seuils plus bas (5–10 σ) tout en vérifiant le nombre de faux positifs.

---

## 4. Photométrie

- **Image utilisée** : l’**image science** (pas l’image soustraite), ce qui est correct : on mesure le flux sur la science aux positions des transitoires détectés sur la soustraction.
- **1re tentative** : **"Pas assez d'étoiles de référence pour calibrer"**. La calibration Gaia exige au moins **3 sources** avec à la fois :
  - un match Gaia dans un rayon de ~0,36" (0,0001 deg),
  - un flux valide.
  Si peu de détections ou peu de matches Gaia (champ pauvre, saturation, etc.), le zero point n’est pas calculé et les magnitudes restent en magnitude instrumentale.
- **2e tentative** : nombreuses requêtes astroquery (Gaia) et succès ; la cible est bien en ligne 6 des résultats.
- **PSF** : choix "psf" → le code détecte que `photutils.psf` n’est pas disponible et bascule automatiquement en **photométrie d’ouverture**. Comportement attendu.

**Conclusion** : La photométrie a fini par aboutir ; le premier échec est lié au nombre d’étoiles de référence Gaia, pas à un bug évident.

---

## 5. Recherche TNS : pourquoi “rien” alors qu’il existe un télégramme

Dans le log :

```text
11:55:40 - ERROR - core.tns_client - Erreur HTTP TNS: 401 - Unauthorized
11:55:58 - ERROR - core.tns_client - Erreur HTTP TNS: 401 - Unauthorized
```

Donc la recherche TNS **ne retourne pas “aucun résultat”** : elle **échoue avant** toute réponse utile, avec une **401 Unauthorized**.

### 5.1 Cause probable : authentification

- **401** = le serveur TNS refuse la requête parce que l’authentification est invalide ou absente.
- Le client TNS utilise :
  - **Bot ID** et **API Key** (chargés depuis `config.TNS_CONFIG` ou saisis dans l’onglet),
  - et par défaut l’**environnement Sandbox** (`use_sandbox: True`).

Conséquences possibles :

1. **Bot ID / API Key** : non renseignés dans l’interface, ou non sauvegardés, ou credentials **production** utilisés contre l’**API Sandbox** (ou l’inverse). Les identifiants Sandbox et Production TNS sont en général **différents**.
2. **Sandbox vs Production** :  
   - **Sandbox** = environnement de test ; la base contient surtout des objets de démo.  
   - **AT 2026fbz** est un transitoire réel (télégramme) : il est dans la base **Production**, pas forcément dans le Sandbox.  
   Même avec une requête acceptée, une recherche **uniquement en Sandbox** peut donc ne rien retourner pour un objet réel.

### 5.2 Ce qui a été modifié dans le code

- **Choix explicite Production / Sandbox** dans l’interface (onglet Photométrie Transitoires, cadre TNS) : la recherche utilise l’URL et les credentials pour l’environnement choisi.
- **En cas de 401** : message clair indiquant que l’erreur est une **erreur d’authentification** et suggérant de :
  - vérifier Bot ID et API Key,
  - utiliser **Production** pour chercher de vrais objets comme AT 2026fbz.
- **Normalisation du nom d’objet** : les noms du type "AT 2026fbz" sont envoyés tels quels ; l’API TNS accepte en général "AT 2026fbz" ou "2026fbz". Si besoin, on peut ajouter une tentative avec l’autre format.

En résumé : **la recherche TNS n’a “rien donné” à cause du 401 (authentification), pas parce que l’objet n’existe pas.** En configurant correctement les identifiants et en utilisant **Production** pour AT 2026fbz, la recherche pourra répondre (si l’objet est bien présent côté TNS).

---

## 6. Synthèse et actions recommandées

| Sujet | État | Action suggérée |
|-------|------|------------------|
| Soustraction | OK | Aucune |
| Détection | OK, seuils très élevés | Tester 5–10 σ si besoin de sources plus faibles |
| Calibration Gaia | ⚠️ 1er échec, 2e OK | Vérifier champ (densité Gaia) ; garder 2e run comme référence |
| Photométrie PSF | Fallback aperture | Optionnel : installer/activer `photutils.psf` si besoin |
| **TNS** | **401 Unauthorized** | Renseigner Bot ID + API Key, choisir **Production**, puis relancer la recherche pour "AT 2026fbz" |

Une fois TNS configuré en Production avec des identifiants valides, la recherche par nom "AT 2026fbz" (ou "2026fbz") devrait pouvoir retourner l’objet correspondant au télégramme.
