import urllib.request
import zipfile
import shutil
from pathlib import Path

URL_ML_SMALL = 'http://files.grouplens.org/datasets/movielens/ml-latest-small.zip'
URL_ML_25M = 'http://files.grouplens.org/datasets/movielens/ml-25m.zip'
TEMP_FILE = Path('temp.zip')

DIR_ML_25M = 'ml-25m'
DIR_ML_SMALL = 'ml-latest-small'


def download_ml_small(base_dir='./', *, force_download=False):
    """
    Downloads movielens small dataset
    :param base_dir: If rating.csv is already in base_dir, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:target filename
    """

    return _download_ml_dataset(URL_ML_SMALL, DIR_ML_SMALL,
                                base_dir=base_dir, force_download=force_download)


def download_ml_25m(base_dir='./', *, force_download=False):
    """
    Downloads movielens-25m dataset
    :param base_dir: If rating.csv is already in base_dir, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:target filename
    """

    return _download_ml_dataset(URL_ML_25M, DIR_ML_25M,
                                base_dir=base_dir, force_download=force_download)


def _download_ml_dataset(url, download_dir, base_dir, *, force_download=False):
    """
    Downloads a movielens dataset
    :param base_dir: If rating.csv is already in base_dir, it skips downloading the file unless force_download is True
    :param force_download If True, downloads (and overwrites) the file regardless of whether the file has already been
    downloaded.
    :return:base directory
    """

    base_dir = Path(base_dir)
    download_dir = Path(download_dir)
    rating_filepath = base_dir / 'movies.csv'
    is_target_file_exist = rating_filepath.is_file()

    if is_target_file_exist and not force_download:
        return str(base_dir)

    urllib.request.urlretrieve(url, TEMP_FILE)
    with zipfile.ZipFile(TEMP_FILE, 'r') as zip_file:
        zip_file.extractall('./')

    for filename in ['ratings.csv', 'movies.csv', 'links.csv']:
        path = download_dir / filename
        path.replace(base_dir / filename)

    TEMP_FILE.unlink()
    shutil.rmtree(download_dir)

    return str(base_dir)
