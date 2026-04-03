"""
Wrapper pour STDPipe - Simple Transient Detection Pipeline
Encapsule les fonctionnalités principales de STDPipe pour l'analyse de transitoires.

Référence: https://stdpipe.readthedocs.io/
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import warnings

logger = logging.getLogger(__name__)

# Import STDPipe avec gestion des erreurs
STDPIPE_AVAILABLE = False
STDPIPE_ERROR = None

# Variables pour les sous-modules (initialisées à None)
stdpipe = None
cutouts = None
stdpipe_astrometry = None
stdpipe_photometry = None
stdpipe_subtraction = None
stdpipe_catalogues = None

try:
    import stdpipe
    logger.info(f"Module stdpipe importé avec succès")
    
    # Importer les sous-modules de manière optionnelle
    # Les modules essentiels
    try:
        from stdpipe import cutouts
        logger.debug("Module stdpipe.cutouts importé")
    except ImportError as e:
        logger.warning(f"Impossible d'importer stdpipe.cutouts: {e}")
    
    try:
        from stdpipe import astrometry as stdpipe_astrometry
        logger.debug("Module stdpipe.astrometry importé")
    except ImportError as e:
        logger.warning(f"Impossible d'importer stdpipe.astrometry: {e}")
    
    try:
        from stdpipe import photometry as stdpipe_photometry
        logger.debug("Module stdpipe.photometry importé")
    except ImportError as e:
        logger.warning(f"Impossible d'importer stdpipe.photometry: {e}")
    
    try:
        from stdpipe import subtraction as stdpipe_subtraction
        logger.debug("Module stdpipe.subtraction importé")
    except ImportError as e:
        logger.warning(f"Impossible d'importer stdpipe.subtraction: {e}")
    
    # Module optionnel (pour téléchargement d'images de référence)
    try:
        from stdpipe import catalogues as stdpipe_catalogues
        logger.debug("Module stdpipe.catalogues importé")
    except ImportError as e:
        logger.info(f"Module stdpipe.catalogues non disponible (optionnel): {e}")
        stdpipe_catalogues = None
    
    # STDPipe est disponible si au moins le module principal est importé
    # et si au moins un sous-module essentiel est disponible
    if stdpipe and (cutouts or stdpipe_astrometry or stdpipe_photometry or stdpipe_subtraction):
        STDPIPE_AVAILABLE = True
        available_modules = []
        if cutouts: available_modules.append("cutouts")
        if stdpipe_astrometry: available_modules.append("astrometry")
        if stdpipe_photometry: available_modules.append("photometry")
        if stdpipe_subtraction: available_modules.append("subtraction")
        if stdpipe_catalogues: available_modules.append("catalogues")
        logger.info(f"STDPipe disponible avec modules: {', '.join(available_modules)}")
    else:
        STDPIPE_AVAILABLE = False
        STDPIPE_ERROR = "STDPipe importé mais aucun sous-module essentiel n'est disponible"
        logger.warning(STDPIPE_ERROR)
        
except ImportError as e:
    STDPIPE_AVAILABLE = False
    STDPIPE_ERROR = f"Impossible d'importer stdpipe: {e}"
    logger.warning(f"STDPipe n'est pas installé ou n'est pas accessible: {e}")
except Exception as e:
    STDPIPE_AVAILABLE = False
    STDPIPE_ERROR = f"Erreur lors de l'import de STDPipe: {e}"
    logger.error(f"Erreur inattendue lors de l'import de STDPipe: {e}", exc_info=True)

from astropy.io import fits
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import astropy.units as u

# Import synphot pour conversion de filtres
try:
    from synphot import SpectralElement, SourceSpectrum, Observation
    from synphot.models import BlackBody1D
    from synphot.units import VEGAMAG
    SYNPHOT_AVAILABLE = True
except ImportError:
    SYNPHOT_AVAILABLE = False
    logger.warning("synphot n'est pas installé. Les filtres U, B, V, R, I ne sont pas disponibles.")

# Import photutils.psf pour photométrie PSF (optionnel)
try:
    from photutils.psf import BasicPSFPhotometry, DAOPhotPSFPhotometry, IntegratedGaussianPRF
    from photutils.detection import IRAFStarFinder
    from photutils.background import MMMBackground
    PSF_PHOTOMETRY_AVAILABLE = True
    logger.debug("photutils.psf disponible - photométrie PSF activée")
except ImportError:
    PSF_PHOTOMETRY_AVAILABLE = False
    logger.debug("photutils.psf non disponible - seule la photométrie d'ouverture sera disponible")

# Import Gaia query et services d'images
try:
    from astroquery.gaia import Gaia
    from astroquery.vizier import Vizier
    try:
        from astroquery.skyview import SkyView
        SKYVIEW_AVAILABLE = True
    except ImportError:
        SKYVIEW_AVAILABLE = False
        logger.info("astroquery.skyview non disponible, utilisation d'alternatives pour les images")
    try:
        from astroquery.sdss import SDSS
        SDSS_AVAILABLE = True
    except ImportError:
        SDSS_AVAILABLE = False
        logger.info("astroquery.sdss non disponible")
    GAIA_AVAILABLE = True
except ImportError:
    GAIA_AVAILABLE = False
    SKYVIEW_AVAILABLE = False
    SDSS_AVAILABLE = False
    logger.warning("astroquery n'est pas disponible. Les requêtes Gaia et le téléchargement d'images ne fonctionneront pas.")


class STDPipeWrapper:
    """
    Wrapper pour utiliser STDPipe de manière simplifiée dans NPOAP.
    
    STDPipe fournit:
    - Astrométrie automatique
    - Photométrie et calibration
    - Soustraction d'images
    - Détection de transitoires
    - Téléchargement d'images de référence depuis Pan-STARRS, SDSS, etc.
    """
    
    def __init__(self):
        if not STDPIPE_AVAILABLE:
            raise ImportError("STDPipe n'est pas installé. Installez-le avec: pip install stdpipe")
    
    def detect_sources(self, image_data: np.ndarray, header: Optional[fits.Header] = None,
                       threshold_sigma: float = 5.0, fwhm: Optional[float] = None,
                       method: str = 'photutils_segmentation', **kwargs) -> Optional[Table]:
        """
        Détecte les sources dans une image.
        
        Parameters
        ----------
        image_data : np.ndarray
            Données de l'image
        header : fits.Header, optional
            Header FITS avec WCS
        threshold_sigma : float
            Seuil de détection en sigma (défaut: 5.0)
        fwhm : float, optional
            FWHM estimé pour la détection
        method : str
            Méthode de détection: 'photutils_segmentation', 'photutils_dao', 'photutils_iraf', 
            ou 'stdpipe_default' (défaut: 'photutils_segmentation')
        **kwargs
            Paramètres additionnels pour la méthode choisie
        
        Returns
        -------
        Table or None
            Catalogue des sources détectées avec positions (pixel et WCS si disponible)
        """
        try:
            if header:
                wcs_obj = WCS(header)
            else:
                wcs_obj = None
            
            # Utiliser la méthode photutils si demandée
            if method.startswith('photutils'):
                return self._detect_sources_photutils(
                    image_data, header, threshold_sigma, fwhm, method, **kwargs
                )
            
            # Méthode par défaut (STDPipe ou fallback)
            if cutouts and hasattr(cutouts, 'detect_sources'):
                sources = cutouts.detect_sources(image_data, threshold=threshold_sigma, fwhm=fwhm)
            elif hasattr(stdpipe, 'detect_sources'):
                sources = stdpipe.detect_sources(image_data, threshold=threshold_sigma, fwhm=fwhm)
            else:
                # Fallback: utiliser photutils directement
                from photutils.detection import DAOStarFinder
                from astropy.stats import sigma_clipped_stats
                mean, median, std = sigma_clipped_stats(image_data)
                daofind = DAOStarFinder(fwhm=fwhm if fwhm else 3.0, threshold=threshold_sigma * std)
                sources = daofind(image_data)
                if sources is None:
                    return None
            
            # Convertir en Table Astropy si ce n'est pas déjà le cas
            if not isinstance(sources, Table):
                sources = Table(sources)
            
            # Si WCS disponible, ajouter RA/Dec
            if wcs_obj and wcs_obj.is_celestial and len(sources) > 0:
                if 'x' in sources.colnames and 'y' in sources.colnames:
                    coords = wcs_obj.pixel_to_world(sources['x'], sources['y'])
                    sources['ra'] = coords.ra.deg
                    sources['dec'] = coords.dec.deg
            
            return sources
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de sources: {e}", exc_info=True)
            return None
    
    def _detect_sources_photutils(self, image_data: np.ndarray, header: Optional[fits.Header] = None,
                                  threshold_sigma: float = 5.0, fwhm: Optional[float] = None,
                                  method: str = 'photutils_segmentation', **kwargs) -> Optional[Table]:
        """
        Détecte les sources en utilisant photutils via STDPipe.
        
        Parameters
        ----------
        image_data : np.ndarray
            Données de l'image
        header : fits.Header, optional
            Header FITS avec WCS
        threshold_sigma : float
            Seuil de détection en sigma
        fwhm : float, optional
            FWHM pour les méthodes dao/iraf
        method : str
            Méthode: 'photutils_segmentation', 'photutils_dao', 'photutils_iraf'
        **kwargs
            Paramètres additionnels pour get_objects_photutils
        
        Returns
        -------
        Table or None
            Catalogue des sources détectées
        """
        try:
            # Déterminer la méthode photutils à utiliser
            if method == 'photutils_segmentation':
                photutils_method = 'segmentation'
            elif method == 'photutils_dao':
                photutils_method = 'dao'
            elif method == 'photutils_iraf':
                photutils_method = 'iraf'
            else:
                photutils_method = 'segmentation'
            
            # Paramètres par défaut
            params = {
                'image': image_data,
                'header': header,
                'thresh': threshold_sigma,
                'method': photutils_method,
                'fwhm': fwhm if fwhm else 3.0,
                'aper': kwargs.get('aper', 3.0),
                'deblend': kwargs.get('deblend', True) if photutils_method == 'segmentation' else False,
                'minarea': kwargs.get('minarea', 5),
                'edge': kwargs.get('edge', 10),
                'sn': kwargs.get('sn', 3.0),
            }
            
            # Paramètres spécifiques pour segmentation
            if photutils_method == 'segmentation':
                params.update({
                    'npixels': kwargs.get('npixels', 5),
                    'nlevels': kwargs.get('nlevels', 32),
                    'contrast': kwargs.get('contrast', 0.001),
                    'connectivity': kwargs.get('connectivity', 8),
                })
            
            # Paramètres spécifiques pour dao/iraf
            if photutils_method in ['dao', 'iraf']:
                params.update({
                    'sharplo': kwargs.get('sharplo', 0.2),
                    'sharphi': kwargs.get('sharphi', 1.0),
                    'roundlo': kwargs.get('roundlo', -1.0),
                    'roundhi': kwargs.get('roundhi', 1.0),
                })
            
            # Ajouter les autres paramètres optionnels
            for key in ['mask', 'err', 'saturation', 'bkgann', 'bg_size', 'subtract_bg', 'wcs']:
                if key in kwargs:
                    params[key] = kwargs[key]
            
            # Appeler la fonction STDPipe
            if stdpipe_photometry and hasattr(stdpipe_photometry, 'get_objects_photutils'):
                sources = stdpipe_photometry.get_objects_photutils(**params)
                return sources
            else:
                logger.warning("stdpipe.photometry.get_objects_photutils non disponible, utilisation du fallback")
                # Fallback vers photutils directement
                return self._detect_sources_photutils_fallback(
                    image_data, header, threshold_sigma, fwhm, photutils_method, **kwargs
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la détection photutils: {e}", exc_info=True)
            return None
    
    def _detect_sources_photutils_fallback(self, image_data: np.ndarray, header: Optional[fits.Header],
                                           threshold_sigma: float, fwhm: Optional[float],
                                           method: str, **kwargs) -> Optional[Table]:
        """
        Fallback vers photutils directement si STDPipe n'est pas disponible.
        """
        from photutils.detection import DAOStarFinder, IRAFStarFinder
        from photutils.segmentation import detect_sources, deblend_sources
        from astropy.stats import sigma_clipped_stats
        from photutils.aperture import CircularAperture, aperture_photometry
        from photutils.background import Background2D, MedianBackground
        
        try:
            # Estimer le bruit
            mean, median, std = sigma_clipped_stats(image_data)
            threshold = threshold_sigma * std
            
            if method == 'segmentation':
                # Détection par segmentation
                sources = detect_sources(image_data, threshold, npixels=kwargs.get('npixels', 5))
                
                if kwargs.get('deblend', True) and sources.nlabels > 0:
                    sources = deblend_sources(
                        image_data, sources,
                        npixels=kwargs.get('npixels', 5),
                        nlevels=kwargs.get('nlevels', 32),
                        contrast=kwargs.get('contrast', 0.001)
                    )
                
                # Extraire les propriétés
                from photutils.segmentation import SourceProperties
                cat = SourceProperties(image_data, sources)
                
                # Convertir en Table
                tbl = cat.to_table(['xcentroid', 'ycentroid', 'area', 'fwhm', 'semimajor_axis_sigma',
                                   'semiminor_axis_sigma', 'orientation'])
                tbl.rename_column('xcentroid', 'x')
                tbl.rename_column('ycentroid', 'y')
                
            elif method == 'dao':
                daofind = DAOStarFinder(
                    fwhm=fwhm if fwhm else 3.0,
                    threshold=threshold,
                    sharplo=kwargs.get('sharplo', 0.2),
                    sharphi=kwargs.get('sharphi', 1.0),
                    roundlo=kwargs.get('roundlo', -1.0),
                    roundhi=kwargs.get('roundhi', 1.0)
                )
                tbl = daofind(image_data)
                
            elif method == 'iraf':
                iraffind = IRAFStarFinder(
                    fwhm=fwhm if fwhm else 3.0,
                    threshold=threshold,
                    sharplo=kwargs.get('sharplo', 0.2),
                    sharphi=kwargs.get('sharphi', 1.0),
                    roundlo=kwargs.get('roundlo', -1.0),
                    roundhi=kwargs.get('roundhi', 1.0)
                )
                tbl = iraffind(image_data)
            else:
                return None
            
            if tbl is None or len(tbl) == 0:
                return None
            
            # Ajouter photométrie d'ouverture
            aper = kwargs.get('aper', 3.0)
            apertures = CircularAperture(list(zip(tbl['x'], tbl['y'])), r=aper)
            phot = aperture_photometry(image_data, apertures)
            tbl['flux'] = phot['aperture_sum']
            tbl['fluxerr'] = phot['aperture_sum_err'] if 'aperture_sum_err' in phot.colnames else 0
            
            # Convertir en magnitudes instrumentales
            tbl['mag'] = -2.5 * np.log10(np.maximum(tbl['flux'], 1.0))
            
            # Ajouter WCS si disponible
            if header:
                wcs_obj = WCS(header)
                if wcs_obj.is_celestial:
                    coords = wcs_obj.pixel_to_world(tbl['x'], tbl['y'])
                    tbl['ra'] = coords.ra.deg
                    tbl['dec'] = coords.dec.deg
            
            return tbl
            
        except Exception as e:
            logger.error(f"Erreur fallback photutils: {e}", exc_info=True)
            return None
    
    def solve_astrometry(self, image_path: str, output_path: Optional[str] = None,
                        radius: float = 0.5, timeout: int = 300) -> Optional[WCS]:
        """
        Résout l'astrométrie d'une image en utilisant Astrometry.Net.
        
        Essaie d'abord STDPipe, puis utilise directement Astrometry.Net (NOVA) en fallback.
        
        Parameters
        ----------
        image_path : str
            Chemin vers l'image FITS
        output_path : str, optional
            Chemin de sortie pour l'image astrométriée (si None, modifie l'image en place)
        radius : float
            Rayon de recherche en degrés (défaut: 0.5)
        timeout : int
            Timeout en secondes (défaut: 300)
        
        Returns
        -------
        WCS or None
            WCS ajusté ou None en cas d'échec
        """
        from astropy.io import fits
        from astropy.wcs import WCS
        from pathlib import Path
        
        image_path = Path(image_path)
        output_path = Path(output_path) if output_path else image_path
        
        # Méthode 1: Essayer STDPipe d'abord
        if stdpipe_astrometry and hasattr(stdpipe_astrometry, 'solve_astrometry'):
            try:
                logger.info(f"Tentative de résolution astrométrique avec STDPipe...")
                result = stdpipe_astrometry.solve_astrometry(
                    str(image_path),
                    output=str(output_path),
                    radius=radius,
                    timeout=timeout
                )
                if result:
                    with fits.open(output_path) as hdul:
                        header = hdul[0].header
                        if 'CRVAL1' in header:  # WCS présent
                            logger.info("✅ Astrométrie résolue avec STDPipe")
                            return WCS(header)
            except Exception as e:
                logger.warning(f"STDPipe astrometry a échoué: {e}")
        
        # Méthode 2: Fallback sur Astrometry.Net (NOVA) directement
        try:
            logger.info(f"Tentative de résolution astrométrique avec Astrometry.Net (NOVA)...")
            from core.astrometry import AstrometrySolverNova
            import config
            
            # Utiliser le chemin de la clé API depuis config.py
            api_key_file = config.ASTROMETRY_API_KEY_FILE
            
            # NOVA modifie l'image en place et sauvegarde aussi dans output_dir
            # On utilise le même fichier d'entrée
            solver = AstrometrySolverNova(
                api_key_file=api_key_file,
                output_dir=image_path.parent
            )
            solver.solve_file(image_path, progress_callback=None)
            # NOVA modifie l'image en place ; vérifier la présence du WCS
            with fits.open(image_path) as hdul:
                header = hdul[0].header
                if 'CRVAL1' in header:
                    if output_path != image_path:
                        import shutil
                        shutil.copy2(image_path, output_path)
                    logger.info("✅ Astrométrie résolue avec Astrometry.Net (NOVA)")
                    return WCS(header)
            logger.error("Astrométrie échouée avec Astrometry.Net (NOVA) (pas de WCS après résolution)")
                
        except ImportError as e:
            logger.error(f"Impossible d'importer AstrometrySolverNova: {e}")
        except FileNotFoundError as e:
            logger.error(f"Clé API Astrometry.net manquante: {e}")
            logger.error("Veuillez configurer votre clé API dans l'onglet Accueil")
        except Exception as e:
            logger.error(f"Erreur lors de la résolution astrométrique avec NOVA: {e}", exc_info=True)
        
        logger.error("❌ Échec de la résolution astrométrique avec toutes les méthodes")
        return None
    
    def download_reference_image(self, coord: SkyCoord, catalog: str = 'panstarrs',
                                filter_name: str = 'r', radius: float = 0.25) -> Optional[str]:
        """
        Télécharge une image de référence depuis un catalogue.
        
        Supporte plusieurs méthodes :
        1. STDPipe (si disponible)
        2. astroquery.skyview (Pan-STARRS, SDSS, DES, etc.)
        3. astroquery.sdss (pour SDSS uniquement)
        
        Parameters
        ----------
        coord : SkyCoord
            Coordonnées du champ
        catalog : str
            Catalogue à utiliser ('panstarrs', 'sdss', 'des', 'gaia', etc.)
            Note: 'gaia' ne fournit pas d'images, seulement des catalogues d'étoiles
        filter_name : str
            Filtre à télécharger ('g', 'r', 'i', 'z', etc.)
        radius : float
            Rayon en degrés (défaut: 0.25)
        
        Returns
        -------
        str or None
            Chemin vers l'image de référence téléchargée
        """
        try:
            # Note: Gaia ne fournit pas d'images, seulement des catalogues
            if catalog.lower() == 'gaia':
                logger.warning("Gaia ne fournit pas d'images, seulement des catalogues d'étoiles. Utilisez 'panstarrs', 'sdss' ou 'des' pour les images.")
                return None
            
            # Méthode 1: Utiliser STDPipe si disponible
            if stdpipe_catalogues and hasattr(stdpipe_catalogues, 'download_reference_image'):
                try:
                    ref_image = stdpipe_catalogues.download_reference_image(
                        coord,
                        catalog=catalog,
                        filter_name=filter_name,
                        radius=radius
                    )
                    if ref_image:
                        logger.info(f"Image téléchargée via STDPipe: {ref_image}")
                        return ref_image
                except Exception as e:
                    logger.warning(f"Échec téléchargement via STDPipe: {e}, tentative avec astroquery")
            
            # Méthode 2: Utiliser astroquery.skyview ou astroquery.sdss
            if not GAIA_AVAILABLE:
                logger.error("astroquery n'est pas disponible. Impossible de télécharger des images.")
                return None
            
            # Mapper les catalogues vers les noms SkyView
            skyview_catalog_map = {
                'panstarrs': 'PanSTARRS',
                'pan-starrs': 'PanSTARRS',
                'sdss': 'SDSS',
                'des': 'DSS',
                'dss': 'DSS',
                '2mass': '2MASS',
                'wise': 'WISE'
            }
            
            skyview_name = skyview_catalog_map.get(catalog.lower(), catalog.upper())
            
            # Télécharger via SkyView
            if SKYVIEW_AVAILABLE:
                try:
                    logger.info(f"Téléchargement image {skyview_name} filtre {filter_name} via SkyView...")
                    
                    # SkyView utilise des noms de surveys spécifiques
                    # Pour Pan-STARRS, on doit spécifier le filtre dans le nom du survey
                    if skyview_name == 'PanSTARRS':
                        survey_name = f'PanSTARRS-DR1 {filter_name.upper()}'
                    elif skyview_name == 'SDSS':
                        survey_name = f'SDSS {filter_name.upper()}'
                    else:
                        survey_name = skyview_name
                    
                    # Télécharger l'image
                    hdul = SkyView.get_images(
                        position=coord,
                        survey=survey_name,
                        radius=radius * u.deg,
                        pixels=512  # Taille par défaut
                    )
                    
                    if hdul and len(hdul) > 0:
                        # Sauvegarder l'image
                        output_dir = Path.home() / ".npoap" / "reference_images"
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        filename = f"ref_{catalog}_{filter_name}_{coord.ra.deg:.5f}_{coord.dec.deg:.5f}.fits"
                        output_path = output_dir / filename
                        
                        hdul[0].writeto(str(output_path), overwrite=True)
                        logger.info(f"Image téléchargée via SkyView: {output_path}")
                        return str(output_path)
                    else:
                        logger.warning(f"Aucune image trouvée pour {survey_name}")
                        
                except Exception as e:
                    logger.warning(f"Échec téléchargement via SkyView: {e}")
            
            # Méthode 3: Utiliser astroquery.sdss directement pour SDSS
            if catalog.lower() == 'sdss' and SDSS_AVAILABLE:
                try:
                    logger.info(f"Téléchargement image SDSS filtre {filter_name} via astroquery.sdss...")
                    
                    # Trouver les images SDSS disponibles
                    field = SDSS.query_region(coord, radius=radius * u.deg, 
                                             photoobj_fields=['ra', 'dec', 'run', 'rerun', 'camcol', 'field'])
                    
                    if field and len(field) > 0:
                        # Prendre le premier champ trouvé
                        run = field[0]['run']
                        camcol = field[0]['camcol']
                        field_id = field[0]['field']
                        
                        # Télécharger l'image
                        hdul = SDSS.get_images(run=run, camcol=camcol, field=field_id, 
                                             band=filter_name.lower())
                        
                        if hdul and len(hdul) > 0:
                            output_dir = Path.home() / ".npoap" / "reference_images"
                            output_dir.mkdir(parents=True, exist_ok=True)
                            
                            filename = f"ref_sdss_{filter_name}_{coord.ra.deg:.5f}_{coord.dec.deg:.5f}.fits"
                            output_path = output_dir / filename
                            
                            hdul[0].writeto(str(output_path), overwrite=True)
                            logger.info(f"Image téléchargée via SDSS: {output_path}")
                            return str(output_path)
                            
                except Exception as e:
                    logger.warning(f"Échec téléchargement via SDSS: {e}")
            
            # Si toutes les méthodes ont échoué
            logger.error(f"Impossible de télécharger l'image depuis {catalog}. Toutes les méthodes ont échoué.")
            logger.info("Vous pouvez utiliser une image de référence locale à la place.")
            return None
                
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de l'image de référence: {e}", exc_info=True)
            return None
    
    def check_image_compatibility(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """
        Vérifie la compatibilité de deux images pour la soustraction.
        Compare les caractéristiques (taille, échelle de pixels, WCS, etc.).
        
        Parameters
        ----------
        image1_path : str
            Chemin vers la première image
        image2_path : str
            Chemin vers la deuxième image
        
        Returns
        -------
        dict
            Dictionnaire avec les informations de compatibilité :
            - 'compatible': bool (si les images sont compatibles)
            - 'warnings': list (avertissements si incompatibilités mineures)
            - 'errors': list (erreurs si incompatibilités majeures)
            - 'scale_ratio': float (ratio des échelles de pixels)
            - 'size_ratio': tuple (ratio des tailles en pixels)
            - 'pixel_scale1': float (échelle pixel image1, arcsec/pixel)
            - 'pixel_scale2': float (échelle pixel image2, arcsec/pixel)
        """
        try:
            with fits.open(image1_path) as hdul1:
                data1 = hdul1[0].data
                header1 = hdul1[0].header
                wcs1 = WCS(header1)
            
            with fits.open(image2_path) as hdul2:
                data2 = hdul2[0].data
                header2 = hdul2[0].header
                wcs2 = WCS(header2)
            
            result = {
                'compatible': True,
                'warnings': [],
                'errors': [],
                'scale_ratio': None,
                'size_ratio': None,
                'pixel_scale1': None,
                'pixel_scale2': None
            }
            
            # Vérifier les tailles
            ny1, nx1 = data1.shape
            ny2, nx2 = data2.shape
            size_ratio = (nx2/nx1, ny2/ny1)
            result['size_ratio'] = size_ratio
            
            # Vérifier les échelles de pixels si WCS disponibles
            if wcs1.is_celestial and wcs2.is_celestial:
                try:
                    scale1 = proj_plane_pixel_scales(wcs1)
                    scale2 = proj_plane_pixel_scales(wcs2)
                    pixel_scale1 = np.mean(scale1) * 3600.0  # arcsec/pixel
                    pixel_scale2 = np.mean(scale2) * 3600.0  # arcsec/pixel
                    
                    result['pixel_scale1'] = pixel_scale1
                    result['pixel_scale2'] = pixel_scale2
                    scale_ratio = pixel_scale2 / pixel_scale1
                    result['scale_ratio'] = scale_ratio
                    
                    # Avertissements pour différences d'échelle
                    if abs(scale_ratio - 1.0) > 0.1:  # Plus de 10% de différence
                        result['warnings'].append(
                            f"Échelles de pixels différentes: {pixel_scale1:.3f}\" vs {pixel_scale2:.3f}\" "
                            f"(ratio: {scale_ratio:.2f}). STDPipe effectuera une mise à l'échelle automatique."
                        )
                    
                    # Vérifier le FOV (Field of View)
                    corners1 = wcs1.pixel_to_world([0, nx1], [0, ny1])
                    corners2 = wcs2.pixel_to_world([0, nx2], [0, ny2])
                    fov1 = np.max([c.separation(corners1[0]).arcsec for c in corners1])
                    fov2 = np.max([c.separation(corners2[0]).arcsec for c in corners2])
                    fov_ratio = fov2 / fov1
                    
                    if abs(fov_ratio - 1.0) > 0.2:  # Plus de 20% de différence
                        result['warnings'].append(
                            f"FOV différents: {fov1:.1f}\" vs {fov2:.1f}\" (ratio: {fov_ratio:.2f}). "
                            f"La soustraction peut être partielle."
                        )
                    
                except Exception as e:
                    result['warnings'].append(f"Impossible de comparer les échelles de pixels: {e}")
            
            # Avertissements pour différences de taille
            if abs(size_ratio[0] - 1.0) > 0.1 or abs(size_ratio[1] - 1.0) > 0.1:
                result['warnings'].append(
                    f"Tailles différentes: {nx1}x{ny1} vs {nx2}x{ny2}. "
                    f"STDPipe effectuera un rééchantillonnage automatique."
                )
            
            # Vérifier la présence de WCS
            if not wcs1.is_celestial:
                result['errors'].append("Image science sans WCS astrométrique valide")
                result['compatible'] = False
            if not wcs2.is_celestial:
                result['errors'].append("Image de référence sans WCS astrométrique valide")
                result['compatible'] = False
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de compatibilité: {e}", exc_info=True)
            return {
                'compatible': False,
                'errors': [f"Erreur de vérification: {e}"],
                'warnings': []
            }
    
    def subtract_images(self, science_image: str, reference_image: str,
                       output_path: str, method: str = 'hotpants',
                       check_compatibility: bool = True,
                       alard_lupton_use_poisson_weights: bool = True,
                       alard_lupton_gain: float = 1.0) -> Tuple[bool, Optional[Dict]]:
        """
        Soustrait l'image de référence de l'image science.

        STDPipe effectue automatiquement :
        - L'alignement astrométrique des images
        - La mise à l'échelle (resampling) si les échelles de pixels diffèrent
        - Le rééchantillonnage si les tailles d'images diffèrent

        Parameters
        ----------
        science_image : str
            Chemin vers l'image science
        reference_image : str
            Chemin vers l'image de référence
        output_path : str
            Chemin de sortie pour l'image soustraite
        method : str
            Méthode de soustraction ('simple', 'hotpants', 'zogy', 'alardlupton')
        check_compatibility : bool
            Vérifier la compatibilité des images avant soustraction (défaut: True)
        alard_lupton_use_poisson_weights : bool
            Pour méthode alardlupton: pondération 1/σ² avec σ² ∝ I (article Alard & Lupton). Défaut True.
        alard_lupton_gain : float
            Pour méthode alardlupton: gain (ADU/photon) pour les poids Poisson. Défaut 1.0.

        Returns
        -------
        tuple (bool, dict or None)
            - bool: True si la soustraction a réussi
            - dict: Informations de compatibilité si check_compatibility=True, None sinon
        """
        compatibility_info = None

        try:
            # Vérifier la compatibilité si demandé
            if check_compatibility:
                compatibility_info = self.check_image_compatibility(science_image, reference_image)
                if not compatibility_info['compatible']:
                    logger.error(f"Images incompatibles: {compatibility_info['errors']}")
                    return False, compatibility_info
                if compatibility_info['warnings']:
                    logger.warning(f"Avertissements de compatibilité: {compatibility_info['warnings']}")

            # Méthode 1: Utiliser STDPipe si disponible
            if stdpipe_subtraction and hasattr(stdpipe_subtraction, 'subtract'):
                try:
                    result = stdpipe_subtraction.subtract(
                        science_image,
                        reference_image,
                        output=output_path,
                        method=method
                    )
                    if result is not None:
                        logger.info(f"Soustraction réussie via STDPipe: {output_path}")
                        return True, compatibility_info
                except Exception as e:
                    logger.warning(f"Échec soustraction via STDPipe: {e}, tentative avec méthode alternative")

            # Méthode 2: Utiliser une implémentation alternative
            logger.info("Utilisation de la méthode alternative de soustraction d'images")
            return self._subtract_images_alternative(
                science_image, reference_image, output_path, method, compatibility_info,
                alard_lupton_use_poisson_weights=alard_lupton_use_poisson_weights,
                alard_lupton_gain=alard_lupton_gain,
            )
                
        except Exception as e:
            logger.error(f"Erreur lors de la soustraction: {e}", exc_info=True)
            return False, compatibility_info
    
    def _zogy_subtract(self, image_new: np.ndarray, image_ref: np.ndarray,
                       fwhm_new: float = 3.0, fwhm_ref: Optional[float] = None,
                       scale_ratio: float = 1.0) -> np.ndarray:
        """
        Soustraction d'images optimale ZOGY (Zackay, Ofek & Gal-Yam 2016).
        
        En espace de Fourier : R = (F_new * P_ref* * sigma_ref^2 - F_ref * P_new* * sigma_new^2)
        / sqrt(sigma_ref^2 |P_new|^2 + sigma_new^2 |P_ref|^2)
        avec P = FFT(PSF Gaussienne). Retourne Re(IFFT(R)).
        
        Parameters
        ----------
        image_new : np.ndarray
            Image science (nouvelle)
        image_ref : np.ndarray
            Image de référence (même dimensions)
        fwhm_new : float
            FWHM de la PSF image science en pixels (défaut 3.0)
        fwhm_ref : float, optional
            FWHM de la PSF référence ; si None, utilise fwhm_new
        scale_ratio : float
            Ratio échelle réf/science ; si > 2, on équilibre les sigmas (réf rééchantillonnée)
        
        Returns
        -------
        np.ndarray
            Image soustraite ZOGY
        """
        if image_new.shape != image_ref.shape:
            raise ValueError("ZOGY nécessite des images de mêmes dimensions")
        ny, nx = image_new.shape
        if fwhm_ref is None:
            fwhm_ref = fwhm_new
        # Sigma du bruit (estimation par MAD sur les bords / fond)
        def _est_sigma(img: np.ndarray) -> float:
            margin = max(2, min(nx, ny) // 20)
            edge = np.concatenate([
                img[:margin, :].ravel(), img[-margin:, :].ravel(),
                img[:, :margin].ravel(), img[:, -margin:].ravel()
            ])
            if len(edge) < 50:
                return np.nanmedian(np.abs(img - np.nanmedian(img))) / 0.6745
            return np.nanmedian(np.abs(edge - np.nanmedian(edge))) / 0.6745
        sigma_new = _est_sigma(image_new)
        sigma_ref = _est_sigma(image_ref)
        if sigma_new <= 0 or not np.isfinite(sigma_new):
            sigma_new = 1.0
        if sigma_ref <= 0 or not np.isfinite(sigma_ref):
            sigma_ref = 1.0
        # Référence rééchantillonnée : l'estimation sigma_ref est souvent fausse (lissée ou biaisée).
        # Équilibrer pour que la soustraction ait une amplitude correcte (éviter "ne soustrait rien").
        if scale_ratio > 2.0:
            sigma_ref = sigma_new
            logger.debug("ZOGY: référence rééchantillonnée, utilisation sigma_ref = sigma_new")
        # PSF Gaussienne : sigma = FWHM / (2*sqrt(2*ln(2)))
        def _gaussian_psf_fft(nx: int, ny: int, fwhm: float) -> np.ndarray:
            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            y = np.fft.fftfreq(ny)[:, np.newaxis]
            x = np.fft.fftfreq(nx)[np.newaxis, :]
            k2 = x*x + y*y
            # Gaussienne en Fourier (non normalisée, pic au centre)
            P = np.exp(-2 * np.pi**2 * sigma**2 * k2)
            return P.astype(np.complex128)
        P_new = _gaussian_psf_fft(nx, ny, fwhm_new)
        P_ref = _gaussian_psf_fft(nx, ny, fwhm_ref)
        F_new = np.fft.fft2(np.nan_to_num(image_new, nan=0.0))
        F_ref = np.fft.fft2(np.nan_to_num(image_ref, nan=0.0))
        # Numérateur : F_new * conj(P_ref) * sigma_ref^2 - F_ref * conj(P_new) * sigma_new^2
        num = F_new * np.conj(P_ref) * (sigma_ref ** 2) - F_ref * np.conj(P_new) * (sigma_new ** 2)
        denom = np.sqrt((sigma_ref ** 2) * (np.abs(P_new) ** 2) + (sigma_new ** 2) * (np.abs(P_ref) ** 2))
        denom = np.maximum(denom, 1e-20)
        R = num / denom
        # IFFT sans facteur 1/N dans numpy : normaliser par N pour avoir des unités flux/pixel
        n_pixels = nx * ny
        subtracted = np.fft.ifft2(R).real / n_pixels
        # Centrer le fond à 0 (résidu médian)
        med = np.nanmedian(subtracted)
        subtracted = subtracted - med
        return subtracted.astype(np.float64)
    
    def _subtract_images_alternative(self, science_image: str, reference_image: str,
                                    output_path: str, method: str,
                                    compatibility_info: Optional[Dict] = None,
                                    alard_lupton_use_poisson_weights: bool = True,
                                    alard_lupton_gain: float = 1.0) -> Tuple[bool, Optional[Dict]]:
        """
        Méthode alternative de soustraction d'images utilisant reproject et des méthodes de base.
        
        Gère automatiquement :
        - L'alignement astrométrique via WCS
        - La mise à l'échelle (resampling) si les échelles de pixels diffèrent
        - Le rééchantillonnage si les tailles d'images diffèrent
        """
        try:
            from reproject import reproject_interp
            REPROJECT_AVAILABLE = True
        except ImportError:
            REPROJECT_AVAILABLE = False
            logger.warning("reproject n'est pas disponible. Installation recommandée: pip install reproject")
        
        try:
            # Charger les images
            with fits.open(science_image) as hdul_sci:
                data_sci = hdul_sci[0].data.astype(float)
                header_sci = hdul_sci[0].header.copy()
                wcs_sci = WCS(header_sci)
            
            with fits.open(reference_image) as hdul_ref:
                data_ref = hdul_ref[0].data.astype(float)
                header_ref = hdul_ref[0].header.copy()
                wcs_ref = WCS(header_ref)
            
            # Vérifier si les images ont des WCS valides
            if not wcs_sci.is_celestial or not wcs_ref.is_celestial:
                logger.error("Les deux images doivent avoir des WCS astrométriques valides pour la soustraction")
                return False, compatibility_info
            
            # Obtenir l'image de référence alignée sur la science (même dimensions)
            data_ref_aligned = None
            if data_sci.shape == data_ref.shape:
                try:
                    scale_sci = proj_plane_pixel_scales(wcs_sci)
                    scale_ref = proj_plane_pixel_scales(wcs_ref)
                    scale_ratio = np.mean(scale_ref) / np.mean(scale_sci)
                    if abs(scale_ratio - 1.0) < 0.01:
                        logger.info("Mêmes dimensions et échelle, pas de rééchantillonnage")
                        data_ref_aligned = data_ref
                    else:
                        if REPROJECT_AVAILABLE:
                            logger.info(f"Rééchantillonnage de l'image de référence (ratio: {scale_ratio:.3f})")
                            data_ref_aligned, _ = reproject_interp(
                                (data_ref, wcs_ref), wcs_sci, shape_out=data_sci.shape
                            )
                        else:
                            logger.error("reproject est nécessaire pour rééchantillonner les images")
                            return False, compatibility_info
                except Exception as e:
                    logger.warning(f"Comparaison WCS: {e}, rééchantillonnage")
                    if REPROJECT_AVAILABLE:
                        data_ref_aligned, _ = reproject_interp(
                            (data_ref, wcs_ref), wcs_sci, shape_out=data_sci.shape
                        )
                    else:
                        return False, compatibility_info
            else:
                if REPROJECT_AVAILABLE:
                    logger.info(f"Rééchantillonnage de l'image de référence ({data_ref.shape} -> {data_sci.shape})")
                    data_ref_aligned, _ = reproject_interp(
                        (data_ref, wcs_ref), wcs_sci, shape_out=data_sci.shape
                    )
                else:
                    logger.error("reproject est nécessaire pour rééchantillonner les images")
                    return False, compatibility_info
            
            if data_ref_aligned is None:
                return False, compatibility_info
            
            # Ratio d'échelle (réf/science) : si > 1, la référence est plus grossière (PSF plus large en px science)
            scale_ratio = 1.0
            try:
                scale_sci = proj_plane_pixel_scales(wcs_sci)
                scale_ref = proj_plane_pixel_scales(wcs_ref)
                scale_ratio = float(np.mean(scale_ref) / np.mean(scale_sci))
            except Exception:
                pass
            
            # Appliquer ZOGY, Alard-Lupton, simple ou hotpants
            if method.lower() == 'zogy':
                try:
                    # FWHM référence plus large si la référence a été rééchantillonnée (échelle plus grossière)
                    fwhm_new = 3.0
                    fwhm_ref = min(25.0, fwhm_new * max(1.0, scale_ratio))
                    subtracted = self._zogy_subtract(
                        data_sci, data_ref_aligned,
                        fwhm_new=fwhm_new, fwhm_ref=fwhm_ref,
                        scale_ratio=scale_ratio
                    )
                    logger.info(f"Soustraction ZOGY (Zackay et al. 2016) appliquée (FWHM science={fwhm_new}, réf={fwhm_ref:.1f})")
                except Exception as e:
                    logger.warning(f"ZOGY échoué ({e}), bascule en soustraction simple")
                    subtracted = data_sci - data_ref_aligned
                    med = np.nanmedian(subtracted)
                    subtracted = subtracted - med
            elif method.lower() == 'alardlupton':
                try:
                    from core.alard_lupton import alard_lupton_subtract
                    subtracted = alard_lupton_subtract(
                        data_sci, data_ref_aligned,
                        kernel_half_size=10,
                        kernel_sigmas=(0.5, 1.0, 2.0, 3.0),
                        fit_background=True,
                        use_poisson_weights=alard_lupton_use_poisson_weights,
                        gain=alard_lupton_gain,
                    )
                    logger.info(
                        f"Soustraction Alard-Lupton (1998) appliquée (noyau constant, pur Python, "
                        f"pondération Poisson={alard_lupton_use_poisson_weights}, gain={alard_lupton_gain})"
                    )
                except ImportError as e:
                    logger.warning(f"Alard-Lupton indisponible ({e}), bascule en soustraction simple")
                    subtracted = data_sci - data_ref_aligned
                    med = np.nanmedian(subtracted)
                    subtracted = subtracted - med
                except Exception as e:
                    logger.warning(f"Alard-Lupton échoué ({e}), bascule en soustraction simple")
                    subtracted = data_sci - data_ref_aligned
                    med = np.nanmedian(subtracted)
                    subtracted = subtracted - med
            elif method.lower() == 'simple':
                subtracted = data_sci - data_ref_aligned
                med = np.nanmedian(subtracted)
                subtracted = subtracted - med
                logger.info("Soustraction simple (science - référence, médiane à 0)")
            else:
                subtracted = data_sci - data_ref_aligned
                if method.lower() == 'hotpants':
                    logger.info("Méthode hotpants demandée, soustraction simple avec normalisation")
                    mask = np.abs(subtracted) < np.percentile(np.abs(subtracted), 50)
                    if np.sum(mask) > 100:
                        subtracted = subtracted - np.median(subtracted[mask])
                else:
                    med = np.nanmedian(subtracted)
                    subtracted = subtracted - med
            
            # Sauvegarder l'image soustraite
            # Note: Les en-têtes FITS doivent contenir uniquement des caractères ASCII
            ref_name = Path(reference_image).name
            header_sci['HISTORY'] = f'Image soustraite de {ref_name}'
            header_sci['HISTORY'] = f'Method: {method} (alternative)'
            
            hdul_out = fits.PrimaryHDU(data=subtracted.astype(np.float32), header=header_sci)
            hdul_out.writeto(output_path, overwrite=True)
            
            logger.info(f"Soustraction réussie (méthode alternative): {output_path}")
            return True, compatibility_info
            
        except ImportError as e:
            logger.error(f"Bibliothèque manquante pour la soustraction alternative: {e}")
            logger.info("Installez reproject avec: pip install reproject")
            return False, compatibility_info
        except Exception as e:
            logger.error(f"Erreur lors de la soustraction alternative: {e}", exc_info=True)
            return False, compatibility_info
    
    def detect_transients(self, subtracted_image: str, threshold_sigma: float = 5.0,
                         min_area: int = 5, max_area: int = 1000,
                         method: str = 'photutils_segmentation', fwhm: Optional[float] = None,
                         deblend: bool = True, **kwargs) -> Optional[Table]:
        """
        Détecte les transitoires dans une image soustraite.
        
        Parameters
        ----------
        subtracted_image : str
            Chemin vers l'image soustraite
        threshold_sigma : float
            Seuil de détection en sigma (défaut: 5.0)
        min_area : int
            Surface minimale d'une détection en pixels (défaut: 5)
        max_area : int
            Surface maximale d'une détection en pixels (défaut: 1000)
        method : str
            Méthode de détection: 'photutils_segmentation', 'photutils_dao', 'photutils_iraf'
            (défaut: 'photutils_segmentation')
        fwhm : float, optional
            FWHM pour les méthodes dao/iraf
        deblend : bool
            Activer le déblending pour la méthode segmentation (défaut: True)
        **kwargs
            Paramètres additionnels pour la détection
        
        Returns
        -------
        Table or None
            Catalogue des transitoires détectés
        """
        try:
            with fits.open(subtracted_image) as hdul:
                data = hdul[0].data
                header = hdul[0].header
            
            # Détection des sources dans l'image soustraite avec la méthode choisie
            kwargs.update({
                'minarea': min_area,
                'deblend': deblend if method == 'photutils_segmentation' else False
            })
            
            sources = self.detect_sources(
                data, 
                header, 
                threshold_sigma=threshold_sigma,
                fwhm=fwhm,
                method=method,
                **kwargs
            )
            
            if sources is None or len(sources) == 0:
                return None
            
            # Filtrer par surface si les colonnes existent
            if 'area' in sources.colnames:
                mask = (sources['area'] >= min_area) & (sources['area'] <= max_area)
                sources = sources[mask]
            elif 'flux' in sources.colnames:
                # Filtrer par flux si pas de colonne area
                flux_threshold = np.percentile(sources['flux'], 5)  # Garder les 95% les plus brillants
                sources = sources[sources['flux'] >= flux_threshold]
            
            return sources
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de transitoires: {e}", exc_info=True)
            return None
    
    def perform_photometry(self, image_path: str, sources: Table,
                          catalog: str = 'gaia', mag_limit: float = 20.0,
                          filter_name: str = 'G', photometry_method: str = 'aperture',
                          fwhm: Optional[float] = None) -> Optional[Table]:
        """
        Effectue la photométrie des sources détectées et la calibre.
        
        Parameters
        ----------
        image_path : str
            Chemin vers l'image
        sources : Table
            Catalogue des sources à mesurer
        catalog : str
            Catalogue de référence pour la calibration ('gaia', 'panstarrs', etc.)
        mag_limit : float
            Magnitude limite du catalogue
        filter_name : str
            Filtre à utiliser pour la calibration :
            - Pour Gaia : 'G', 'G_Bp', 'G_Rp'
            - Pour synthétique : 'U', 'B', 'V', 'R', 'I' (nécessite synphot)
        photometry_method : str
            Méthode de photométrie : 'aperture' ou 'psf'
        fwhm : float, optional
            FWHM estimé pour la photométrie PSF (nécessaire si photometry_method='psf')
        
        Returns
        -------
        Table or None
            Table avec les magnitudes mesurées et calibrées
        """
        try:
            # Charger l'image
            with fits.open(image_path) as hdul:
                image_data = hdul[0].data.astype(float)
                header = hdul[0].header
            
            # Effectuer la photométrie selon la méthode choisie
            if photometry_method == 'psf':
                if not PSF_PHOTOMETRY_AVAILABLE:
                    logger.error("photutils.psf n'est pas disponible. Utilisation de l'aperture photometry.")
                    photometry_method = 'aperture'
                elif fwhm is None:
                    logger.warning("FWHM non fourni pour PSF photometry. Utilisation de l'aperture photometry.")
                    photometry_method = 'aperture'
            
            if photometry_method == 'psf':
                # Photométrie PSF
                sources_with_flux = self._perform_psf_photometry(image_data, sources, fwhm)
            else:
                # Photométrie d'ouverture (méthode par défaut)
                sources_with_flux = self._perform_aperture_photometry(image_data, sources)
            
            # Calibration photométrique
            if catalog == 'gaia':
                calibrated = self._calibrate_with_gaia(sources_with_flux, header, filter_name, mag_limit)
            else:
                # Utiliser STDPipe pour les autres catalogues
                if stdpipe_photometry and hasattr(stdpipe_photometry, 'photometry'):
                    calibrated = stdpipe_photometry.photometry(
                        image_path,
                        sources_with_flux,
                        catalog=catalog,
                        mag_limit=mag_limit
                    )
                else:
                    calibrated = sources_with_flux
            
            return calibrated
                
        except Exception as e:
            logger.error(f"Erreur lors de la photométrie: {e}", exc_info=True)
            return None
    
    def _perform_aperture_photometry(self, image_data: np.ndarray, sources: Table) -> Table:
        """Effectue la photométrie d'ouverture."""
        from photutils.aperture import CircularAperture, aperture_photometry
        
        if len(sources) == 0:
            return sources
        
        # Utiliser une ouverture de 3.0 pixels par défaut
        aper_radius = 3.0
        if 'x' in sources.colnames and 'y' in sources.colnames:
            positions = list(zip(sources['x'], sources['y']))
        elif 'xcentroid' in sources.colnames and 'ycentroid' in sources.colnames:
            positions = list(zip(sources['xcentroid'], sources['ycentroid']))
        else:
            logger.warning("Pas de colonnes x/y trouvées dans sources")
            return sources
        
        apertures = CircularAperture(positions, r=aper_radius)
        phot = aperture_photometry(image_data, apertures)
        
        result = sources.copy()
        result['flux'] = phot['aperture_sum']
        result['fluxerr'] = phot['aperture_sum_err'] if 'aperture_sum_err' in phot.colnames else phot['aperture_sum'] * 0.1
        
        return result
    
    def _perform_psf_photometry(self, image_data: np.ndarray, sources: Table, fwhm: float) -> Table:
        """Effectue la photométrie PSF."""
        if not PSF_PHOTOMETRY_AVAILABLE:
            raise ImportError("photutils.psf n'est pas disponible")
        
        if len(sources) == 0:
            return sources
        
        # Extraire les positions
        if 'x' in sources.colnames and 'y' in sources.colnames:
            positions = np.array([[x, y] for x, y in zip(sources['x'], sources['y'])])
        elif 'xcentroid' in sources.colnames and 'ycentroid' in sources.colnames:
            positions = np.array([[x, y] for x, y in zip(sources['xcentroid'], sources['ycentroid'])])
        else:
            logger.warning("Pas de colonnes x/y trouvées dans sources")
            return sources
        
        # Créer le PRF (Point Response Function) - modèle gaussien intégré
        sigma = fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))  # Conversion FWHM -> sigma
        prf_model = IntegratedGaussianPRF(sigma=sigma)
        
        # Initialiser la photométrie PSF
        psf_phot = DAOPhotPSFPhotometry(
            prf_model,
            fit_shape=(int(2.5 * fwhm), int(2.5 * fwhm)),
            aperture_radius=3.0,
            finder=IRAFStarFinder(threshold=3.0 * np.std(image_data), fwhm=fwhm),
            bkg_estimator=MMMBackground(),
            fitshape=(int(2.5 * fwhm), int(2.5 * fwhm))
        )
        
        # Effectuer la photométrie PSF
        result_table = psf_phot(image_data, positions)
        
        # Créer une table de résultats avec les colonnes attendues
        result = sources.copy()
        if 'flux_fit' in result_table.colnames:
            result['flux'] = result_table['flux_fit']
            result['fluxerr'] = result_table['flux_fit_err'] if 'flux_fit_err' in result_table.colnames else result_table['flux_fit'] * 0.1
        else:
            # Fallback vers aperture photometry si PSF échoue
            logger.warning("PSF photometry échouée, utilisation de l'aperture photometry")
            return self._perform_aperture_photometry(image_data, sources)
        
        return result
    
    def _calibrate_with_gaia(self, sources: Table, header: fits.Header,
                             filter_name: str, mag_limit: float) -> Table:
        """
        Calibre la photométrie avec Gaia eDR3.
        
        Supporte les filtres : 'G', 'G_Bp', 'G_Rp', 'U', 'B', 'V', 'R', 'I'
        """
        if not GAIA_AVAILABLE:
            logger.error("astroquery n'est pas disponible pour requêter Gaia")
            return sources
        
        if len(sources) == 0:
            return sources
        
        # Extraire les coordonnées
        if 'ra' not in sources.colnames or 'dec' not in sources.colnames:
            logger.warning("Pas de coordonnées RA/Dec dans sources")
            return sources
        
        result = sources.copy()
        
        # Requêter Gaia eDR3 pour les étoiles de référence
        try:
            coords = SkyCoord(ra=sources['ra'], dec=sources['dec'], unit=(u.deg, u.deg))
            
            # Requête Gaia avec les colonnes nécessaires
            columns = ['source_id', 'ra', 'dec', 'phot_g_mean_mag', 
                      'phot_bp_mean_mag', 'phot_rp_mean_mag']
            
            # Requête par groupe pour éviter les timeouts
            gaia_mags = []
            for i, coord in enumerate(coords):
                try:
                    job = Gaia.launch_job_async(
                        f"""
                        SELECT TOP 1 
                            source_id, ra, dec, 
                            phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag
                        FROM gaiadr3.gaia_source
                        WHERE 1=CONTAINS(
                            POINT('ICRS', ra, dec),
                            CIRCLE('ICRS', {coord.ra.deg}, {coord.dec.deg}, 0.0001)
                        )
                        AND phot_g_mean_mag <= {mag_limit}
                        ORDER BY phot_g_mean_mag
                        """
                    )
                    results = job.get_results()
                    if len(results) > 0:
                        r = results[0]
                        gaia_mags.append({
                            'source_id': r['source_id'],
                            'G': r['phot_g_mean_mag'],
                            'G_Bp': r['phot_bp_mean_mag'],
                            'G_Rp': r['phot_rp_mean_mag']
                        })
                    else:
                        gaia_mags.append(None)
                except Exception as e:
                    logger.debug(f"Erreur requête Gaia pour source {i}: {e}")
                    gaia_mags.append(None)
            
            # Convertir les magnitudes Gaia en magnitudes du filtre demandé
            catalog_mags = []
            for i, gaia_mag in enumerate(gaia_mags):
                if gaia_mag is None:
                    catalog_mags.append(np.nan)
                    continue
                
                if filter_name in ['G', 'G_Bp', 'G_Rp']:
                    # Utiliser directement la magnitude Gaia
                    catalog_mags.append(gaia_mag.get(filter_name, np.nan))
                elif filter_name in ['U', 'B', 'V', 'R', 'I']:
                    # Conversion avec synphot
                    if SYNPHOT_AVAILABLE:
                        try:
                            synth_mag = self._convert_gaia_to_synth_mag(
                                gaia_mag, filter_name
                            )
                            catalog_mags.append(synth_mag)
                        except Exception as e:
                            logger.debug(f"Erreur conversion synphot: {e}")
                            catalog_mags.append(np.nan)
                    else:
                        logger.warning(f"synphot non disponible pour filtre {filter_name}")
                        catalog_mags.append(np.nan)
                else:
                    logger.warning(f"Filtre {filter_name} non supporté")
                    catalog_mags.append(np.nan)
            
            # Calculer le zero point
            valid_mask = ~np.isnan(catalog_mags) & ~np.isnan(result['flux']) & (result['flux'] > 0)
            if np.sum(valid_mask) >= 3:
                catalog_mags_arr = np.array(catalog_mags)[valid_mask]
                inst_mags = -2.5 * np.log10(result['flux'][valid_mask])
                zero_point = np.median(catalog_mags_arr - inst_mags)
                
                # Appliquer le zero point
                result['mag'] = -2.5 * np.log10(np.maximum(result['flux'], 1.0)) + zero_point
                result['magerr'] = 2.5 / np.log(10) * (result['fluxerr'] / np.maximum(result['flux'], 1.0))
                result['zp'] = zero_point
                result['catalog_mag'] = catalog_mags
            else:
                logger.warning("Pas assez d'étoiles de référence pour calibrer")
                result['mag'] = -2.5 * np.log10(np.maximum(result['flux'], 1.0))
                result['magerr'] = 2.5 / np.log(10) * (result['fluxerr'] / np.maximum(result['flux'], 1.0))
        except Exception as e:
            logger.error(f"Erreur calibration Gaia: {e}", exc_info=True)
            result['mag'] = -2.5 * np.log10(np.maximum(result['flux'], 1.0))
            result['magerr'] = 2.5 / np.log(10) * (result['fluxerr'] / np.maximum(result['flux'], 1.0))
        
        return result
    
    def _convert_gaia_to_synth_mag(self, gaia_mag: Dict[str, float], filter_name: str) -> float:
        """
        Convertit les magnitudes Gaia en magnitudes synthétiques (U, B, V, R, I) avec synphot.
        """
        if not SYNPHOT_AVAILABLE:
            raise ImportError("synphot n'est pas disponible")
        
        # Cette fonction nécessite des spectres d'étoiles, ce qui est complexe
        # Pour l'instant, on utilise des approximations empiriques basées sur les indices de couleur
        
        # Approximation basée sur les transformations de Jordi et al. (2010) et autres
        G = gaia_mag['G']
        G_Bp = gaia_mag.get('G_Bp', np.nan)
        G_Rp = gaia_mag.get('G_Rp', np.nan)
        
        if np.isnan(G_Bp) or np.isnan(G_Rp):
            # Si pas de BP/RP, utiliser seulement G (moins précis)
            if filter_name == 'V':
                return G - 0.02704  # Approximation moyenne
            else:
                logger.warning(f"Conversion {filter_name} impossible sans BP/RP")
                return np.nan
        
        # Indices de couleur
        bp_rp = G_Bp - G_Rp
        
        # Transformations approximatives (à améliorer avec vraie synthèse spectrale)
        if filter_name == 'V':
            # Transformation G -> V (Jordi et al. 2010)
            synth_mag = G - 0.02704 - 0.01424 * bp_rp - 0.2156 * bp_rp**2 + 0.01426 * bp_rp**3
        elif filter_name == 'B':
            # Transformation G_Bp -> B (approximation)
            synth_mag = G_Bp + 0.1  # Approximation grossière
        elif filter_name == 'R':
            # Transformation G_Rp -> R (approximation)
            synth_mag = G_Rp - 0.1  # Approximation grossière
        elif filter_name == 'I':
            # Transformation G_Rp -> I (approximation)
            synth_mag = G_Rp - 0.3  # Approximation grossière
        elif filter_name == 'U':
            # Transformation difficile sans spectre, approximation très grossière
            synth_mag = G_Bp + 0.5  # Approximation très grossière
        else:
            return np.nan
        
        return synth_mag
    
    def calibrate_photometry(self, image_path: str, catalog: str = 'gaia',
                            mag_limit: float = 20.0) -> Dict[str, Any]:
        """
        Calibre photométriquement une image.
        
        Parameters
        ----------
        image_path : str
            Chemin vers l'image
        catalog : str
            Catalogue de référence ('gaia', 'panstarrs', etc.)
        mag_limit : float
            Magnitude limite du catalogue
        
        Returns
        -------
        dict
            Dictionnaire avec zero point, extinction, erreurs, etc.
        """
        try:
            # Calibration photométrique avec STDPipe
            if stdpipe_photometry and hasattr(stdpipe_photometry, 'calibrate'):
                calibration = stdpipe_photometry.calibrate(
                    image_path,
                    catalog=catalog,
                    mag_limit=mag_limit
                )
                return calibration if calibration else {}
            else:
                logger.warning("Fonction calibrate non disponible dans cette version de STDPipe")
                return {}
                
        except Exception as e:
            logger.error(f"Erreur lors de la calibration photométrique: {e}", exc_info=True)
            return {}
