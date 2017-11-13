import ROOT
import pandas as pd
import os
import numpy as np
from fact.instrument.camera import chid2softid

result = ROOT.gSystem.Load('libmars.so')
if result != 0:
    raise ImportError(
        'Could not load libmars, Make sure to set your "LD_LIBRARY_PATH"'
    )
# import this only after libmars.so
from .status_display import StatusDisplay


def datepath(base, date):
    return os.path.join(
        base,
        '{:04d}'.format(date.year),
        '{:02d}'.format(date.month),
        '{:02d}'.format(date.day),
    )


datatypes = {"Float_t": np.float32,
             "ULong_t": np.uint64,
             "Long_t": np.int64,
             "UInt_t": np.uint32,
             "Int_t": np.int32,
             "UShort_t": np.uint16,
             "Short_t": np.int16,
             "UChar_t": np.uint8,
             "Char_t": np.int8,
             "Bool_t": np.bool8}


def is_valid_leaf(leaf):
    """
    Function to select valid leaves

    It returns False for leaves ending on `.` and for `fBits` and `fUniqueID`
    columns
    """
    return not any((
        leaf.GetName().endswith('.'),
        leaf.GetName().endswith('fBits'),
        leaf.GetName().endswith('fUniqueID'),
        leaf.GetName().startswith('MSignalCam')
    ))


def leaves_to_numpy(tree, leaf_names, N=1):
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
    tree_v1_dtype = np.dtype('float64')

    order = chid2softid(range(N))

    for leaf_name in leaf_names:
        tree.Draw(leaf_name, "", "goff")
        v1 = tree.GetV1()
        v1.SetSize(n_events * tree_v1_dtype.itemize)  # a double has 8 Bytes
        out[leaf_name] = np.frombuffer(v1.tobytes(), dtype=tree_v1_dtype)

        if N > 1:
            out[leaf_name] = out[leaf_name].reshape(n_events, N)[:, order]

        dtype = tree.GetLeaf(leaf_name).GetTypeName()
        if dtype in datatypes:
            out[leaf_name] = out[leaf_name].astype(datatypes[dtype])

    return out


def read_mars(filename, tree='Events', leaf_names=None):
    """Return a Pandas DataFrame of a MARS (eg. star or ganymed output) root file.

    read_mars uses the TTree.Draw() function to prevent calling each leaf of each event
    with a lot of overhead from python. It also omits the useless leaves fBits and fUniqueID.
    When reading files with MSignalCam containers (callisto output), the MSignalCam containers
    are skipped. To get the pixel information (e.g. charge, arrival time), use read_callisto()
    instead.
    Keyword arguments:
    tree: string
         Set, which tree to read. (default: 'Events')
    leaf_names: list of strings
         Specify a list of leaf_names. (default: None, what reads in all leaf_names)
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


def read_callisto(
    filename,
    tree='Events',
    fields=[
        'MSignalCam.fPixels.fPhot',
        'MSignalCam.fPixels.fArrivalTime'
    ],
):
    """Return a dict like fields, with numpy arrays of shape (N_events, 1440)

        tree: which tree to read.
        fields: Specify the containers to read, e.g. add:
            'MSignalCam.fPixels.fTimeSlope'
    """
    return leaves_to_numpy(ROOT.TFile(filename).Get(tree), fields, N=1440)
