# Guide : Création d'un Onglet Dédié pour les Transitoires TNS

## État Actuel

Un cadre de recherche TNS a été ajouté dans l'onglet "Photométrie Transitoires" sur la partie droite. Ce cadre permet :
- Configuration de l'API TNS (Bot ID, API Key)
- Recherche d'objets transitoires par nom ou coordonnées
- Affichage des résultats
- Récupération des détails d'un objet (photométrie, spectres)

## Structure Actuelle

### Fichiers Créés/Modifiés

1. **`core/tns_client.py`** : Client API TNS
   - Classe `TNSClient` pour interagir avec l'API TNS
   - Méthodes : `search_objects()`, `get_object()`, `get_file()`
   - Support SANDBOX et Production

2. **`gui/transient_photometry_tab.py`** : Modifié
   - Layout en deux colonnes (PanedWindow)
   - Partie gauche : Workflow STDPipe existant
   - Partie droite : Cadre de recherche TNS

3. **`config.py`** : Ajout de `TNS_CONFIG`
   - Configuration pour Bot ID, API Key, etc.

## Option 1 : Créer un Onglet Dédié "Transitoires TNS"

Si vous souhaitez créer un onglet complètement séparé pour la gestion des transitoires TNS, voici la structure recommandée :

### Structure Proposée

```
gui/
  └── transient_tns_tab.py  # Nouvel onglet dédié
```

### Fonctionnalités de l'Onglet Dédié

1. **Recherche Avancée**
   - Recherche par nom, coordonnées, date de découverte
   - Filtres multiples (magnitude, type d'objet, redshift, etc.)
   - Recherche par groupe/observateur

2. **Gestion des Objets**
   - Liste des objets suivis
   - Favoris/bookmarks
   - Historique des recherches

3. **Visualisation**
   - Courbes de lumière (si photométrie disponible)
   - Spectres (si disponibles)
   - Informations détaillées (classification, redshift, etc.)

4. **Export/Import**
   - Export des résultats en CSV/JSON
   - Import de listes d'objets à suivre
   - Génération de rapports

5. **Intégration avec Photométrie**
   - Lien direct vers l'onglet "Photométrie Transitoires"
   - Pré-remplissage des coordonnées depuis TNS

### Exemple de Code pour l'Onglet Dédié

```python
# gui/transient_tns_tab.py
"""
Onglet dédié pour la recherche et la gestion des transitoires via TNS.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import json
from pathlib import Path
import logging

from core.tns_client import TNSClient

logger = logging.getLogger(__name__)


class TransientTNSTab(ttk.Frame):
    """
    Onglet dédié pour la recherche et gestion des transitoires TNS.
    """
    
    def __init__(self, parent, base_dir=None):
        super().__init__(parent, padding=10)
        
        self.base_dir = Path(base_dir) if base_dir else Path.home()
        self.tns_client = None
        self.search_results = []
        self.followed_objects = []  # Objets suivis
        
        self.load_tns_client()
        self.create_widgets()
    
    def load_tns_client(self):
        """Charge le client TNS depuis la configuration."""
        try:
            import config
            tns_config = getattr(config, 'TNS_CONFIG', {})
            self.tns_client = TNSClient(
                bot_id=tns_config.get('bot_id', ''),
                api_key=tns_config.get('api_key', ''),
                bot_name=tns_config.get('bot_name', 'NPOAP'),
                use_sandbox=tns_config.get('use_sandbox', True)
            )
        except Exception as e:
            logger.error(f"Erreur chargement client TNS: {e}")
    
    def create_widgets(self):
        """Crée l'interface de l'onglet."""
        # Layout en 3 sections : Recherche | Résultats | Détails
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Section gauche : Recherche
        search_frame = ttk.Frame(paned, padding=10)
        paned.add(search_frame, weight=1)
        self.create_search_section(search_frame)
        
        # Section centrale : Résultats
        results_frame = ttk.Frame(paned, padding=10)
        paned.add(results_frame, weight=2)
        self.create_results_section(results_frame)
        
        # Section droite : Détails
        details_frame = ttk.Frame(paned, padding=10)
        paned.add(details_frame, weight=1)
        self.create_details_section(details_frame)
    
    def create_search_section(self, parent):
        """Crée la section de recherche."""
        # ... (code de recherche similaire au cadre actuel mais plus complet)
        pass
    
    def create_results_section(self, parent):
        """Crée la section d'affichage des résultats."""
        # ... (tableau avec colonnes : Nom, RA, Dec, Date, Type, etc.)
        pass
    
    def create_details_section(self, parent):
        """Crée la section d'affichage des détails."""
        # ... (affichage détaillé de l'objet sélectionné)
        pass
```

### Intégration dans main_window.py

```python
# Dans gui/main_window.py
from gui.transient_tns_tab import TransientTNSTab

# Dans __init__ :
self.transient_tns_tab = TransientTNSTab(self.notebook)

# Dans l'ajout au notebook :
self.notebook.add(self.transient_tns_tab, text="🌌 Transitoires TNS")
```

## Option 2 : Améliorer le Cadre Actuel

Si vous préférez garder le cadre dans l'onglet "Photométrie Transitoires", vous pouvez l'améliorer avec :

1. **Recherche par Date**
   - Date de découverte début/fin
   - Filtre par magnitude

2. **Filtres Avancés**
   - Type d'objet (SN Ia, SN II, etc.)
   - Redshift
   - Groupe/observateur

3. **Intégration avec STDPipe**
   - Pré-remplir les coordonnées depuis TNS
   - Comparer les transitoires détectés avec TNS

## Recommandation

**Option 1 (Onglet Dédié)** est recommandée si :
- Vous avez besoin de fonctionnalités avancées de gestion
- Vous suivez régulièrement plusieurs transitoires
- Vous voulez séparer la recherche TNS de l'analyse photométrique

**Option 2 (Cadre Amélioré)** est suffisante si :
- La recherche TNS est complémentaire à l'analyse photométrique
- Vous utilisez TNS principalement pour vérifier des coordonnées
- Vous préférez garder tout dans un seul onglet

## Prochaines Étapes

1. **Tester le cadre actuel** avec des recherches réelles
2. **Décider** si un onglet dédié est nécessaire
3. **Implémenter** les fonctionnalités manquantes selon vos besoins
