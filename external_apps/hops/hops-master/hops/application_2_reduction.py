
import os
import sys
import time
import numpy as np
import shutil
import exoclock
import hops.pylightcurve41 as plc

from astropy.io import fits as pf

from hops.hops_tools.fits import *
from hops.hops_tools.image_analysis import image_mean_std, image_burn_limit, image_psf, bin_frame
from hops.application_windows import MainWindow


def _hops_work_directory(log):
    """Répertoire de travail HOPS (absolu), ou None si non défini."""
    d = log.get_param('directory')
    if d is None or str(d).strip() == '' or str(d) == 'Choose Directory':
        return None
    return os.path.abspath(str(d))


def _safe_get_param(log, key, default=None):
    """
    Accès sûr à log.get_param(key) avec valeur par défaut si la clé
    n'existe pas encore dans le profil/local-log.
    """
    try:
        return log.get_param(key)
    except KeyError:
        return default


def _find_fits_paths_in_dir(name_identifier, base_dir, default_work_dir):
    """
    Cherche des FITS correspondant à name_identifier dans base_dir
    et renvoie des chemins absolus normalisés. Si base_dir est vide
    ou None, retombe sur le comportement HOPS historique via
    _resolve_fits_paths + find_fits_files dans default_work_dir.
    """
    if not name_identifier:
        return []

    # Pas de dossier spécifique : comportement identique à HOPS original
    if not base_dir:
        return _resolve_fits_paths(find_fits_files(name_identifier), default_work_dir)

    prev_cwd = os.getcwd()
    try:
        os.chdir(base_dir)
        names = find_fits_files(name_identifier)
        resolved = []
        for p in names:
            s = os.path.normpath(os.path.abspath(str(p)))
            resolved.append(s)
        return resolved
    finally:
        os.chdir(prev_cwd)


def _resolve_fits_paths(paths, work_dir):
    """
    Normalise les chemins renvoyés par glob (souvent relatifs au répertoire HOPS).
    Nécessaire lorsque __init__ s'exécute avec un cwd différent (ex. NPOAP intégré).
    """
    resolved = []
    for p in paths:
        s = str(p)
        if work_dir and not os.path.isabs(s):
            resolved.append(os.path.normpath(os.path.join(work_dir, s)))
        else:
            resolved.append(os.path.normpath(os.path.abspath(s)))
    return resolved


def _exptime_filename_tag(seconds):
    """Fragment sûr pour un nom de fichier (secondes d'exposition)."""
    if seconds is None:
        return 'NA'
    try:
        x = float(seconds)
    except (TypeError, ValueError):
        return 'NA'
    if np.isnan(x):
        return 'NA'
    ax = abs(x)
    if x != 0.0 and (ax < 1e-4 or ax >= 1e5):
        s = '{:.3e}'.format(x)
    else:
        s = '{:.6g}'.format(x)
    for c in ('\\', '/', ':', '*', '?', '"', '<', '>', '|'):
        s = s.replace(c, '_')
    return s


