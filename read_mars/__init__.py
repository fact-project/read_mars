import ROOT
import pandas as pd
import numpy as np

result = ROOT.gSystem.Load('libmars.so')
if result != 0:
    raise ImportError(
        'Could not load libmars, Make sure to set your "LD_LIBRARY_PATH"'
    )
# import this only after libmars.so
from .status_display import StatusDisplay


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


def leaves_to_numpy(tree, leaf_names):
    # Looping over all events of a root file from python is extremely slow.
    # As the Draw function also loops over all events and
    # stores the values of the leaf in the memory,
    # only very few root function calls from python are used.
    # "" means, that no cut is applied and the "goff" option disables graphics.
    # GetV1() returns a pointer or memory view of the values of the leaf.
    # See eg. https://root.cern.ch/root/roottalk/roottalk03/0638.html
    n_events = tree.GetEntries()
    tree.SetEstimate(n_events + 1)  # necessary for files with more than 1 M events
    out = {}
    for leaf_name in leaf_names:
        tree.Draw(leaf_name, "", "goff")
        v1 = tree.GetV1()
        v1.SetSize(n_events * 8)  # a double has 8 Bytes
        out[leaf_name] = np.frombuffer(v1.tobytes(), dtype='float64')
    return out


def read_mars(filename, tree='Events', leaf_names=None):
    """Return a Pandas DataFrame of a MARS (eg. star or ganymed output) root file.

    read_mars uses the TTree.Draw() function to prevent calling each leaf of each event
    with a lot of overhead from python. It also omits the useless leaves fBits and fUniqueID.
    Files with MSignalCam containers (callisto output) can not be read.
    Keyword arguments:
    tree -- Set, which tree to read. (Default = "Events")
    leaf_names -- Specify a list of leaf_names. (Default is None, what reads in all leaf_names)
    """

    file = ROOT.TFile(filename)
    tree = file.Get(tree)

    if not leaf_names:
        leaf_names = [
            leaf.GetName()
            for leaf in filter(is_valid_leaf, tree.GetListOfLeaves())
        ]

    df = pd.DataFrame(leaves_to_numpy(tree, leaf_names))
    file.Close()

    return df
