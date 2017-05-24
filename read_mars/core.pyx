import ROOT


def read_mars_to_list(filename, tree='Events'):
    f = ROOT.TFile(filename)
    tree = f.Get(tree)
    n_events = tree.GetEntries()

    leaves = [
        l.GetName()
        for l in tree.GetListOfLeaves()
        if not l.GetName().endswith('.')
    ]

    cdef long i;
    events = []

    for i in range(n_events):
        tree.GetEntry(i)

        events.append({})
        for leaf in leaves:
            events[-1][leaf] = tree.GetLeaf(leaf).GetValue()

    f.Close()

    return events
