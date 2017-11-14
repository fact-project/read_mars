"""
function to read a "Mars tree file", i.e. a file containing one or
more TTrees possibly containing Mars classes.

Example:
Looking at all the leaves in a file, their shape and their data-type
This can already tell you a lot about an unknown file.

    from read_mars import tree_file_to_dict
    d = tree_file_to_dict('20171022_215_C.root')
    for leaf_name, nd_array in d.items():
        print(leaf_name, nd_array.shape, nd_array.dtype)


In case you do not want to read all the leaves, e.g. for speed optimization,
or to reduce the memory footprint of your application.
Assume you want to only read one leaf, and you know its:
    * tree_name
    * leaf_name and
    * data_type

Then you can do:

    from read_mars import ROOT, LeafInfo, any_leaf_to_numpy
    my_leaf = any_leaf_to_numpy(
        ROOT.TFile('20171022_215_C.root'),
        LeafInfo('Events', 'MFoo.fBar.fBaz', np.float32)
    )
    print(my_leaf)

"""
import ROOT
import numpy as np
from fact.instrument.camera import chid2softid
from collections import namedtuple
import os
from contextlib import redirect_stdout, redirect_stderr
import warnings

DEV_NULL = open(os.devnull, 'w')
N_PIXEL = 1440
CHID_2_SOFTID = chid2softid(range(N_PIXEL))


def tree_file_to_dict(path):
    file = ROOT.TFile(path)

    results = {}
    for leaf in leaves(file):
        try:
            results[leaf.leaf_name] = any_leaf_to_numpy(file, leaf)
        except ValueError:
            pass

    file.Close()
    return results


def leaves(file):
    _leaves = []
    for tree_name in tree_names(file):
        tree = file.Get(tree_name)
        _leaves.extend(leaves_of_tree(tree))
    return _leaves


def tree_names(file):
    _tree_names = []
    for key in file.GetListOfKeys():
        if key.GetClassName() == 'TTree':
            _tree_names.append(key.GetName())
    return _tree_names


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


def any_leaf_to_numpy(file, leaf):

    # We try to convert any leaf to numpy, no matter what,
    # if it does not work, we throw ValueError,
    # but root is very verbose about it, while an exception would be enough
    # so we simply suppress all output

    tree = file.Get(leaf.tree_name)
    with redirect_stdout(DEV_NULL), redirect_stderr(DEV_NULL):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if 'MSignalCam' in leaf.leaf_name:
                return MSignalCam_to_numpy(tree, leaf.leaf_name)
            else:
                return leaf_to_numpy(tree, leaf.leaf_name)


def MSignalCam_to_numpy(tree, leaf_name):
    out = leaf_to_numpy(tree, leaf_name, N_PIXEL)
    out = out.reshape(-1, N_PIXEL)[:, CHID_2_SOFTID]
    return out


def leaf_to_numpy(tree, leaf_name, N=1):
    # Looping over all events of a root file from python is extremely slow.
    # As the Draw function also loops over all events and
    # stores the values of the leaf in the memory,
    # only very few root function calls from python are used.
    # "" means, that no cut is applied and the "goff" option disables graphics.
    # GetV1() returns a pointer or memory view of the values of the leaf.
    # See eg. https://root.cern.ch/root/roottalk/roottalk03/0638.html

    n_events = tree.GetEntries()
    tree.SetEstimate((n_events + 1) * N)

    tree.Draw(leaf_name, "", "goff")
    v1 = tree.GetV1()

    tree_v1_dtype = np.dtype('float64')
    v1.SetSize(n_events * tree_v1_dtype.itemsize * N)
    out = np.frombuffer(v1.tobytes(), dtype=tree_v1_dtype)

    dtype = tree.GetLeaf(leaf_name).GetTypeName()
    if dtype in root_TypeName_to_numpy_dtype:
        out = out.astype(root_TypeName_to_numpy_dtype[dtype])

    return out
