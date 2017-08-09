import ROOT
import fact
from collections import OrderedDict
from root_numpy import hist2array
from fact.instrument.camera import reorder_softid2chid

__all__ = ['StatusDisplay']


def transform_MHCamera(c):
    a = hist2array(c, return_edges=False, include_overflow=False)
    assert len(a) == 1440
    return reorder_softid2chid(a)


def transform_TH1(h):
    return hist2array(h, return_edges=True, include_overflow=True)


def transform_TF1(tf1):
    th1 = tf1.GetHistogram()
    return transform_TH1(th1)


class StatusDisplay:
    def __init__(self, path, transform=True):
        self.path = path
        self.date = fact.run2dt(self.path.split('/')[-1].split('_')[0]).date()
        self.run = int(self.path.split('/')[-1].split('_')[1])

        self.tfile = ROOT.TFile(path)
        self.status_array = self.tfile.Get('MStatusDisplay')
        self.contents = flat_contents_of_status_array(self.status_array)

        self.transformations = {
            'MHCamera': transform_MHCamera,
            'TH1F': transform_TH1,
            'TH1D': transform_TH1,
            'TF1': transform_TF1,
        }

    def keys(self):
            return self.contents.keys()

    def __getitem__(self, key):
        self._transform_root_object_to_python(self.contents[key])

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.tfile.Close()

    def _transform_root_object_to_python(self, obj):
        clsname = obj.__class__.__name__
        transformation = self.transformations.get(clsname, lambda x: x)
        return transformation(obj)


def flat_contents_of_status_array(sa):
    canvases = canvases_from_status_array(sa)
    contents = OrderedDict()
    for name, canvas in canvases.items():
        contents[name] = primitives_from_canvas(canvas)
    contents = flatten_ordered_dicts(contents)
    contents = {'_'.join(map(str, k[::-1])): v for k, v in contents.items()}
    return contents


def canvases_from_status_array(sa):
    canvases = OrderedDict()
    for obj in sa:
        if 'TCanvas' in obj.__class__.__name__:
            canvases[obj.GetName()] = obj
    return canvases


def primitives_from_canvas(c):
    primitives = OrderedDict()
    for p in c.GetListOfPrimitives():
        if 'TPad' not in p.__class__.__name__:
            primitives[p.GetName()] = p
        else:
            primitives[p.GetName()] = primitives_from_canvas(p)
    return primitives


def flatten_ordered_dicts(ordered_dict, outer_keys=None):
    if outer_keys is None:
        outer_keys = tuple()

    output = {}
    for this_key, value in ordered_dict.items():
        keys = tuple([*outer_keys, this_key])
        if not isinstance(value, OrderedDict):
            output[keys] = value
        else:
            output.update(flatten_ordered_dicts(value, keys))
    return output
