import ROOT
import numpy as np
from fact.instrument.camera import chid2softid
from collections import namedtuple
import os
from contextlib import contextmanager
from contextlib import redirect_stdout, redirect_stderr

result = ROOT.gSystem.Load('libmars.so')
if result != 0:
    raise ImportError(
        'Could not load libmars, Make sure to set your "LD_LIBRARY_PATH"'
    )
# import this only after libmars.so
from .status_display import StatusDisplay

DEV_NULL = open(os.devnull, 'w')

root_TypeName_to_numpy_dtype = {
    "Float_t": np.float32,
    "ULong_t": np.uint64,
    "Long_t": np.int64,
    "UInt_t": np.uint32,
    "Int_t": np.int32,
    "UShort_t": np.uint16,
    "Short_t": np.int16,
    "UChar_t": np.uint8,
    "Char_t": np.int8,
    "Bool_t": np.bool8,
}

LeafInfo = namedtuple('LeafInfo', 'tree_name leaf_name dtype')


def leaves_of_tree(tree):
    tree_name = tree.GetName()
    leaves = []
    for leaf in tree.GetListOfLeaves():
        leaf_name = leaf.GetName()
        dtype = tree.GetLeaf(leaf_name).GetTypeName()
        if dtype in root_TypeName_to_numpy_dtype:
            dtype = root_TypeName_to_numpy_dtype[dtype]
        leaves.append(LeafInfo(tree_name, leaf_name, dtype))
    return leaves


class TreeFile:

    def __init__(self, path):
        self.path = path
        self.file = ROOT.TFile(path)

    def to_dict(self):
        results = {}
        with redirect_stdout(DEV_NULL), redirect_stderr(DEV_NULL):
            for leaf in self.leaves_of_file():
                tree = self.file.Get(leaf.tree_name)
                try:
                    size = 1
                    if 'MSignalCam' in leaf.leaf_name:
                        size = 1440
                    results[leaf.leaf_name] = leaf_to_numpy(tree, leaf.leaf_name, size)
                except ValueError:
                    pass
        return results

    def __del__(self):
        self.file.Close()

    def tree_names(self):
        _tree_names = []
        for key in self.file.GetListOfKeys():
            if key.GetClassName() == 'TTree':
                _tree_names.append(key.GetName())
        return _tree_names

    def leaves_of_file(self):
        leaves = []
        for tree_name in self.tree_names():
            tree = self.file.Get(tree_name)
            leaves.extend(leaves_of_tree(tree))
        return leaves


def leaf_to_numpy(tree, leaf_name, N=1):
    # Looping over all events of a root file from python is extremely slow.
    # As the Draw function also loops over all events and
    # stores the values of the leaf in the memory,
    # only very few root function calls from python are used.
    # "" means, that no cut is applied and the "goff" option disables graphics.
    # GetV1() returns a pointer or memory view of the values of the leaf.
    # See eg. https://root.cern.ch/root/roottalk/roottalk03/0638.html

    assert N in [1, 1440]

    n_events = tree.GetEntries()
    tree.SetEstimate((n_events + 1) * N)

    tree.Draw(leaf_name, "", "goff")
    v1 = tree.GetV1()

    tree_v1_dtype = np.dtype('float64')
    v1.SetSize(n_events * tree_v1_dtype.itemsize * N)
    out = np.frombuffer(v1.tobytes(), dtype=tree_v1_dtype)

    if N > 1:
        order = chid2softid(range(N))
        out = out.reshape(n_events, N)[:, order]

    dtype = tree.GetLeaf(leaf_name).GetTypeName()
    if dtype in root_TypeName_to_numpy_dtype:
        out = out.astype(root_TypeName_to_numpy_dtype[dtype])

    return out
