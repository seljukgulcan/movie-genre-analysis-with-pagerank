import urllib.request
import zipfile
import os
import shutil
from pathlib import Path

URL_ML_SMALL = 'http://files.grouplens.org/datasets/movielens/ml-latest-small.zip'
URL_ML_25M = 'http://files.grouplens.org/datasets/movielens/ml-25m.zip'
TEMP_FILE = 'temp.zip'

DIR_ML_25M = 'ml-25m'
DIR_ML_SMALL = 'ml-latest-small'


def download_ml_small(target_filename='ratings.csv', *, force_download=False):
    """
    Downloads movielens small dataset
    :param target_filename: If target file is already there, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:target filename
    """

    return _download_ml_dataset(URL_ML_SMALL, DIR_ML_SMALL,
                                target_filename=target_filename, force_download=force_download)


def download_ml_25m(target_filename='ratings.csv', *, force_download=False):
    """
    Downloads movielens-25m dataset
    :param target_filename: If target file is already there, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:target filename
    """

    return _download_ml_dataset(URL_ML_25M, DIR_ML_25M,
                                target_filename=target_filename, force_download=force_download)


def _download_ml_dataset(url, directory_name, target_filename, *, force_download=False):
    """
    Downloads a movielens dataset
    :param target_filename: If target file is already there, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:target filename
    """

    is_target_file_exist = os.path.isfile(target_filename)

    if is_target_file_exist and not force_download:
        return target_filename

    urllib.request.urlretrieve(url, TEMP_FILE)
    with zipfile.ZipFile(TEMP_FILE, 'r') as zip_file:
        zip_file.extractall('./')

    os.rename(f'{directory_name}/ratings.csv', target_filename)

    target_directory = Path(target_filename).parent
    os.rename(f'{directory_name}/movies.csv', target_directory / 'movies.csv')
    os.rename(f'{directory_name}/links.csv', target_directory / 'links.csv')

    os.remove(TEMP_FILE)
    shutil.rmtree(directory_name)

    return target_filename
