import ROOT
import pandas as pd
import os
from tqdm import tqdm


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


def read_mars(filename, tree='Events', verbose=False):
    f = ROOT.TFile(filename)
    tree = f.Get(tree)
    n_events = tree.GetEntries()

    leaves = [
        l.GetName()
        for l in tree.GetListOfLeaves()
        if not l.GetName().endswith('.')
    ]

    events = []
    for i in tqdm(range(n_events), disable=not verbose):
        tree.GetEntry(i)

        events.append({})
        for leaf in leaves:
            events[-1][leaf] = tree.GetLeaf(leaf).GetValue()

    f.Close()

    return pd.DataFrame(events)
