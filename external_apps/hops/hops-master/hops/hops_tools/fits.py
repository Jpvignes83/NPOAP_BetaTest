
__all__ = ['find_fits_files', 'get_fits_data', 'get_fits_data_and_header']

import glob
import numpy as np
from astropy.io import fits as pf

import hops.pylightcurve41 as plc


def _header_to_dict(header):
    return {ff: header[ff] for ff in header if ff not in ['HISTORY', 'COMMENT', '']}


def _select_largest_image_hdu(fits_file):
    """
    Choisit le HDU dont les données forment la plus grande image 2D.
    Évite de prendre un Primary quasi vide ou une vignette alors qu'une Image / CompImageHDU
    contient l'image complète (cas fréquent avec certains masters ou brut multi-extension).
    """
    best_idx = None
    best_size = -1
    for idx in range(len(fits_file)):
        hdu = fits_file[idx]
        if hdu.data is None:
            continue
        try:
            arr = np.asarray(hdu.data, dtype=float)
            if arr.size <= 0:
                continue
            if arr.ndim > 2:
                arr = np.squeeze(arr)
            if arr.ndim != 2:
                continue
            n = int(arr.shape[0] * arr.shape[1])
            if n > best_size:
                best_size = n
                best_idx = idx
        except Exception:
            continue
    if best_idx is None:
        raise ValueError('Aucune image 2D exploitable dans ce FITS ({0} HDUs).'.format(len(fits_file)))
    hdu = fits_file[best_idx]
    fits_data = np.asarray(hdu.data, dtype=float)
    if fits_data.ndim > 2:
        fits_data = np.squeeze(fits_data)
    fits_data = np.array(fits_data, dtype=float)
    fits_header = _header_to_dict(hdu.header)
    return fits_data, fits_header


def find_fits_files(name_identifier):

    if len(name_identifier) > 0:

        fits_files_names = glob.glob('*{0}*.f*t*'.format(name_identifier)) + glob.glob('*{0}*.F*T*'.format(name_identifier))
        fits_files_names = list(np.unique(fits_files_names))
        fits_files_names.sort()
        return fits_files_names

    else:
        return []


def get_fits_data(fits_file_name):

    with plc.open_fits(fits_file_name) as fits_file:

        try:
            fits_data = [fits_file['SCI']]
        except KeyError:
            sci_id = 0
            for sci_id in range(len(fits_file)):
                try:
                    if fits_file[sci_id].data.all():
                        break
                except:
                    pass
            fits_data = [fits_file[sci_id]]

    return fits_data


def get_fits_data_and_header(path):

    with pf.open(path, memmap=False) as fits_file:

        fits_file.verify('fix')

        try:
            sci = fits_file['SCI']
            if sci.data is None:
                raise KeyError('SCI sans données')
            fits_data = np.asarray(sci.data, dtype=float)
            if fits_data.ndim > 2:
                fits_data = np.squeeze(fits_data)
            fits_data = np.array(fits_data, dtype=float)
            fits_header = _header_to_dict(sci.header)
        except KeyError:
            fits_data, fits_header = _select_largest_image_hdu(fits_file)

        # bit10_test = np.sum((fits_data/64.0-np.int_(fits_data/64.0))**2) == 0
        # bit12_test = np.sum((fits_data/16.0-np.int_(fits_data/16.0))**2) == 0
        # bit14_test = np.sum((fits_data/4.0-np.int_(fits_data/4.0))**2) == 0
        #
        # if bit10_test:
        #     fits_data = fits_data/64.0
        #     fits_header['BITPIX'] = 10
        # elif bit12_test:
        #     fits_data = fits_data/16.0
        #     fits_header['BITPIX'] = 12
        # elif bit14_test:
        #     fits_data = fits_data/4.0
        #     fits_header['BITPIX'] = 14

        fits_data[np.where(np.isnan(fits_data))] = 1
        fits_data[np.where(fits_data == 0)] = 1

    return np.array(fits_data, dtype=float), fits_header


