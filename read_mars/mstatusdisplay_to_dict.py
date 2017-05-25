from collections import OrderedDict
import numpy as np
import ROOT

import fact


def mstatusdisplay_to_dict(
        path,
        transform=True,
        exclude=['TF1', 'TPaveText'],
        ):
    ''' return a flat dict, with string keys and values either coming:
     * from an MHCamera -> np.array(shape=(1440,)) or
     * from a TH1 -> {'bins': np.array, 'content':np.array}

    keep low  level acces to the Root classes with `transform=False`
    and more class names to the `classes` list in case you want ot
    '''

    tfile = ROOT.TFile(path)
    status_array = tfile.Get('MStatusDisplay')
    canvases = canvases_from_status_array(status_array)

    contents = OrderedDict()
    for name, canvas in canvases.items():
        contents[name] = primitives_from_canvas(canvas)
    contents = flatten_ordered_dicts(contents)

    if transform:
        output = {}
        for name, obj in contents.items():
            clsname = obj.__class__.__name__
            if clsname in exclude:
                continue
            if clsname == 'MHCamera':
                output[name] = transform_MHCamera(obj)
            elif clsname in ['TH1F', 'TH1D']:
                output[name] = transform_TH1(obj)
            else:
                output[name] = obj
        return output
    else:
        return contents


def transform_TH1(h):
    ''' transform a TH1 into a dict of {'bins': np.array, 'content':np.array}
    '''
    N = h.GetNbinsX()
    low_edge = []
    content = []

    for i in range(0, N+2):
        low_edge.append(h.GetBinLowEdge(i))
        content.append(h.GetBinContent(i))
    return {
        'bins': np.array(low_edge),
        'content': np.array(content)
    }

p = fact.instrument.get_pixel_dataframe()
softids = p.sort_values('CHID').softID.values


def transform_MHCamera(c):
    ''' transform an MHCamera into an 1D np.array of length 1440 in CHID order
    '''
    return np.array(
            [c.GetBinContent(i+1) for i in softids]
        )


def flatten_ordered_dicts(rest, start=None, output=None):
    '''From a deeply nested dict, like eg:

    d = {'a': {'b': {'c': value1, 'd': value2}, 'd': value3}}

    make a single dict, with keys reflecting the "path" to the values.
    A first way would be the full "path", e.g. like this:

    d = {
        'a_b_c': value1,
        'a_b_d': value2,
        'a_d': value3
    }

    But such long keys feel clumsy and seem to be not needed.
    In this special case, the last keys in the list caried the most information
    for a human, while intermediate keys were boring.
    So the policy is to drop everything from the key, unless it makes it
    non-unique, in that case add previous levels of the path until a
    unique key is found.

    So in this example the result is:
    d = {
        'c': value1,
        'd': value2,
        'a_d': value3
    }
    '''
    if start is None:
        start = []
    if output is None:
        output = {}
    for k, v in rest.items():
        foo = start + [k]
        if isinstance(v, OrderedDict):
            flatten_ordered_dicts(v, foo, output)
        else:
            keys = [
                '_'.join(foo[-i-1:])
                for i in range(len(foo))
            ]
            for key in keys:
                if key not in output:
                    output[key] = v
                    break
    return output


def canvases_from_status_array(sa):
    '''return OrderedDict() of `Name`: TCanvas inside an MStatusArray
    '''
    canvases = OrderedDict()
    for obj in sa:
        if 'TCanvas' in obj.__class__.__name__:
            canvases[obj.GetName()] = obj
    return canvases


def primitives_from_canvas(c):
    '''Return (nested) OrderedDict() of Primitives found on a TCanvas,

    Steps also down into TPads in order to find primitives.
    '''
    primitives = OrderedDict()
    for p in c.GetListOfPrimitives():
        if 'TPad' not in p.__class__.__name__:
            primitives[p.GetName()] = p
        else:
            primitives[p.GetName()] = primitives_from_canvas(p)
    return primitives
