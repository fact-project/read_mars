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


def read_mars_fast(filename, tree='Events', leaves=[]):
    """Return a Pandas DataFrame of a star or ganymed output root file.
    
    A faster (~factor 15) version of read_mars. It also omits the useless leaves fBits and fUniqueID. 
    Keyword arguments:
    tree -- Set, which tree to read. (Default = "Events")
    leaves -- Specify a list of leaves. (Default is [], what reads in all leaves)
    """

    f = ROOT.TFile(filename)
    tree = f.Get(tree)
    if not leaves:
        leaves = [l.GetName() for l in tree.GetListOfLeaves() if
            not (l.GetName().endswith('.') or l.GetName().endswith('fBits') or l.GetName().endswith('fUniqueID'))]

    n_events = tree.GetEntries()
    tree.SetEstimate(n_events + 1) #necessary for files with more than 1 M events
    df = pd.DataFrame(np.empty([n_events, len(leaves)]), columns=leaves)
    b = np.empty([n_events])

    for leaf in leaves:
        tree.Draw(leaf, "", "goff")
        v1 = tree.GetV1()
        v1.SetSize(n_events + 1)
        for i in range(n_events):
            b[i] = v1[i]
        df[leaf] = b
    f.Close()

    return df
