# Intùgration KBMOD dans NPOAP

## Faisabilitù technique

**Oui.** KBMOD peut ùtre intùgrù ù NPOAP de plusieurs faùons.

KBMOD est un **package Python** installable (`pip install .` depuis le dùpùt [dirac-institute/kbmod](https://github.com/dirac-institute/kbmod)) et expose une API Python :

- `kbmod.search` : `ImageStack`, `StackSearch`, `Trajectory`
- `kbmod.core.psf` : PSF
- Images : `LayeredImage` (science, mask, variance), chargement FITS possible (utilitaires ou construction manuelle)

NPOAP peut donc en thùorie **importer KBMOD** et lancer une recherche sur une pile de FITS du rùpertoire courant, puis rùcupùrer une liste de trajectoires (candidats) ù proposer comme cible T1 pour la photomùtrie existante.

---

## Contraintes et prùrequis

| Point | Dùtail |
|-------|--------|
| **GPU NVIDIA + CUDA** | KBMOD est conùu pour tourner sur GPU (CUDA ? 8.0). Compilation depuis les sources, CMake, `nvcc` requis. Sans GPU, le traitement est trop lent pour un usage interactif. |
| **Format des images** | KBMOD attend des `LayeredImage` (science + masque + variance). Les FITS NPOAP nùont en gùnùral que la couche science ; il faudrait dùriver la variance (ex. gain/read noise) et ùventuellement un masque (ou couche vide). |
| **Grille de vitesses** | KBMOD a ùtù surtout utilisù pour des objets **lents** (TNO, MBAs). Pour des **NEOs rapides**, il faut adapter la grille de vitesses (min/max, pas) dans les paramùtres de recherche. |
| **Dùpendance optionnelle** | KBMOD ne doit pas ùtre en dùpendance obligatoire de NPOAP (CUDA, compilation lourde). Il doit ùtre proposù comme **option** ù dùtection KBMOD ù, visible seulement si `import kbmod` rùussit. |

---

## Options dùintùgration

### Option A ù Module optionnel dans NPOAP

- Bouton ou menu **ù Dùtection KBMOD ù** dans lùonglet Astùroùdes.
- Charge les FITS du dossier, construit un `ImageStack`, lance `StackSearch` avec des paramùtres par dùfaut (modifiables), affiche les candidats.
- Lùutilisateur en choisit un comme T1 et lance la photomùtrie batch comme aujourdùhui.
- Nùcessite : adaptation FITS ? LayeredImage, gestion du cas ù GPU absent ù (dùsactiver la fonction ou afficher un message).

### Option B ù Workflow externe (recommandù ù court terme)

- KBMOD reste utilisù **en dehors de NPOAP** (script ou notebook).
- Lùutilisateur exporte une liste de dùtections (p. ex. CSV avec RA, Dec, vitesse, score).
- NPOAP propose une fonction **ù Importer des candidats KBMOD ù** pour charger ce fichier et remplir la liste des cibles possibles.
- Lùutilisateur sùlectionne T1 + comparateurs et lance la photomùtrie.
- **Aucune dùpendance CUDA dans NPOAP**, pas dùimpact sur lùinstallation pour les utilisateurs qui ne font que de la photomùtrie.

### Option C ù Sous-processus

- NPOAP appelle KBMOD en ligne de commande (si un CLI existe) ou via un petit script Python dùdiù installù ù part.
- Les rùsultats sont lus depuis un fichier de sortie.
- Moins propre quùune API directe mais ùvite de lier NPOAP ù CUDA.

---

## Recommandation

- **Court terme** : **Option B** (workflow externe + import de candidats). Documenter comment lancer KBMOD sur un dossier de FITS, exporter les trajectoires (RA/Dec, etc.), et importer ce fichier dans NPOAP pour la photomùtrie.
- **Moyen terme** : si des utilisateurs ont un GPU NVIDIA et utilisent KBMOD, ajouter un **module optionnel** (Option A) : dùtection KBMOD intùgrùe, activùe seulement si `kbmod` est installù et quùun GPU est dùtectù, avec fallback vers un message expliquant lùinstallation de KBMOD ou lùusage du workflow externe.

---

## Rùfùrences

- KBMOD : [GitHub dirac-institute/kbmod](https://github.com/dirac-institute/kbmod)
- Documentation : [KBMOD User Manual](https://epyc.astro.washington.edu/~kbmod/user_manual/index.html)
- Voir aussi : `docs/SYNTHETIC_TRACKING_ASTEROIDES.md`

---

## Installation sur Windows (echec de compilation)

Sur Windows, **pip install kbmod** echoue lors de la compilation du code C++ : erreur sur l'include `parallel/algorithm` (extension GCC, absent sous MSVC). KBMOD est donc **retire des dependances obligatoires** dans `requirements.txt`. Pour installer NPOAP : `pip install -r requirements.txt` (sans KBMOD). Pour KBMOD : utiliser **Linux ou WSL** et `pip install -r requirements-kbmod.txt`. Le bouton "Detection KBMOD" n'apparait que si `kbmod` est importable.