class ReductionWindow(MainWindow):

    def __init__(self, log):

        MainWindow.__init__(self, log, name='HOPS - Reduction', position=2)

        self.colour_camera_mode = self.log.get_param('colour_camera_mode')
        self.scale_darks_by_exposure = bool(self.log.get_param('scale_darks_by_exposure'))

        self.file_info = []

        work_dir = _hops_work_directory(self.log)

        obs_dir = _safe_get_param(self.log, 'observation_directory', work_dir)
        bias_dir = _safe_get_param(self.log, 'bias_directory', work_dir)
        dark_dir = _safe_get_param(self.log, 'dark_directory', work_dir)
        darkf_dir = _safe_get_param(self.log, 'darkf_directory', dark_dir or work_dir)
        flat_dir = _safe_get_param(self.log, 'flat_directory', work_dir)

        self.bias_files = _find_fits_paths_in_dir(self.log.get_param('bias_files'), bias_dir, work_dir)
        self.bias_frames = []
        self.bias_frames_exp = []
        self.bias_counter = 0

        self.dark_files = _find_fits_paths_in_dir(self.log.get_param('dark_files'), dark_dir, work_dir)
        self.dark_frames = []
        self.dark_frames_exp = []
        self.dark_counter = 0
        self.dark_median_exptime = float('nan')

        # dark-flat: répertoire dédié si défini, sinon même répertoire que les darks
        self.darkf_files = _find_fits_paths_in_dir(self.log.get_param('darkf_files'), darkf_dir, work_dir)
        self.darkf_frames = []
        self.darkf_frames_exp = []
        self.darkf_counter = 0

        self.flat_files = _find_fits_paths_in_dir(self.log.get_param('flat_files'), flat_dir, work_dir)
        self.flat_frames = []
        self.flat_frames_exp = []
        self.flat_counter = 0

        # Observation files: même logique répertoire + mot-clé que dans la fenêtre Data & Target
        self.science_files = _find_fits_paths_in_dir(self.log.get_param('observation_files'), obs_dir, work_dir)
        self.all_frames = {}
        self.science_counter = 0
        self.ref_stars = []
        self.psf = 10

        location_string = self.log.get_param('location').split(' ')
        self.observatory = exoclock.Observatory(exoclock.Degrees(location_string[0]), 
                                                exoclock.Degrees(location_string[1]))
        ra_dec_string = self.log.get_param('target_ra_dec').split(' ')
        self.target = exoclock.FixedTarget(exoclock.Hours(ra_dec_string[0]), exoclock.Degrees(ra_dec_string[1]))

        self.filter = self.log.get_param('filter')

        self._science_paths_norm = set(
            os.path.normpath(os.path.abspath(str(p))) for p in self.science_files)

        test_fits_name = self.science_files[0]
        test_fits_data, test_fits_header = self.get_fits_data_and_header(test_fits_name)

        t0 = time.time()
        _ = plc.mean_std_from_median_mad(test_fits_data)
        self.fr_time = int(2000 * (time.time()-t0))

        self.progress_figure = self.FitsWindow(fits_data=test_fits_data, fits_header=test_fits_header,
                                               input_name=self.science_files[0])
        self.progress_bias = self.Progressbar(task="Loading bias frames")
        self.progress_dark = self.Progressbar(task="Loading dark frames")
        self.progress_darkf = self.Progressbar(task="Loading dark-flat frames")
        self.progress_flat = self.Progressbar(task="Loading flat frames")
        self.progress_science = self.Progressbar(task="Reducing science frames and calculating statistics")
        self.progress_science_loop = self.CheckButton(text='Show all frames', initial=0)

        setup_window = [
            [[self.progress_figure, 0, 2]]
        ]

        if len(self.bias_files) > 0:
            setup_window.append([[self.progress_bias, 0, 2]])
        if len(self.dark_files) > 0:
            setup_window.append([[self.progress_dark, 0, 2]])
        if len(self.darkf_files) > 0:
            setup_window.append([[self.progress_darkf, 0, 2]])
        if len(self.flat_files) > 0:
            setup_window.append([[self.progress_flat, 0, 2]])

        setup_window += [
            [[self.progress_science, 0], [self.progress_science_loop, 1]],
            [[self.Button(text='STOP REDUCTION & RETURN TO MAIN MENU', command=self.trigger_exit), 0, 2]],
            []
        ]

        self.setup_window(setup_window)

        self.set_close_button_function(self.trigger_exit)

    def _reduced_data_dir(self):
        """Chemin absolu du dossier REDUCED_DATA (toujours sous le répertoire projet Data & Target)."""
        work = _hops_work_directory(self.log)
        if work:
            return os.path.normpath(os.path.join(work, self.log.reduction_directory))
        return os.path.abspath(self.log.reduction_directory)

    def get_fits_data_and_header(self, fits_name):

        fits_name = str(fits_name)
        fits_data, fits_header = get_fits_data_and_header(fits_name)
        path_ref = os.path.normpath(os.path.abspath(fits_name))
        is_science_frame = path_ref in self._science_paths_norm

        if self.file_info == []:
            self.file_info = [len(fits_data[0]), len(fits_data), fits_header['BITPIX']]
        else:
            bad_size = (
                len(fits_data[0]) != self.file_info[0]
                or self.file_info[1] != len(fits_data))
            bad_bitpix = self.file_info[2] != fits_header['BITPIX']
            if bad_size or (bad_bitpix and is_science_frame):
                wx, hy = len(fits_data[0]), len(fits_data)
                rx, ry = self.file_info[0], self.file_info[1]
                if bad_size:
                    body = (
                        '{0}\n\n'
                        'Taille attendue (réf. science, première image) : {1} × {2} px\n'
                        'Taille de ce fichier : {3} × {4} px\n\n'
                        'BITPIX : {5} (réf. science : {6})\n\n'
                        'Les masters / calibration doivent avoir exactement la même '
                        'largeur et hauteur que les images science.\n'
                        'Réexportez le master au bon format ou retirez ce fichier des listes bias/dark/flat.'
                    ).format(
                        fits_name, rx, ry, wx, hy,
                        fits_header['BITPIX'], self.file_info[2])
                else:
                    body = (
                        '{0}\n\n'
                        'BITPIX incompatible pour une image science.\nCe fichier : {1}-bit  |  '
                        'référence : {2}-bit\n\nReduction will terminate, please check your files!'
                    ).format(fits_name, fits_header['BITPIX'], self.file_info[2])
                self.showinfo('Inconsistent image size', body)
                self.show()
                self.exit = True
                self.after(self.reduce_science)
            elif bad_bitpix and not is_science_frame:
                msg = (
                    'Calibration {0}: BITPIX fichier = {1}, science = {2} — '
                    'les pixels sont lus en float ; poursuite de la réduction.').format(
                        fits_name, fits_header['BITPIX'], self.file_info[2])
                print('Avertissement:', msg)
                try:
                    self.log.runtime('Reduction: {0}'.format(msg), level='WARNING')
                except Exception:
                    pass

        return fits_data, fits_header

    # define functions

    def run_reduction(self):

        if self.log.get_param('reduction_complete'):
            if self.askyesno('Overwrite files', 'Reduction has been completed, do you want to run again?'):
                self.log.set_param('reduction_complete', False)
                self.log.save_local_log()
            else:
                self.log.set_param('proceed', True)

        if not self.log.get_param('reduction_complete'):

            red_dir = self._reduced_data_dir()
            if os.path.isdir(red_dir):
                shutil.rmtree(red_dir)
            os.makedirs(red_dir, exist_ok=True)
            print('HOPS réduction — sortie (masters + science) : {0}'.format(red_dir))
            try:
                self.log.runtime('Reduction: output directory {0}'.format(red_dir), level='INFO')
            except Exception:
                pass

            self.progress_science.show_message(
                'Calibration (bias / dark / flat) — la barre science avance après cette étape')
            self.after(self.get_bias)

        else:
            self.close()

    # reduction routines

    def _save_master_frame(self, master_base, master_frame, method_label='', exptime_sec=None,
                           legacy_filenames=None):
        """
        Sauvegarde un master FITS sous <master_base>_exp<tag>.fits avec EXPTIME dans l'en-tête.
        master_base: sans extension, ex. 'master_bias', 'master_dark', 'master_dark_flat', 'master_flat'.
        legacy_filenames: copie(s) du fichier (ex. ['master_darkf.fits'] pour compatibilité HOPS).
        """
        try:
            if isinstance(master_frame, np.ndarray):
                frame_to_save = master_frame
            elif np.isscalar(master_frame):
                # Fallback: when no calibration files are provided, HOPS uses scalar defaults.
                # Persist them as constant images so expected master_*.fits files are still produced.
                width = int(self.file_info[0]) if self.file_info else 0
                height = int(self.file_info[1]) if self.file_info else 0
                if width > 0 and height > 0:
                    frame_to_save = np.full((height, width), float(master_frame), dtype=np.float32)
                else:
                    return
            else:
                return
            red_dir = self._reduced_data_dir()
            os.makedirs(red_dir, exist_ok=True)
            tag = _exptime_filename_tag(exptime_sec)
            master_name = '{0}_exp{1}.fits'.format(master_base, tag)
            out_path = os.path.join(red_dir, master_name)
            primary = pf.PrimaryHDU(data=np.array(frame_to_save, dtype=np.float32))
            exp_key = self.log.get_param('exposure_time_key')
            if exp_key:
                try:
                    if exptime_sec is not None and not (isinstance(exptime_sec, float) and np.isnan(exptime_sec)):
                        primary.header[exp_key] = float(exptime_sec)
                    else:
                        primary.header[exp_key] = 0.0
                except Exception:
                    pass
            if method_label:
                primary.header.set('METHOD', str(method_label))
            primary.header.set('HOPSSTEP', 'REDUCTION')
            plc.save_fits(pf.HDUList([primary]), out_path)
            print('Saved master:', out_path)
            try:
                self.log.runtime('Reduction: saved master {0}'.format(out_path), level='INFO')
            except Exception:
                pass
            if legacy_filenames:
                for leg in legacy_filenames:
                    legacy_path = os.path.join(red_dir, leg)
                    shutil.copyfile(out_path, legacy_path)
                    print('Saved master (alias):', legacy_path)
                    try:
                        self.log.runtime('Reduction: saved master alias {0}'.format(legacy_path), level='INFO')
                    except Exception:
                        pass
        except Exception as e:
            print('Failed to save {0}: {1}'.format(master_base, e))
            try:
                self.log.runtime('Reduction: failed to save master {0}: {1}'.format(master_base, e), level='WARNING')
            except Exception:
                pass

    def _dark_scale_for_exptime(self, fits_header):
        if not self.scale_darks_by_exposure:
            return 1.0
        scale = float(fits_header[self.log.get_param('exposure_time_key')]) - float(self.bias_frames_exp)
        if abs(scale) < 1e-30:
            return 1.0
        return scale

    def get_bias(self):

        if self.exit or len(self.bias_files) == 0:
            self.after(self.get_master_bias)

        else:

            if self.bias_counter == 0:
                self.progress_bias.initiate(len(self.bias_files))

            fits_data, fits_header = self.get_fits_data_and_header(self.bias_files[self.bias_counter])
            self.bias_frames.append(np.ones_like(fits_data) * fits_data)

            try:
                bias_exptime = fits_header[self.log.get_param('exposure_time_key')]
            except:
                bias_exptime = 0
            self.bias_frames_exp.append(bias_exptime)

            print('{0}: median = {1}, exp.time = {2}'.format(self.bias_files[self.bias_counter], np.nanmedian(self.bias_frames[-1]), bias_exptime))

            self.progress_bias.update()
            self.bias_counter += 1

            if self.bias_counter >= len(self.bias_files):
                self.progress_bias.show_message('Calculating master bias...')
                self.after(self.get_master_bias)
            else:
                self.after(self.get_bias)

    def get_master_bias(self):

        if self.exit:
            self.after(self.get_dark)

        else:

            if len(self.bias_frames) > 0:

                med_exp = float(np.median(np.asarray(self.bias_frames_exp, dtype=float)))
                consistent_exp_time = np.asarray(self.bias_frames_exp, dtype=float) == med_exp

                self.bias_frames = [self.bias_frames[ff] for ff in range(len(self.bias_frames)) if consistent_exp_time[ff]]

                if self.log.get_param('master_bias_method') == 'median':
                    self.master_bias = np.array([np.nanmedian([xx[ff] for xx in self.bias_frames], 0) for ff in range(len(self.bias_frames[0]))])
                elif self.log.get_param('master_bias_method') == 'mean':
                    self.master_bias = np.array([np.nanmean([xx[ff] for xx in self.bias_frames], 0) for ff in range(len(self.bias_frames[0]))])
                else:
                    self.master_bias = np.array([np.nanmedian([xx[ff] for xx in self.bias_frames], 0) for ff in range(len(self.bias_frames[0]))])

                self.bias_frames_exp = np.median(self.bias_frames_exp)

            else:
                self.master_bias = 0.0
                self.bias_frames_exp = 0.0

            print('Median Bias: ', round(np.nanmedian(self.master_bias), 3))
            print('Bias exp. time: ', self.bias_frames_exp)
            self._save_master_frame(
                'master_bias',
                self.master_bias,
                method_label=self.log.get_param('master_bias_method'),
                exptime_sec=float(self.bias_frames_exp),
            )
            self.progress_bias.show_message('Calculating master bias... Completed!')

            self.after(self.get_dark)

    def get_dark(self):

        if self.exit or len(self.dark_files) == 0:
            self.after(self.get_master_dark)

        else:

            if self.dark_counter == 0:
                self.progress_dark.initiate(len(self.dark_files))

            fits_data, fits_header = self.get_fits_data_and_header(self.dark_files[self.dark_counter])
            dark_frame = np.ones_like(fits_data) * fits_data
            dark_scale = self._dark_scale_for_exptime(fits_header)
            try:
                dark_exptime = float(fits_header[self.log.get_param('exposure_time_key')])
            except Exception:
                dark_exptime = 0.0
            self.dark_frames_exp.append(dark_exptime)
            self.dark_frames.append((dark_frame - self.master_bias) / dark_scale)

            print('{0}: median = {1}'.format(self.dark_files[self.dark_counter], np.nanmedian(self.dark_frames[-1])))

            self.progress_dark.update()
            self.dark_counter += 1

            if self.dark_counter >= len(self.dark_files):
                self.progress_dark.show_message('Calculating master dark...')
                self.after(self.get_master_dark)
            else:
                self.after(self.get_dark)

    def get_master_dark(self):

        if self.exit:
            self.after(self.get_flat)
        else:

            if len(self.dark_frames) > 0:
                if self.log.get_param('master_dark_method') == 'median':
                    self.master_dark = np.array([np.nanmedian([xx[ff] for xx in self.dark_frames], 0) for ff in range(len(self.dark_frames[0]))])
                elif self.log.get_param('master_dark_method') == 'mean':
                    self.master_dark = np.array([np.nanmean([xx[ff] for xx in self.dark_frames], 0) for ff in range(len(self.dark_frames[0]))])
                else:
                    self.master_dark = np.array([np.nanmedian([xx[ff] for xx in self.dark_frames], 0) for ff in range(len(self.dark_frames[0]))])
                self.dark_median_exptime = float(np.median(np.asarray(self.dark_frames_exp, dtype=float)))
            else:
                self.master_dark = 0.0
                self.dark_median_exptime = float('nan')

            print('Median Dark: ', round(np.nanmedian(self.master_dark), 3))
            self._save_master_frame(
                'master_dark',
                self.master_dark,
                method_label=self.log.get_param('master_dark_method'),
                exptime_sec=self.dark_median_exptime,
            )
            self.progress_dark.show_message('Calculating master dark... Completed!')

            self.after(self.get_darkf)

    def get_darkf(self):

        if self.exit or len(self.darkf_files) == 0:
            self.after(self.get_master_darkf)

        else:

            if self.darkf_counter == 0:
                self.progress_darkf.initiate(len(self.darkf_files))

            fits_data, fits_header = self.get_fits_data_and_header(self.darkf_files[self.darkf_counter])
            darkf_frame = np.ones_like(fits_data) * fits_data
            darkf_scale = self._dark_scale_for_exptime(fits_header)
            try:
                darkf_exptime = float(fits_header[self.log.get_param('exposure_time_key')])
            except Exception:
                darkf_exptime = 0.0
            self.darkf_frames_exp.append(darkf_exptime)
            self.darkf_frames.append((darkf_frame - self.master_bias) / darkf_scale)

            print('{0}: median = {1}'.format(self.darkf_files[self.darkf_counter], np.nanmedian(self.darkf_frames[-1])))

            self.progress_darkf.update()
            self.darkf_counter += 1

            if self.darkf_counter >= len(self.darkf_files):
                self.progress_darkf.show_message('Calculating master dark-flat...')
                self.after(self.get_master_darkf)
            else:
                self.after(self.get_darkf)

    def get_master_darkf(self):

        if self.exit:
            self.after(self.get_flat)
        else:

            if len(self.darkf_frames) > 0:
                if self.log.get_param('master_darkf_method') == 'median':
                    self.master_darkf = np.array([np.nanmedian([xx[ff] for xx in self.darkf_frames], 0) for ff in range(len(self.darkf_frames[0]))])
                elif self.log.get_param('master_darkf_method') == 'mean':
                    self.master_darkf = np.array([np.nanmean([xx[ff] for xx in self.darkf_frames], 0) for ff in range(len(self.darkf_frames[0]))])
                else:
                    self.master_darkf = np.array([np.nanmedian([xx[ff] for xx in self.darkf_frames], 0) for ff in range(len(self.darkf_frames[0]))])
            else:
                self.master_darkf = self.master_dark

            if len(self.darkf_frames) > 0:
                darkf_median_exptime = float(np.median(np.asarray(self.darkf_frames_exp, dtype=float)))
            else:
                darkf_median_exptime = self.dark_median_exptime

            print('Median Dark-Flat: ', round(np.nanmedian(self.master_darkf), 3))
            self._save_master_frame(
                'master_dark_flat',
                self.master_darkf,
                method_label=self.log.get_param('master_darkf_method'),
                exptime_sec=darkf_median_exptime,
                legacy_filenames=['master_darkf.fits'],
            )
            self.progress_darkf.show_message('Calculating master dark-flat... Completed!')

            self.after(self.get_flat)

    def get_flat(self):

        if self.exit or len(self.flat_files) == 0:
            self.after(self.get_master_flat)

        else:

            if self.flat_counter == 0:
                self.progress_flat.initiate(len(self.flat_files))

            fits_data, fits_header = self.get_fits_data_and_header(self.flat_files[self.flat_counter])
            flat_frame = np.ones_like(fits_data) * fits_data
            darkf_scale = self._dark_scale_for_exptime(fits_header)
            try:
                flat_exptime = float(fits_header[self.log.get_param('exposure_time_key')])
            except Exception:
                flat_exptime = 0.0
            self.flat_frames_exp.append(flat_exptime)

            self.flat_frames.append(
                flat_frame - self.master_bias - darkf_scale * self.master_darkf)

            print('{0}: median = {1}'.format(self.flat_files[self.flat_counter], np.nanmedian(self.flat_frames[-1])))

            self.progress_flat.update()
            self.flat_counter += 1

            if self.flat_counter >= len(self.flat_files):
                self.progress_flat.show_message('Calculating master flat...')
                self.after(self.get_master_flat)
            else:
                self.after(self.get_flat)

    def get_master_flat(self):

        if self.exit:
            self.after(self.reduce_science)

        else:

            if len(self.flat_frames) > 0:
                if self.log.get_param('master_flat_method') == 'mean':
                    flat_frames = [ff / np.nanmean(ff) for ff in self.flat_frames]
                    self.master_flat = np.array([np.nanmean([xx[ff] for xx in flat_frames], 0) for ff in range(len(flat_frames[0]))])
                else:
                    flat_frames = [ff / np.nanmedian(ff) for ff in self.flat_frames]
                    self.master_flat = np.array([np.nanmedian([xx[ff] for xx in flat_frames], 0) for ff in range(len(flat_frames[0]))])
                print('Median Flat: ', round(np.nanmedian(self.master_flat), 3))

                if self.colour_camera_mode:
                    self.master_flat[::2, ::2] = self.master_flat[::2, ::2] / np.nanmedian(self.master_flat[::2, ::2])
                    self.master_flat[::2, 1::2] = self.master_flat[::2, 1::2] / np.nanmedian(self.master_flat[::2, 1::2])
                    self.master_flat[1::2, ::2] = self.master_flat[1::2, ::2] / np.nanmedian(self.master_flat[1::2, ::2])
                    self.master_flat[1::2, 1::2] = self.master_flat[1::2, 1::2] / np.nanmedian(self.master_flat[1::2, 1::2])
                else:
                    self.master_flat = self.master_flat / np.nanmedian(self.master_flat)

                self.master_flat = np.where(self.master_flat == 0, 1, self.master_flat)

            else:
                self.master_flat = 1.0

            if len(self.flat_frames_exp) > 0:
                flat_median_exptime = float(np.median(np.asarray(self.flat_frames_exp, dtype=float)))
            else:
                flat_median_exptime = float('nan')

            self._save_master_frame(
                'master_flat',
                self.master_flat,
                method_label=self.log.get_param('master_flat_method'),
                exptime_sec=flat_median_exptime,
            )
            self.progress_flat.show_message('Calculating master flat... Completed!')
            sys.setrecursionlimit(100 * len(self.science_files))
            self.after(self.reduce_science)

    def reduce_science(self):

        timing = False
        # timing = True

        # correct each observation_files file

        if self.exit:
            self.after(self.save)

        else:

            if self.science_counter == 0:
                self.progress_science.initiate(len(self.science_files))

            science_file = self.science_files[self.science_counter]

            # correct it with master bias_files, master dark_files and master flat_files
            t00 = time.time()
            t0 = time.time()
            fits_data, fits_header = self.get_fits_data_and_header(science_file)

            if timing:
                print('Loading: ', time.time()-t0)

            t0 = time.time()

            saturation = image_burn_limit(fits_header, key=self.log.hops_saturation_key)
            exp_time = float(fits_header[self.log.get_param('exposure_time_key')])
            centroids_snr = self.log.get_param('centroids_snr')
            stars_snr = self.log.get_param('stars_snr')
            psf_guess = self.log.get_param('psf_guess')
            data_frame = np.ones_like(fits_data) * fits_data
            dq_frame = np.where(data_frame == saturation, 1, 0)
            dark_scale = self._dark_scale_for_exptime(fits_header)
            data_frame = (data_frame - self.master_bias - dark_scale * self.master_dark) / self.master_flat
            data_frame[np.where(np.isnan(data_frame))] = 0

            if timing:
                print('Reduction: ', time.time()-t0)

            t0 = time.time()

            crop_x1 = int(max(0, self.log.get_param('crop_x1')))
            crop_x2 = int(min(self.log.get_param('crop_x2'), len(data_frame[0])))
            crop_y1 = int(max(0, self.log.get_param('crop_y1')))
            crop_y2 = int(min(self.log.get_param('crop_y2'), len(data_frame)))

            if crop_x2 == 0:
                crop_x2 = len(data_frame[0])
            if crop_y2 == 0:
                crop_y2 = len(data_frame)

            if not (np.array([crop_x1, crop_x2, crop_y1, crop_y2]) == np.array([0, len(data_frame[0]), 0, len(data_frame)])).all():
                data_frame = data_frame[crop_y1: crop_y2]
                data_frame = data_frame[:, crop_x1: crop_x2]
                dq_frame = dq_frame[crop_y1: crop_y2]
                dq_frame = dq_frame[:, crop_x1: crop_x2]

            crop_edge_pixels = int(self.log.get_param('crop_edge_pixels'))
            if crop_edge_pixels > 0:
                data_frame = data_frame[crop_edge_pixels: -crop_edge_pixels, crop_edge_pixels: -crop_edge_pixels]
                dq_frame = dq_frame[crop_edge_pixels: -crop_edge_pixels, crop_edge_pixels: -crop_edge_pixels]

            bin_fits = self.log.get_param('bin_fits')
            if bin_fits > 1:
                data_frame = bin_frame(data_frame, bin_fits)
                saturation = saturation * bin_fits * bin_fits
                dq_frame = bin_frame(dq_frame, bin_fits)
                dq_frame = np.where(dq_frame > 0, 1, 0)

            data_frame[np.where(dq_frame > 0)] = saturation

            if timing:
                print('Binning and cropping: ', time.time()-t0)

            if self.science_counter == 0:
                t0 = time.time()
                _ = plc.mean_std_from_median_mad(data_frame)
                self.fr_time = int(1000 * (time.time()-t0))

            t0 = time.time()
            mean, std = image_mean_std(data_frame, samples=10000, mad_filter=5.0)
            if timing:
                print('SKY: ', time.time()-t0)

            t0 = time.time()
            psf = image_psf(data_frame, fits_header, mean, std, 0.8 * saturation,
                            centroids_snr=centroids_snr, stars_snr=stars_snr, psf_guess=psf_guess)
            if np.isnan(psf):
                psf = 10
                skip = True
            else:
                skip = False
            if timing:
                print('PSF: ', time.time()-t0)

            t0 = time.time()
            if self.log.get_param('observation_date_key') == self.log.get_param('observation_time_key'):
                observation_time = ' '.join(fits_header[self.log.get_param('observation_date_key')].split('T'))
            else:
                observation_time = ' '.join([fits_header[self.log.get_param('observation_date_key')].split('T')[0],
                                             fits_header[self.log.get_param('observation_time_key')]])

            try:
                observation_time = exoclock.Moment(utc=observation_time)
                if self.log.get_param('time_stamp') == 'exposure start':
                    pass
                elif self.log.get_param('time_stamp') == 'mid-exposure':
                    observation_time = exoclock.Moment(jd_utc=observation_time.jd_utc() - 0.5 * exp_time / 24.0 / 3600.0)
                elif self.log.get_param('time_stamp') == 'exposure end':
                    observation_time = exoclock.Moment(jd_utc=observation_time.jd_utc() - exp_time / 24.0 / 3600.0)
                else:
                    raise RuntimeError('Not acceptable time stamp.')

                julian_date = observation_time.jd_utc()
                airmass = self.observatory.airmass(self.target, observation_time)

                # write the new fits file
                # important to keep it like this for windows!

                time_in_file = observation_time.utc().isoformat()
                time_in_file = time_in_file.split('.')[0]
                time_in_file = time_in_file.replace('-', '_').replace(':', '_').replace('T', '_')

                new_name = '{0}{1}_{2}'.format(self.log.reduction_prefix, time_in_file, science_file.split(os.sep)[-1])
                primary = pf.PrimaryHDU()
                image = pf.CompImageHDU()
                image.data = np.array(data_frame, dtype=np.int32)
                image.header.set('BITPIX', fits_header['BITPIX'])
                image.header.set('NAXIS1', len(fits_data[0]))
                image.header.set('NAXIS2', len(fits_data))
                image.header.set('XBINNING', bin_fits)
                image.header.set('YBINNING', bin_fits)
                image.header.set('BZERO',  0)
                image.header.set('BSCALE', 1)
                image.header.set(self.log.hops_observatory_latitude_key, self.observatory.latitude.deg_coord())
                image.header.set(self.log.hops_observatory_longitude_key, self.observatory.longitude.deg())
                image.header.set(self.log.hops_target_ra_key, self.target.ra.deg())
                image.header.set(self.log.hops_target_dec_key, self.target.dec.deg_coord())
                image.header.set(self.log.hops_datetime_key, observation_time.utc().isoformat())
                image.header.set(self.log.hops_exposure_key, exp_time)
                image.header.set(self.log.hops_filter_key, self.filter)
                image.header.set(self.log.time_key, julian_date)
                image.header.set(self.log.airmass_key, airmass)
                image.header.set(self.log.mean_key, mean)
                image.header.set(self.log.std_key, std)
                image.header.set(self.log.hops_saturation_key, saturation)
                image.header.set(self.log.psf_key, psf)
                image.header.set(self.log.skip_key, skip)
                image.header.set(self.log.align_x0_key, False)
                image.header.set(self.log.align_y0_key, False)
                image.header.set(self.log.align_u0_key, False)
                image.header.set(self.log.align_u0_key, False)
                fits_header[self.log.mean_key] = mean
                fits_header[self.log.std_key] = std

                plc.save_fits(pf.HDUList([primary, image]), os.path.join(self._reduced_data_dir(), new_name))

                self.all_frames[new_name] = {
                    self.log.mean_key: mean,
                    self.log.std_key: std,
                    self.log.psf_key: psf,
                    self.log.time_key: julian_date,
                    self.log.airmass_key: airmass,
                    self.log.get_param('exposure_time_key'): exp_time,
                    self.log.skip_key: skip,
                    self.log.align_x0_key: False,
                    self.log.align_y0_key: False,
                    self.log.align_u0_key: False,
                }

                if timing:
                    print('Saving: ', time.time()-t0)
                    print('Total: ', time.time()-t00)

                self.progress_science.update()
                self.science_counter += 1

                if self.science_counter >= len(self.science_files):
                    self.after(self.save)
                else:
                    if self.progress_science_loop.get() or self.science_counter == 1:
                        self.progress_figure.load_fits(data_frame, fits_header, new_name)
                        self.progress_figure.draw()

                    if len(self.jobs) > self.jobs_completed + 1:
                        self.fr_time += 10

            except exoclock.errors.ExoClockInputError:
                print('Bad time data, skipping frame: ', science_file)
                print(observation_time)

                self.science_counter += 1

                pass

            self.after(self.reduce_science, time=self.fr_time)

    def save(self):

        if self.exit:
            self.close()
        else:
            plc.save_dict(self.all_frames, self.log.all_frames)
            self.log.set_param('reduction_complete', True)
            self.log.set_param('reduction_version', self.log.version)
            self.log.save_local_log()
            self.log.set_param('proceed', True)
            self.close()
