import ROOT
import numpy as np
import pandas as pd
import fact

from .path_tools import SpeFilePathInfo


def read_gain_rate_xtalk(path):
    '''
    Read the "gain", "rate" and "crosstalk" Histograms for the given file
    and return them as a `pd.DataFrame` including a "CHID" column.

    Add:
     * the "date" (pd.Timestamp) and
     * "run" (integer)
    as constant columns to the dataframe.
    '''
    result = mstatusdisplay_to_df(
        path,
        hists_n_tabs={
            'gain': ('Gain', 'Cams1'),
            'rate': ('Rate', 'Cams1'),
            'crosstalk': ('Crosstalk', 'Cams1'),
        }
    )

    pathinfo = SpeFilePathInfo(path)
    result['date'] = pd.to_datetime(pathinfo.night)
    result['run'] = pathinfo.run1
    return result


def mstatusdisplay_to_df(path, hists_n_tabs):
    '''
    return a `pd.DataFrame` read from the given path.

    What to read is specified by `hists_n_tabs`.

    hists_n_tabs: to be read out needs to be a list of
    tuples of strings like this:

    hists_n_tabs = {
        'gain': ('Gain', 'Cams1'),
        'rate': ('Rate', 'Cams1'),
        'crosstalk': ('Crosstalk', 'Cams1'),
    }

    I believe:
     * the 1st string refers to the histogram name and
     * the 2nd string refers to the to the tab name.

    I have no idea how to find out these names
    without using `showlog` (a MARS tool)
    to look at the file before reading the data out using this function.
    '''

    rootfile = ROOT.TFile(path)
    display = rootfile.Get('MStatusDisplay')
    result = pd.DataFrame()
    result['CHID'] = fact.instrument.camera.softid2chid(np.arange(0, 1440))
    for name, (hist, tab) in hists_n_tabs.items:
        histo = display.FindObjectInCanvas(hist, 'MHCamera', tab)
        result[name] = np.array(
            [histo.GetBinContent(i) for i in range(1, 1441)]
        )

    return result
