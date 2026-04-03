"""
Onglet dédié pour la recherche et la gestion des transitoires via TNS.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
import json
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Import du client TNS
try:
    from core.tns_client import TNSClient, TNSUnauthorizedError
    TNS_AVAILABLE = True
except ImportError:
    TNS_AVAILABLE = False
    TNSClient = None


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
        self.current_object_details = None  # Détails de l'objet actuellement sélectionné
        
        self.load_tns_client()
        self.create_widgets()
    
    def load_tns_client(self):
        """Charge le client TNS depuis la configuration."""
        try:
            import config
            tns_config = getattr(config, 'TNS_CONFIG', {})
            self.tns_client = TNSClient(
                bot_id=tns_config.get('bot_id'),
                api_key=tns_config.get('api_key', ''),
                bot_name=tns_config.get('bot_name', 'NPOAP'),
                use_sandbox=tns_config.get('use_sandbox', False),
                tns_marker_type=tns_config.get('tns_marker_type', 'user'),
                tns_id=tns_config.get('tns_id'),
                tns_name=tns_config.get('tns_name'),
            )
            logger.info("Client TNS initialisé")
        except Exception as e:
            logger.error(f"Erreur chargement client TNS: {e}")
    
    def create_widgets(self):
        """Crée l'interface de l'onglet."""
        # Titre
        title = ttk.Label(self, text="🌌 Recherche et Gestion des Transitoires TNS", 
                         font=("Helvetica", 14, "bold"))
        title.pack(pady=10)
        
        # Layout en 3 sections : Recherche | Résultats | Détails
        paned_main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Section gauche : Recherche et Configuration
        search_frame = ttk.Frame(paned_main, padding=10)
        paned_main.add(search_frame, weight=1)
        self.create_search_section(search_frame)
        
        # Section centrale : Résultats
        results_frame = ttk.Frame(paned_main, padding=10)
        paned_main.add(results_frame, weight=2)
        self.create_results_section(results_frame)
        
        # Section droite : Détails
        details_frame = ttk.Frame(paned_main, padding=10)
        paned_main.add(details_frame, weight=1)
        self.create_details_section(details_frame)
    
    def create_search_section(self, parent):
        """Crée la section de recherche."""
        # Configuration API (User-Agent TNS)
        config_frame = ttk.LabelFrame(parent, text="Configuration API (User-Agent TNS)", padding=10)
        config_frame.pack(fill="x", pady=5)

        ttk.Label(config_frame, text="Type compte:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.tns_marker_type_var = tk.StringVar(value="user")
        tns_type_combo = ttk.Combobox(config_frame, textvariable=self.tns_marker_type_var,
                                     values=["user", "bot"], state="readonly", width=10)
        tns_type_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="TNS ID (user):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.tns_id_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.tns_id_var, width=20).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="Nom (user):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.tns_name_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.tns_name_var, width=20).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="Bot ID (bot):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.tns_bot_id_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.tns_bot_id_var, width=20).grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="Nom (bot):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.tns_bot_name_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.tns_bot_name_var, width=25).grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="API Key (requise pour Search):").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.tns_api_key_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.tns_api_key_var, width=20, show="*").grid(row=5, column=1, padx=5, pady=2)

        ttk.Button(config_frame, text="💾 Sauvegarder Config",
                  command=self.save_tns_config).grid(row=6, column=0, columnspan=2, pady=5)
        
        # Charger la configuration existante
        self.load_tns_config()
        
        # Recherche
        search_frame = ttk.LabelFrame(parent, text="Recherche", padding=10)
        search_frame.pack(fill="x", pady=5)
        
        # Nom d'objet
        ttk.Label(search_frame, text="Nom objet:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.tns_objname_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_objname_var, width=25).grid(row=0, column=1, padx=5, pady=2)
        
        # Coordonnées
        ttk.Label(search_frame, text="RA (°):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.tns_ra_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_ra_var, width=25).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Dec (°):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.tns_dec_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_dec_var, width=25).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Rayon (arcsec):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.tns_radius_var = tk.StringVar(value="60")
        ttk.Entry(search_frame, textvariable=self.tns_radius_var, width=25).grid(row=3, column=1, padx=5, pady=2)
        
        # Séparateur pour les dates
        ttk.Separator(search_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Recherche par date
        ttk.Label(search_frame, text="Date début (YYYY-MM-DD):").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.tns_date_start_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_date_start_var, width=25).grid(row=5, column=1, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Date fin (YYYY-MM-DD):").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        self.tns_date_end_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_date_end_var, width=25).grid(row=6, column=1, padx=5, pady=2)
        
        # Filtres avancés (optionnels)
        ttk.Separator(search_frame, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Label(search_frame, text="Magnitude min:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        self.tns_mag_min_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_mag_min_var, width=25).grid(row=8, column=1, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Magnitude max:").grid(row=9, column=0, sticky="e", padx=5, pady=2)
        self.tns_mag_max_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tns_mag_max_var, width=25).grid(row=9, column=1, padx=5, pady=2)
        
        ttk.Button(search_frame, text="🔍 Rechercher", 
                  command=self.search_tns).grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(search_frame, text="🔄 Réinitialiser", 
                  command=self.reset_search_fields).grid(row=11, column=0, columnspan=2, pady=5)
    
    def create_results_section(self, parent):
        """Crée la section d'affichage des résultats."""
        # Titre et statistiques
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=5)
        
        ttk.Label(header_frame, text="Résultats de recherche", 
                 font=("Helvetica", 11, "bold")).pack(side="left")
        
        self.results_count_label = ttk.Label(header_frame, text="0 résultat(s)", 
                                            foreground="gray")
        self.results_count_label.pack(side="right")
        
        # Liste scrollable des résultats
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        results_scroll = ttk.Scrollbar(list_frame)
        results_scroll.pack(side="right", fill="y")
        
        # Treeview pour afficher les résultats en colonnes
        columns = ("Nom", "RA", "Dec", "Date", "Type", "Mag")
        self.results_tree = ttk.Treeview(list_frame, columns=columns, show="headings", 
                                        yscrollcommand=results_scroll.set, height=20)
        results_scroll.config(command=self.results_tree.yview)
        
        # Configuration des colonnes
        self.results_tree.heading("Nom", text="Nom")
        self.results_tree.heading("RA", text="RA (°)")
        self.results_tree.heading("Dec", text="Dec (°)")
        self.results_tree.heading("Date", text="Date découverte")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.heading("Mag", text="Mag")
        
        self.results_tree.column("Nom", width=150)
        self.results_tree.column("RA", width=100)
        self.results_tree.column("Dec", width=100)
        self.results_tree.column("Date", width=120)
        self.results_tree.column("Type", width=100)
        self.results_tree.column("Mag", width=80)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        
        # Sélection d'un élément
        self.results_tree.bind("<<TreeviewSelect>>", self.on_result_selected)
        self.results_tree.bind("<Double-Button-1>", lambda e: self.get_object_details())
        
        # Boutons d'action
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", pady=5)
        
        ttk.Button(action_frame, text="📋 Détails", 
                  command=self.get_object_details).pack(side="left", padx=2)
        ttk.Button(action_frame, text="⭐ Ajouter aux favoris", 
                  command=self.add_to_favorites).pack(side="left", padx=2)
        ttk.Button(action_frame, text="💾 Exporter CSV", 
                  command=self.export_results_csv).pack(side="left", padx=2)
        ttk.Button(action_frame, text="🔄 Actualiser", 
                  command=self.refresh_results).pack(side="left", padx=2)
    
    def create_details_section(self, parent):
        """Crée la section d'affichage des détails."""
        ttk.Label(parent, text="Détails de l'objet", 
                 font=("Helvetica", 11, "bold")).pack(pady=5)
        
        # Zone de texte scrollable pour les détails
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.details_text = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                                    wrap=tk.WORD, width=40, height=30)
        self.details_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.details_text.yview)
        
        # Boutons pour les détails
        details_btn_frame = ttk.Frame(parent)
        details_btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(details_btn_frame, text="📊 Photométrie", 
                  command=self.show_photometry).pack(side="left", padx=2)
        ttk.Button(details_btn_frame, text="📈 Spectres", 
                  command=self.show_spectra).pack(side="left", padx=2)
        ttk.Button(details_btn_frame, text="💾 Sauvegarder détails", 
                  command=self.save_details).pack(side="left", padx=2)
    
    def load_tns_config(self):
        """Charge la configuration TNS depuis config.py."""
        try:
            import config
            tns_config = getattr(config, 'TNS_CONFIG', {})
            self.tns_marker_type_var.set(tns_config.get('tns_marker_type', 'user'))
            self.tns_id_var.set(tns_config.get('tns_id', ''))
            self.tns_name_var.set(tns_config.get('tns_name', ''))
            self.tns_bot_id_var.set(tns_config.get('bot_id', ''))
            self.tns_bot_name_var.set(tns_config.get('bot_name', ''))
            self.tns_api_key_var.set(tns_config.get('api_key', ''))
        except Exception as e:
            logger.error(f"Erreur chargement config TNS: {e}")

    def save_tns_config(self):
        """Sauvegarde la configuration TNS dans config.py."""
        try:
            import config
            import importlib

            api_key = self.tns_api_key_var.get().strip()
            marker_type = (self.tns_marker_type_var.get() or "user").strip().lower()
            if marker_type not in ("user", "bot"):
                marker_type = "user"

            if marker_type == "bot" and not api_key:
                messagebox.showwarning("Attention", "En mode Bot, l'API Key est obligatoire.")
                return
            if marker_type == "user":
                tns_id = self.tns_id_var.get().strip()
                tns_name = self.tns_name_var.get().strip()
                if not tns_id or not tns_name:
                    messagebox.showwarning("Attention", "En mode User, remplissez TNS ID et Nom")
                    return
            else:
                bot_id = self.tns_bot_id_var.get().strip()
                if not bot_id:
                    messagebox.showwarning("Attention", "En mode Bot, remplissez le Bot ID")
                    return

            bot_name = self.tns_bot_name_var.get().strip() or "NPOAP"
            config.TNS_CONFIG = {
                "tns_marker_type": marker_type,
                "tns_id": self.tns_id_var.get().strip(),
                "tns_name": self.tns_name_var.get().strip(),
                "bot_id": self.tns_bot_id_var.get().strip(),
                "bot_name": bot_name,
                "api_key": api_key,
                "use_sandbox": False,
            }
            importlib.reload(config)

            if TNS_AVAILABLE:
                self.tns_client = TNSClient(
                    bot_id=config.TNS_CONFIG.get("bot_id"),
                    api_key=api_key,
                    bot_name=config.TNS_CONFIG.get("bot_name", "").strip() or "NPOAP",
                    use_sandbox=False,
                    tns_marker_type=marker_type,
                    tns_id=config.TNS_CONFIG.get("tns_id"),
                    tns_name=config.TNS_CONFIG.get("tns_name"),
                )

            messagebox.showinfo("Succès", "Configuration TNS sauvegardée")
        except Exception as e:
            logger.error(f"Erreur sauvegarde config TNS: {e}")
            messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")
    
    def reset_search_fields(self):
        """Réinitialise tous les champs de recherche."""
        self.tns_objname_var.set("")
        self.tns_ra_var.set("")
        self.tns_dec_var.set("")
        self.tns_radius_var.set("60")
        self.tns_date_start_var.set("")
        self.tns_date_end_var.set("")
        self.tns_mag_min_var.set("")
        self.tns_mag_max_var.set("")
    
    def search_tns(self):
        """Lance une recherche TNS."""
        if not TNS_AVAILABLE:
            messagebox.showerror("Erreur", "Client TNS non disponible")
            return

        # Utiliser les valeurs actuelles du formulaire
        marker_type = (self.tns_marker_type_var.get() or "user").strip().lower()
        if marker_type not in ("user", "bot"):
            marker_type = "user"
        api_key = (self.tns_api_key_var.get() or "").strip()
        if not api_key:
            messagebox.showwarning(
                "Attention",
                "L'API Search TNS exige une API Key.\n"
                "Mode Bot : utilisez la clé de votre bot.\n"
                "Mode User : utilisez une clé depuis My Account (wis-tns.org)."
            )
            return
        if marker_type == "user":
            tns_id = (self.tns_id_var.get() or "").strip()
            tns_name = (self.tns_name_var.get() or "").strip()
            if not tns_id or not tns_name:
                messagebox.showwarning("Attention", "En mode User, remplissez TNS ID et Nom.")
                return

        try:
            search_client = TNSClient(
                bot_id=(self.tns_bot_id_var.get() or "").strip() or None,
                api_key=api_key or None,
                bot_name=(self.tns_bot_name_var.get() or "").strip() or "NPOAP",
                use_sandbox=False,
                tns_marker_type=marker_type,
                tns_id=(self.tns_id_var.get() or "").strip() or None,
                tns_name=(self.tns_name_var.get() or "").strip() or None,
            )
        except Exception as e:
            logger.error(f"Erreur création client TNS: {e}")
            messagebox.showerror("Erreur", f"Impossible de créer le client TNS:\n{e}")
            return

        # Récupérer les critères de recherche
        objname = self.tns_objname_var.get().strip() or None
        ra = None
        dec = None
        radius = None
        date_start = None
        date_end = None
        mag_min = None
        mag_max = None
        
        try:
            ra_str = self.tns_ra_var.get().strip()
            dec_str = self.tns_dec_var.get().strip()
            radius_str = self.tns_radius_var.get().strip()
            
            if ra_str:
                ra = float(ra_str)
            if dec_str:
                dec = float(dec_str)
            if radius_str:
                radius = float(radius_str)
        except ValueError:
            messagebox.showerror("Erreur", "RA, Dec et Rayon doivent être numériques")
            return
        
        # Récupérer les dates
        date_start_str = self.tns_date_start_var.get().strip()
        date_end_str = self.tns_date_end_var.get().strip()
        
        if date_start_str:
            try:
                datetime.strptime(date_start_str, "%Y-%m-%d")
                date_start = date_start_str
            except ValueError:
                messagebox.showerror("Erreur", "Format de date début invalide. Utilisez YYYY-MM-DD (ex: 2024-01-15)")
                return
        
        if date_end_str:
            try:
                datetime.strptime(date_end_str, "%Y-%m-%d")
                date_end = date_end_str
            except ValueError:
                messagebox.showerror("Erreur", "Format de date fin invalide. Utilisez YYYY-MM-DD (ex: 2024-01-15)")
                return
        
        # Récupérer les magnitudes
        try:
            mag_min_str = self.tns_mag_min_var.get().strip()
            mag_max_str = self.tns_mag_max_var.get().strip()
            
            if mag_min_str:
                mag_min = float(mag_min_str)
            if mag_max_str:
                mag_max = float(mag_max_str)
        except ValueError:
            messagebox.showerror("Erreur", "Les magnitudes doivent être numériques")
            return
        
        # Vérifier qu'au moins un critère est fourni
        if not objname and (ra is None or dec is None) and not date_start and not date_end:
            messagebox.showwarning("Attention", "Indiquez au moins un critère :\n- Nom d'objet\n- Coordonnées (RA/Dec)\n- Date de découverte")
            return
        
        # Lancer la recherche dans un thread (client = formulaire)
        Thread(target=self._search_tns_task,
               args=(search_client, objname, ra, dec, radius, date_start, date_end, mag_min, mag_max),
               daemon=True).start()

    def _search_tns_task(self, client, objname, ra, dec, radius, date_start, date_end, mag_min, mag_max):
        """Tâche de recherche TNS en arrière-plan."""
        try:
            results = client.search_objects(
                objname=objname,
                ra=ra,
                dec=dec,
                radius=radius,
                radius_units="arcsec",
                discovery_date_start=date_start,
                discovery_date_end=date_end,
                discovery_mag_min=mag_min,
                discovery_mag_max=mag_max
            )
            
            if results:
                self.search_results = results
                self.after(0, self.display_results)
            else:
                self.after(0, lambda: messagebox.showinfo("Info", "Aucun résultat trouvé"))
        except TNSUnauthorizedError as e:
            logger.error(f"TNS 401 Unauthorized: {e}")
            self.after(0, lambda: messagebox.showerror(
                "TNS – Authentification refusée (401)",
                "L'API TNS a refusé la requête (401 Unauthorized).\n\n"
                "À vérifier :\n"
                "• Mode BOT : Bot ID = le numéro (tns_id) sur la page d'édition du bot (wis-tns.org/bots → votre bot), pas le Name ni le Survey name.\n"
                "• Mode USER : TNS ID et Nom exact de votre compte.\n"
                "• Search/Get exigent une API Key (mode Bot ou User avec clé depuis My Account).\n"
                "• Environnement : Production (pas Sandbox) pour les vrais objets.\n\n"
                "Sauvegardez la config après toute modification."
            ))
        except Exception as e:
            logger.error(f"Erreur recherche TNS: {e}", exc_info=True)
            self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur recherche TNS:\n{e}"))
    
    def display_results(self):
        """Affiche les résultats de recherche dans le Treeview."""
        # Effacer les résultats précédents
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Afficher les nouveaux résultats
        for obj in self.search_results:
            objname = obj.get('objname', 'N/A')
            ra = obj.get('ra', {})
            if isinstance(ra, dict):
                ra = ra.get('value', 'N/A')
            else:
                ra = str(ra) if ra is not None else 'N/A'
            
            dec = obj.get('dec', {})
            if isinstance(dec, dict):
                dec = dec.get('value', 'N/A')
            else:
                dec = str(dec) if dec is not None else 'N/A'
            
            disc_date = obj.get('discoverydate', 'N/A')
            obj_type = obj.get('objtype', {}).get('name', 'N/A') if isinstance(obj.get('objtype'), dict) else 'N/A'
            disc_mag = obj.get('discoverymag', 'N/A')
            
            self.results_tree.insert("", tk.END, values=(objname, ra, dec, disc_date, obj_type, disc_mag))
        
        # Mettre à jour le compteur
        count = len(self.search_results)
        self.results_count_label.config(text=f"{count} résultat(s)")
    
    def refresh_results(self):
        """Rafraîchit l'affichage des résultats."""
        if self.search_results:
            self.display_results()
    
    def on_result_selected(self, event):
        """Appelé quand un résultat est sélectionné."""
        selection = self.results_tree.selection()
        if selection:
            # Récupérer automatiquement les détails
            self.get_object_details()
    
    def get_object_details(self):
        """Récupère les détails d'un objet sélectionné."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un objet dans la liste")
            return
        
        item = self.results_tree.item(selection[0])
        objname = item['values'][0]  # Le nom est dans la première colonne
        
        if not objname or objname == 'N/A':
            messagebox.showerror("Erreur", "Nom d'objet invalide")
            return
        
        # Récupérer les détails dans un thread
        Thread(target=self._get_details_task, args=(objname,), daemon=True).start()
    
    def _get_details_task(self, objname):
        """Récupère les détails d'un objet TNS en arrière-plan."""
        try:
            details = self.tns_client.get_object(objname, photometry=True, spectra=False)
            
            if details:
                self.current_object_details = details
                # Afficher les détails
                self.after(0, lambda: self.display_details(objname, details))
            else:
                self.after(0, lambda: messagebox.showinfo("Info", f"Aucun détail trouvé pour {objname}"))
        except Exception as e:
            logger.error(f"Erreur récupération détails TNS: {e}", exc_info=True)
            self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur récupération détails:\n{e}"))
    
    def display_details(self, objname, details):
        """Affiche les détails d'un objet dans la zone de texte."""
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        
        # Formater les détails de manière lisible
        details_text = f"=== Détails TNS: {objname} ===\n\n"
        
        # Informations de base
        if 'objname' in details:
            details_text += f"Nom: {details.get('objname', 'N/A')}\n"
        if 'ra' in details:
            ra = details['ra']
            if isinstance(ra, dict):
                details_text += f"RA: {ra.get('value', 'N/A')}°\n"
            else:
                details_text += f"RA: {ra}°\n"
        if 'dec' in details:
            dec = details['dec']
            if isinstance(dec, dict):
                details_text += f"Dec: {dec.get('value', 'N/A')}°\n"
            else:
                details_text += f"Dec: {dec}°\n"
        if 'discoverydate' in details:
            details_text += f"Date de découverte: {details.get('discoverydate', 'N/A')}\n"
        if 'discoverymag' in details:
            details_text += f"Magnitude de découverte: {details.get('discoverymag', 'N/A')}\n"
        if 'objtype' in details:
            objtype = details['objtype']
            if isinstance(objtype, dict):
                details_text += f"Type: {objtype.get('name', 'N/A')}\n"
            else:
                details_text += f"Type: {objtype}\n"
        if 'redshift' in details:
            details_text += f"Redshift: {details.get('redshift', 'N/A')}\n"
        
        details_text += "\n=== Données complètes (JSON) ===\n\n"
        details_text += json.dumps(details, indent=2, ensure_ascii=False)
        
        self.details_text.insert("1.0", details_text)
        self.details_text.config(state="disabled")
    
    def add_to_favorites(self):
        """Ajoute l'objet sélectionné aux favoris."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un objet dans la liste")
            return
        
        item = self.results_tree.item(selection[0])
        objname = item['values'][0]
        
        if objname and objname != 'N/A':
            if objname not in self.followed_objects:
                self.followed_objects.append(objname)
                messagebox.showinfo("Succès", f"{objname} ajouté aux favoris")
            else:
                messagebox.showinfo("Info", f"{objname} est déjà dans les favoris")
    
    def export_results_csv(self):
        """Exporte les résultats en CSV."""
        if not self.search_results:
            messagebox.showwarning("Attention", "Aucun résultat à exporter")
            return
        
        output_path = filedialog.asksaveasfilename(
            initialdir=self.base_dir,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        
        if not output_path:
            return
        
        try:
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # En-têtes
                writer.writerow(["Nom", "RA", "Dec", "Date découverte", "Type", "Magnitude"])
                
                # Données
                for obj in self.search_results:
                    objname = obj.get('objname', 'N/A')
                    ra = obj.get('ra', {})
                    if isinstance(ra, dict):
                        ra = ra.get('value', 'N/A')
                    else:
                        ra = str(ra) if ra is not None else 'N/A'
                    
                    dec = obj.get('dec', {})
                    if isinstance(dec, dict):
                        dec = dec.get('value', 'N/A')
                    else:
                        dec = str(dec) if dec is not None else 'N/A'
                    
                    disc_date = obj.get('discoverydate', 'N/A')
                    obj_type = obj.get('objtype', {}).get('name', 'N/A') if isinstance(obj.get('objtype'), dict) else 'N/A'
                    disc_mag = obj.get('discoverymag', 'N/A')
                    
                    writer.writerow([objname, ra, dec, disc_date, obj_type, disc_mag])
            
            messagebox.showinfo("Succès", f"Résultats exportés vers:\n{output_path}")
        except Exception as e:
            logger.error(f"Erreur export CSV: {e}", exc_info=True)
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")
    
    def show_photometry(self):
        """Affiche les données photométriques de l'objet."""
        if not self.current_object_details:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un objet et chargez ses détails")
            return
        
        photometry = self.current_object_details.get('photometry', {})
        if not photometry:
            messagebox.showinfo("Info", "Aucune donnée photométrique disponible")
            return
        
        # Afficher dans une fenêtre séparée
        phot_window = tk.Toplevel(self)
        phot_window.title("Photométrie")
        phot_window.geometry("800x600")
        
        text_frame = ttk.Frame(phot_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        phot_text = json.dumps(photometry, indent=2, ensure_ascii=False)
        text_widget.insert("1.0", phot_text)
        text_widget.config(state="disabled")
    
    def show_spectra(self):
        """Affiche les données spectrales de l'objet."""
        if not self.current_object_details:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un objet et chargez ses détails")
            return
        
        # Pour les spectres, il faudrait récupérer avec spectra=True
        messagebox.showinfo("Info", "Fonctionnalité à implémenter: récupération des spectres")
    
    def save_details(self):
        """Sauvegarde les détails de l'objet dans un fichier JSON."""
        if not self.current_object_details:
            messagebox.showwarning("Attention", "Aucun détail à sauvegarder")
            return
        
        output_path = filedialog.asksaveasfilename(
            initialdir=self.base_dir,
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        
        if not output_path:
            return
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_object_details, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Succès", f"Détails sauvegardés vers:\n{output_path}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde détails: {e}", exc_info=True)
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
