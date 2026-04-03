"""
Onglet GUI pour la détection de sources et l'extraction de courbes de lumière
utilisant le pipeline SPDE (Synchronous Photometry Data Extraction).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import logging
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from astropy.coordinates import SkyCoord
import astropy.units as u

try:
    from core.spde_pipeline import SPDEPipeline
    SPDE_AVAILABLE = True
except ImportError as e:
    SPDE_AVAILABLE = False
    logger.warning(f"SPDE non disponible : {e}")

try:
    from core.lca_analysis import LCAAnalysis
    LCA_AVAILABLE = True
except ImportError as e:
    LCA_AVAILABLE = False
    logger.warning(f"LCA non disponible : {e}")

logger = logging.getLogger(__name__)


class ToolTip:
    """Classe pour créer des tooltips."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self._id1 = self.widget.bind("<Enter>", self.enter)
        self._id2 = self.widget.bind("<Leave>", self.leave)
        self._id3 = self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("TkDefaultFont", 9), wraplength=300)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class SourceDetectionTab:
    """
    Onglet pour la détection automatique de sources et l'extraction de courbes de lumière.
    """
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
        self.pipeline = None
        self.results = None
        self.light_curves = {}
        
    def create_widgets(self):
        """Crée l'interface utilisateur."""
        
        # Panneau principal avec séparateur
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panneau gauche : Paramètres et contrôles
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Panneau droit : Résultats et visualisation
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # ===== PANneau GAUCHE : Paramètres =====
        
        # Section 1 : Sélection des fichiers
        files_frame = ttk.LabelFrame(left_frame, text="1. Sélection des Fichiers", padding=10)
        files_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(files_frame, text="Dossier des images FITS :").pack(anchor=tk.W)
        files_path_frame = ttk.Frame(files_frame)
        files_path_frame.pack(fill=tk.X, pady=2)
        self.fits_folder = tk.StringVar()
        ttk.Entry(files_path_frame, textvariable=self.fits_folder, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(files_path_frame, text="Parcourir", command=self.browse_fits_folder).pack(side=tk.LEFT, padx=5)
        
        # Section 2 : Calibration
        calib_frame = ttk.LabelFrame(left_frame, text="2. Calibration (Optionnel)", padding=10)
        calib_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.apply_dark = tk.BooleanVar(value=False)
        ttk.Checkbutton(calib_frame, text="Appliquer soustraction de dark", 
                        variable=self.apply_dark).pack(anchor=tk.W)
        
        dark_frame = ttk.Frame(calib_frame)
        dark_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dark_frame, text="Fichier dark :").pack(anchor=tk.W)
        dark_path_frame = ttk.Frame(dark_frame)
        dark_path_frame.pack(fill=tk.X)
        self.dark_path = tk.StringVar()
        ttk.Entry(dark_path_frame, textvariable=self.dark_path, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dark_path_frame, text="...", command=self.browse_dark, width=3).pack(side=tk.LEFT, padx=2)
        
        self.apply_flat = tk.BooleanVar(value=False)
        ttk.Checkbutton(calib_frame, text="Appliquer correction de flat-field", 
                        variable=self.apply_flat).pack(anchor=tk.W, pady=(5, 0))
        
        flat_frame = ttk.Frame(calib_frame)
        flat_frame.pack(fill=tk.X, pady=2)
        ttk.Label(flat_frame, text="Fichier flat :").pack(anchor=tk.W)
        flat_path_frame = ttk.Frame(flat_frame)
        flat_path_frame.pack(fill=tk.X)
        self.flat_path = tk.StringVar()
        ttk.Entry(flat_path_frame, textvariable=self.flat_path, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(flat_path_frame, text="...", command=self.browse_flat, width=3).pack(side=tk.LEFT, padx=2)
        
        # Section 3 : Paramètres SPDE
        params_frame = ttk.LabelFrame(left_frame, text="3. Paramètres SPDE", padding=10)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Info générale SPDE
        spde_info = ttk.Label(params_frame, 
                             text="Pipeline d'extraction automatique de courbes de lumière\n"
                                  "basé sur Dai et al. (2023) - 5 étapes: Classification, Pre-processing,\n"
                                  "Quality justification, Matching, Photométrie",
                             font=("TkDefaultFont", 7), foreground="gray", justify=tk.LEFT)
        spde_info.pack(anchor=tk.W, pady=(0, 8))
        
        # Sigma
        sigma_row = ttk.Frame(params_frame)
        sigma_row.pack(fill=tk.X, pady=2)
        sigma_label = ttk.Label(sigma_row, text="Sigma (soustraction fond) :", width=25)
        sigma_label.pack(side=tk.LEFT)
        self.sigma = tk.DoubleVar(value=3.0)
        sigma_spinbox = ttk.Spinbox(sigma_row, from_=1.0, to=10.0, increment=0.5, 
                   textvariable=self.sigma, width=10)
        sigma_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(sigma_spinbox, "Paramètre σ pour le clipping sigma lors de la soustraction du fond.\n"
                              "Utilisé par Background2D (DAOPHOT).\n"
                              "Valeurs typiques: 3.0 (par défaut). Plus élevé = fond plus conservateur.")
        
        # FWHM
        fwhm_row = ttk.Frame(params_frame)
        fwhm_row.pack(fill=tk.X, pady=2)
        fwhm_label = ttk.Label(fwhm_row, text="FWHM (pixels) :", width=25)
        fwhm_label.pack(side=tk.LEFT)
        self.fwhm = tk.DoubleVar(value=3.0)
        fwhm_spinbox = ttk.Spinbox(fwhm_row, from_=1.0, to=10.0, increment=0.5, 
                   textvariable=self.fwhm, width=10)
        fwhm_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(fwhm_spinbox, "Largeur à mi-hauteur (Full Width at Half Maximum) des étoiles en pixels.\n"
                             "Paramètre utilisé par DAOStarFinder pour la détection.\n"
                             "Doit correspondre au seeing réel de vos images.\n"
                             "Typique: 2-4 pixels pour petits télescopes, 3-6 pour moyens.")
        
        # Threshold
        threshold_row = ttk.Frame(params_frame)
        threshold_row.pack(fill=tk.X, pady=2)
        threshold_label = ttk.Label(threshold_row, text="Seuil de détection :", width=25)
        threshold_label.pack(side=tk.LEFT)
        self.threshold = tk.DoubleVar(value=5.0)
        threshold_spinbox = ttk.Spinbox(threshold_row, from_=1.0, to=50.0, increment=1.0, 
                   textvariable=self.threshold, width=10)
        threshold_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(threshold_spinbox, "Seuil de détection en multiples de l'écart-type du bruit.\n"
                                  "Définit le minimum de flux pour qu'une source soit détectée.\n"
                                  "Seuil = threshold × σ_bruit. Plus élevé = moins de fausses détections.\n"
                                  "Typique: 5.0 (par défaut). Réduire à 3-4 pour images profondes.")
        
        # N brightest
        nbrightest_row = ttk.Frame(params_frame)
        nbrightest_row.pack(fill=tk.X, pady=2)
        nbrightest_label = ttk.Label(nbrightest_row, text="N étoiles brillantes :", width=25)
        nbrightest_label.pack(side=tk.LEFT)
        self.n_brightest = tk.IntVar(value=50)
        nbrightest_spinbox = ttk.Spinbox(nbrightest_row, from_=10, to=200, increment=10, 
                   textvariable=self.n_brightest, width=10)
        nbrightest_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(nbrightest_spinbox, "Nombre d'étoiles les plus brillantes utilisées pour le matching.\n"
                                   "Ces étoiles servent à trouver le triangle de repères et à aligner les images.\n"
                                   "Plus élevé = matching plus robuste mais plus lent.\n"
                                   "Recommandé: 30-100. 50 est un bon compromis.")
        
        # Section 4 : Paramètres LCA
        lca_frame = ttk.LabelFrame(left_frame, text="4. Paramètres LCA", padding=10)
        lca_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Info générale LCA
        lca_info = ttk.Label(lca_frame, 
                            text="Analyse des courbes de lumière pour détecter et classer\n"
                                 "les étoiles variables (périodiques, transitoires, particulières)",
                            font=("TkDefaultFont", 7), foreground="gray", justify=tk.LEFT)
        lca_info.pack(anchor=tk.W, pady=(0, 8))
        
        # St threshold
        st_row = ttk.Frame(lca_frame)
        st_row.pack(fill=tk.X, pady=2)
        st_label = ttk.Label(st_row, text="Seuil St (variabilité) :", width=25)
        st_label.pack(side=tk.LEFT)
        self.st_threshold = tk.DoubleVar(value=0.01)
        st_spinbox = ttk.Spinbox(st_row, from_=0.001, to=0.1, increment=0.001, 
                   textvariable=self.st_threshold, width=10, format="%.3f")
        st_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(st_spinbox, "Index de variabilité St = σ(flux) / μ(flux)\n"
                           "Mesure la variabilité relative d'une courbe de lumière.\n"
                           "St > seuil → étoile considérée comme variable.\n"
                           "Typique: 0.01 (1% de variation). Augmenter pour détecter moins de variables.")
        
        # Min amplitude
        amp_row = ttk.Frame(lca_frame)
        amp_row.pack(fill=tk.X, pady=2)
        amp_label = ttk.Label(amp_row, text="Amplitude minimale :", width=25)
        amp_label.pack(side=tk.LEFT)
        self.min_amplitude = tk.DoubleVar(value=0.005)
        amp_spinbox = ttk.Spinbox(amp_row, from_=0.001, to=0.1, increment=0.001, 
                   textvariable=self.min_amplitude, width=10, format="%.3f")
        amp_spinbox.pack(side=tk.LEFT, padx=5)
        ToolTip(amp_spinbox, "Amplitude minimale = (flux_max - flux_min) / flux_moyen\n"
                            "Variation minimale en amplitude pour considérer une étoile comme variable.\n"
                            "Typique: 0.005 (0.5% d'amplitude).\n"
                            "Réduire pour détecter des variations plus subtiles.")
        
        # Boutons d'action
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(action_frame, text="🚀 Lancer Pipeline SPDE", 
                  command=self.run_pipeline, width=25).pack(pady=5)
        ttk.Button(action_frame, text="📊 Analyser Courbes (LCA)", 
                  command=self.run_lca_analysis, width=25).pack(pady=5)
        ttk.Button(action_frame, text="💾 Exporter Résultats", 
                  command=self.export_results, width=25).pack(pady=5)
        ttk.Button(action_frame, text="🖼️ Sauvegarder Image Référence", 
                  command=self.save_reference_image, width=25).pack(pady=5)
        
        # Barre de progression
        self.progress = ttk.Progressbar(left_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # ===== PANneau DROIT : Résultats =====
        
        # Notebook pour organiser les résultats
        results_notebook = ttk.Notebook(right_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 1 : Logs
        log_frame = ttk.Frame(results_notebook)
        results_notebook.add(log_frame, text="📝 Logs")
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Onglet 2 : Courbes de lumière
        lc_frame = ttk.Frame(results_notebook)
        results_notebook.add(lc_frame, text="📈 Courbes de Lumière")
        
        lc_control_frame = ttk.Frame(lc_frame)
        lc_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(lc_control_frame, text="Étoile à afficher :").pack(side=tk.LEFT, padx=5)
        self.star_selector = ttk.Combobox(lc_control_frame, width=20, state='readonly')
        self.star_selector.pack(side=tk.LEFT, padx=5)
        self.star_selector.bind('<<ComboboxSelected>>', self.plot_light_curve)
        
        ttk.Button(lc_control_frame, text="Afficher toutes", 
                  command=self.plot_all_light_curves).pack(side=tk.LEFT, padx=5)
        
        self.lc_figure = Figure(figsize=(10, 6))
        self.lc_canvas = FigureCanvasTkAgg(self.lc_figure, lc_frame)
        self.lc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.lc_toolbar = NavigationToolbar2Tk(self.lc_canvas, lc_frame)
        self.lc_toolbar.update()
        
        # Onglet 3 : Variables détectées
        vars_frame = ttk.Frame(results_notebook)
        results_notebook.add(vars_frame, text="⭐ Variables")
        
        vars_control_frame = ttk.Frame(vars_frame)
        vars_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(vars_control_frame, text="Type :").pack(side=tk.LEFT, padx=5)
        self.var_type_filter = ttk.Combobox(vars_control_frame, 
                                           values=['Toutes', 'Périodiques', 'Transitoires', 'Particulières'],
                                           width=15, state='readonly')
        self.var_type_filter.set('Toutes')
        self.var_type_filter.pack(side=tk.LEFT, padx=5)
        self.var_type_filter.bind('<<ComboboxSelected>>', self.update_variables_list)
        
        self.vars_listbox = tk.Listbox(vars_frame, height=15)
        self.vars_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.vars_listbox.bind('<<ListboxSelect>>', self.on_variable_selected)
        
        # Onglet 4 : Rapport
        report_frame = ttk.Frame(results_notebook)
        results_notebook.add(report_frame, text="📄 Rapport")
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_fits_folder(self):
        """Ouvre un dialogue pour sélectionner le dossier des images FITS."""
        folder = filedialog.askdirectory(title="Sélectionner le dossier des images FITS")
        if folder:
            self.fits_folder.set(folder)
    
    def browse_dark(self):
        """Ouvre un dialogue pour sélectionner le fichier dark."""
        file = filedialog.askopenfilename(
            title="Sélectionner le fichier dark",
            filetypes=[("FITS files", "*.fits"), ("All files", "*.*")]
        )
        if file:
            self.dark_path.set(file)
    
    def browse_flat(self):
        """Ouvre un dialogue pour sélectionner le fichier flat."""
        file = filedialog.askopenfilename(
            title="Sélectionner le fichier flat",
            filetypes=[("FITS files", "*.fits"), ("All files", "*.*")]
        )
        if file:
            self.flat_path.set(file)
    
    def log_message(self, message: str):
        """Ajoute un message au log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.frame.update()
    
    def run_pipeline(self):
        """Lance le pipeline SPDE dans un thread séparé."""
        if not self.fits_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier d'images FITS")
            return
        
        folder = Path(self.fits_folder.get())
        fits_files = sorted(folder.glob("*.fits"))
        
        if len(fits_files) == 0:
            messagebox.showerror("Erreur", "Aucun fichier FITS trouvé dans le dossier sélectionné")
            return
        
        # Démarrer le pipeline dans un thread
        thread = threading.Thread(target=self._run_pipeline_thread, args=(fits_files,))
        thread.daemon = True
        thread.start()
    
    def _run_pipeline_thread(self, fits_files):
        """Exécute le pipeline SPDE dans un thread séparé."""
        try:
            self.progress.start()
            self.log_message(f"Démarrage du pipeline SPDE sur {len(fits_files)} fichiers...")
            
            # Initialiser le pipeline
            if not SPDE_AVAILABLE:
                raise ImportError("Le module SPDE n'est pas disponible")
            self.pipeline = SPDEPipeline(
                sigma=self.sigma.get(),
                fwhm=self.fwhm.get(),
                threshold=self.threshold.get(),
                n_max_brightest=self.n_brightest.get()
            )
            
            # Préparer les chemins dark/flat
            dark_path = Path(self.dark_path.get()) if self.apply_dark.get() and self.dark_path.get() else None
            flat_path = Path(self.flat_path.get()) if self.apply_flat.get() and self.flat_path.get() else None
            
            # Exécuter le pipeline
            self.results = self.pipeline.run_full_pipeline(
                fits_files,
                apply_dark=self.apply_dark.get(),
                apply_flat=self.apply_flat.get(),
                dark_path=dark_path,
                flat_path=flat_path
            )
            
            self.light_curves = self.results['light_curves']
            
            # Mettre à jour l'interface
            self.frame.after(0, self._pipeline_finished)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du pipeline : {e}", exc_info=True)
            self.frame.after(0, lambda: messagebox.showerror("Erreur", f"Erreur pipeline : {e}"))
        finally:
            self.frame.after(0, self.progress.stop)
    
    def _pipeline_finished(self):
        """Appelé lorsque le pipeline est terminé."""
        self.log_message(f"Pipeline terminé : {self.results['n_stars']} courbes de lumière extraites")
        
        # Mettre à jour le sélecteur d'étoiles
        star_ids = list(self.light_curves.keys())
        self.star_selector['values'] = star_ids
        if star_ids:
            self.star_selector.set(star_ids[0])
            self.plot_light_curve()
        
        messagebox.showinfo("Succès", 
                          f"Pipeline SPDE terminé avec succès !\n"
                          f"- {self.results['n_images']} images traitées\n"
                          f"- {self.results['n_stars']} courbes de lumière extraites")
    
    def plot_light_curve(self, event=None):
        """Affiche la courbe de lumière de l'étoile sélectionnée."""
        star_id = self.star_selector.get()
        if not star_id or star_id not in self.light_curves:
            return
        
        lc_data = self.light_curves[star_id]
        time = lc_data['time']
        flux = lc_data['flux']
        
        self.lc_figure.clear()
        ax = self.lc_figure.add_subplot(111)
        ax.plot(time, flux, 'b.-', markersize=3)
        ax.set_xlabel('Temps (JD)')
        ax.set_ylabel('Flux (ADU)')
        ax.set_title(f'Courbe de lumière : {star_id}')
        ax.grid(True, alpha=0.3)
        self.lc_figure.tight_layout()
        self.lc_canvas.draw()
    
    def plot_all_light_curves(self):
        """Affiche toutes les courbes de lumière."""
        if not self.light_curves:
            messagebox.showwarning("Avertissement", "Aucune courbe de lumière disponible")
            return
        
        self.lc_figure.clear()
        ax = self.lc_figure.add_subplot(111)
        
        for star_id, lc_data in self.light_curves.items():
            time = lc_data['time']
            flux = lc_data['flux']
            # Normaliser pour la visualisation
            flux_norm = (flux - np.mean(flux)) / np.std(flux) if np.std(flux) > 0 else flux
            ax.plot(time, flux_norm, '.-', markersize=2, alpha=0.5, label=star_id)
        
        ax.set_xlabel('Temps (JD)')
        ax.set_ylabel('Flux normalisé')
        ax.set_title('Toutes les courbes de lumière')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=6, ncol=2)
        self.lc_figure.tight_layout()
        self.lc_canvas.draw()
    
    def run_lca_analysis(self):
        """Lance l'analyse LCA dans un thread séparé."""
        if not self.light_curves:
            messagebox.showerror("Erreur", "Veuillez d'abord exécuter le pipeline SPDE")
            return
        
        thread = threading.Thread(target=self._run_lca_thread)
        thread.daemon = True
        thread.start()
    
    def _run_lca_thread(self):
        """Exécute l'analyse LCA dans un thread séparé."""
        try:
            self.progress.start()
            self.log_message("Démarrage de l'analyse LCA...")
            
            # Initialiser l'analyseur LCA
            if not LCA_AVAILABLE:
                raise ImportError("Le module LCA n'est pas disponible")
            lca = LCAAnalysis(
                st_threshold=self.st_threshold.get(),
                min_amplitude=self.min_amplitude.get()
            )
            
            # Détecter les variables
            variables = lca.detect_variability(self.light_curves)
            self.log_message(f"{len(variables)} étoiles variables détectées")
            
            # Classifier
            classifications = lca.classify_variables(self.light_curves, variables)
            
            # Extraire les coordonnées des étoiles variables
            star_coordinates = {}
            if hasattr(self, 'results') and self.results and 'reference_stars' in self.results:
                ref_stars = self.results['reference_stars']
                for var in variables:
                    star_id = var['star_id']
                    # Extraire l'index depuis l'ID (format: star_XXXX)
                    try:
                        star_idx = int(star_id.split('_')[1])
                        if star_idx < len(ref_stars):
                            star = ref_stars[star_idx]
                            if 'ra' in star.colnames and 'dec' in star.colnames:
                                star_coordinates[star_id] = {
                                    'ra': float(star['ra']),
                                    'dec': float(star['dec'])
                                }
                    except (ValueError, IndexError):
                        pass
            
            # Générer le rapport avec coordonnées
            report = lca.generate_report(self.light_curves, classifications, 
                                        star_coordinates=star_coordinates)
            
            # Mettre à jour l'interface
            self.frame.after(0, lambda: self._lca_finished(lca, classifications, report, star_coordinates))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse LCA : {e}", exc_info=True)
            self.frame.after(0, lambda: messagebox.showerror("Erreur", f"Erreur LCA : {e}"))
        finally:
            self.frame.after(0, self.progress.stop)
    
    def _lca_finished(self, lca, classifications, report, star_coordinates=None):
        """Appelé lorsque l'analyse LCA est terminée."""
        self.lca_analysis = lca
        self.classifications = classifications
        self.star_coordinates = star_coordinates or {}
        
        # Mettre à jour le rapport
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
        
        # Mettre à jour la liste des variables
        self.update_variables_list()
        
        self.log_message("Analyse LCA terminée")
        messagebox.showinfo("Succès", "Analyse LCA terminée avec succès !")
    
    def update_variables_list(self, event=None):
        """Met à jour la liste des variables selon le filtre."""
        if not hasattr(self, 'classifications'):
            return
        
        filter_type = self.var_type_filter.get()
        self.vars_listbox.delete(0, tk.END)
        
        if filter_type == 'Toutes':
            all_vars = (self.classifications['periodic'] + 
                        self.classifications['transient'] + 
                        self.classifications['peculiar'])
        elif filter_type == 'Périodiques':
            all_vars = self.classifications['periodic']
        elif filter_type == 'Transitoires':
            all_vars = self.classifications['transient']
        elif filter_type == 'Particulières':
            all_vars = self.classifications['peculiar']
        else:
            all_vars = []
        
        for var in all_vars:
            star_id = var['star_id']
            st = var['st']
            amp = var['amplitude']
            var_type = var.get('type', 'unknown')
            period = var.get('period', None)
            
            if period:
                text = f"{star_id} | {var_type} | St={st:.4f} | Amp={amp:.4f} | P={period:.2f}j"
            else:
                text = f"{star_id} | {var_type} | St={st:.4f} | Amp={amp:.4f}"
            
            self.vars_listbox.insert(tk.END, text)
    
    def on_variable_selected(self, event):
        """Appelé lorsqu'une variable est sélectionnée."""
        selection = self.vars_listbox.curselection()
        if not selection:
            return
        
        # Extraire l'ID de l'étoile depuis le texte
        text = self.vars_listbox.get(selection[0])
        star_id = text.split(' | ')[0]
        
        # Afficher la courbe de lumière
        if star_id in self.light_curves:
            self.star_selector.set(star_id)
            self.plot_light_curve()
    
    def export_results(self):
        """Exporte les résultats."""
        if not self.results:
            messagebox.showerror("Erreur", "Aucun résultat à exporter")
            return
        
        # Demander où sauvegarder
        file = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".npz",
            filetypes=[("NumPy archive", "*.npz"), ("All files", "*.*")]
        )
        
        if file:
            try:
                np.savez_compressed(
                    file,
                    light_curves=self.light_curves,
                    results=self.results
                )
                messagebox.showinfo("Succès", f"Résultats exportés vers {file}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")
    
    def save_reference_image(self):
        """Sauvegarde l'image de référence avec les étoiles marquées."""
        if not self.pipeline or not self.results:
            messagebox.showerror("Erreur", "Veuillez d'abord exécuter le pipeline SPDE")
            return
        
        # Demander où sauvegarder
        file = filedialog.asksaveasfilename(
            title="Sauvegarder l'image de référence annotée",
            defaultextension=".fits",
            filetypes=[("FITS files", "*.fits"), ("All files", "*.*")]
        )
        
        if file:
            try:
                # Extraire les IDs des étoiles variables
                variable_star_ids = []
                if hasattr(self, 'classifications') and self.classifications:
                    for var_type in ['periodic', 'transient', 'peculiar']:
                        for var in self.classifications.get(var_type, []):
                            variable_star_ids.append(var['star_id'])
                
                # Sauvegarder l'image annotée
                ref_image_path = self.results.get('reference_image')
                if not ref_image_path:
                    messagebox.showerror("Erreur", "Chemin de l'image de référence non disponible")
                    return
                
                self.pipeline.save_annotated_reference_image(
                    Path(file),
                    reference_image_path=Path(ref_image_path),
                    variable_star_ids=variable_star_ids if variable_star_ids else None,
                    mark_all_stars=True
                )
                
                messagebox.showinfo("Succès", 
                                  f"Image de référence annotée sauvegardée : {file}\n\n"
                                  f"Cette image peut être ouverte dans Aladin pour analyse avec les catalogues.")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde de l'image : {e}", exc_info=True)
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")
