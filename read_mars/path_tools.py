import os
from collections import namedtuple
import fact


class SpeFilePathInfo:

    def __init__(self, path):

        filename = os.path.basename(path)
        no_ext_filename = splitext_all(filename)[0]
        night_int_string, run_id1, run_id2 = no_ext_filename.split('_')

        self.night = fact.run2dt(night_int_string).date()
        self.run1 = int(run_id1)
        self.run2 = int(run_id2)


def splitext_all(path):
    ''' like os.path.splitext just be sure to remove all exts,
    for cases like "20170102_345.drs.fits.gz"
    we return
    ('20170102_345', '.drs', '.fits', '.gz')
    '''
    result = []
    while True:
        path, ext = os.path.splitext(path)
        if ext:
            result.append(ext)
        else:
            result.append(path)
            break
    return tuple(result[::-1])
