import ROOT
import pandas as pd
import os
import numpy as np


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


def is_valid_leaf(leaf):
    '''
    Function to select valid leaves

    It returns False for leaves ending on `.` and for `fBits` and `fUniqueID`
    columns
    '''
    return not any((
        leaf.GetName().endswith('.'),
        leaf.GetName().endswith('fBits'),
        leaf.GetName().endswith('fUniqueID'),
    ))


def read_mars(filename, tree='Events', leaves=[]):
    """Return a Pandas DataFrame of a MARS (eg. star or ganymed output) root file.

    read_mars uses the TTree.Draw() function to prevent calling each leaf of each event
    with a lot of overhead from python. It also omits the useless leaves fBits and fUniqueID.
    Keyword arguments:
    tree -- Set, which tree to read. (Default = "Events")
    leaves -- Specify a list of leaves. (Default is [], what reads in all leaves)
    """

    file = ROOT.TFile(filename)
    tree = file.Get(tree)

    if not leaves:
        leaves = [
            leaf.GetName()
            for leaf in filter(is_valid_leaf, tree.GetListOfLeaves())
        ]

    n_events = tree.GetEntries()
    tree.SetEstimate(n_events + 1)  # necessary for files with more than 1 M events

    df = pd.DataFrame()
    for leaf in leaves:

        # Looping over all events of a root file from python is extremely slow.
        # As the Draw function also loops over all events and
        # stores the values of the leaf in the memory,
        # only very few root function calls from python are used.
        # "" means, that no cut is applied and the "goff" option disables graphics.
        # GetV1() returns a pointer or memory view of the values of the leaf.
        # See eg. https://root.cern.ch/root/roottalk/roottalk03/0638.html

        tree.Draw(leaf, "", "goff")
        v1 = tree.GetV1()
        v1.SetSize(n_events * 8)  # a double has 8 Bytes

        df[leaf] = np.frombuffer(v1.tobytes(), dtype='float64')

    file.Close()

    return df
