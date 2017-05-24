import ROOT
import pandas as pd
import os

from .core import read_mars_to_list


result = ROOT.gSystem.Load('libmars.so')
if result != 0:
    raise ImportError(
        'Could not load libmars, Make sure to set your "LD_LIBRARY_PATH"'
    )


def datepath(base, date):
    return os.path.join(
        base,
        '{:04d}'.format(date.year),
        '{:02d}'.format(date.month),
        '{:02d}'.format(date.day),
    )


def read_mars(filename, treename='Events'):
    return pd.DataFrame(read_mars_to_list(filename, treename))
