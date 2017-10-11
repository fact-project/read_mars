import ROOT
import fact
import pandas as pd
from collections import namedtuple
from collections import OrderedDict
from root_numpy import hist2array
from fact.instrument.camera import reorder_softid2chid
__all__ = ['StatusDisplay']


def transform_MHCamera(c):
    a = hist2array(c, return_edges=False, include_overflow=False)
    assert len(a) == 1440
    return reorder_softid2chid(a)


def transform_TH(h):
    return hist2array(h, return_edges=True, include_overflow=True)


def transform_TF1(tf1):
    th1 = tf1.GetHistogram()
    return transform_TH(th1)

_p_names = ['name', 'class_name', 'canvas_name', 'pad_id_name']

StatusDisplayKey = namedtuple(
    'StatusDisplayKey',
    _p_names
)


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
            'TH1F': transform_TH,
            'TH1D': transform_TH,
            'TH2F': transform_TH,
            'TH2D': transform_TH,
            'TProfile': transform_TH,
            'TF1': transform_TF1,
        }

        self._df = self.df()

    def keys(self):
        return self.contents.keys()

    def get(self, name=None, class_name=None, canvas_name=None, pad_id_name=None):
        k = StatusDisplayKey(name, class_name, canvas_name, pad_id_name)
        return self[k]

    def df(self):
        if not hasattr(self, '_df'):
            _df = []
            for k in self.keys():
                d = k._asdict()
                d['object'] = self[k]
                _df.append(d)
            self._df = pd.DataFrame(_df)
        return self._df

    def __repr__(self):
        return repr(self._df)

    def _repr_html_(self):
        return self._df._repr_html_()

    def find(self, name=None, class_name=None, canvas_name=None, pad_id_name=None):
        p_values = [name, class_name, canvas_name, pad_id_name]
        restrictions = {
            _p_names[i]: p_values[i] for i in range(len(_p_names))
            if p_values[i] is not None
        }

        query_string = ' and '.join('{0}=="{1}"'.format(k, v) for k, v in restrictions.items())
        result = self._df.query(query_string)
        if len(result) == 1:
            return result.object.iloc[0]
        else:
            return result

    def __getitem__(self, key):
        return self._transform_root_object_to_python(self.contents[key])

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
    contents = improve_keys(contents)
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
        cls_name = p.__class__.__name__
        if cls_name not in ['TPad', ]:
            if cls_name not in ['TPaveText', 'TFrame']:
                primitives[p.GetName()] = p
        else:
            primitives[p.GetName()] = primitives_from_canvas(p)
    return primitives


def flatten_ordered_dicts(ordered_dict, outer_keys=None):
    if outer_keys is None:
        outer_keys = tuple()

    output = {}
    for this_key, value in ordered_dict.items():
        keys = tuple([this_key, *outer_keys])
        if not isinstance(value, OrderedDict):
            output[tuple([value.__class__.__name__, *keys])] = value
        else:
            output.update(flatten_ordered_dicts(value, keys))
    return output


def improve_keys(contents):
    ''' the input keys are at the moment:

    'class_name', 'obj_name', 'pad_name', 'canvas_name'
    or
    'class_name', 'obj_name', 'canvas_name'

    Example:
     ('TH1D', 'Pix5', 'Pix5'),
     ('TF1', 'spektrum', 'Pix5'),
     ('MHCamera', 'Rate', 'Cams1_1', 'Cams1'),
     ('MHCamera', 'Gain', 'Cams1_2', 'Cams1'),
     ('MHCamera', 'Baseline', 'Cams1_3', 'Cams1'),

    We form them here into `StatusDisplayKey`s
    '''
    new_contents = {}
    for k, v in contents.items():
        assert len(k) in [3, 4]

        if len(k) == 3:
            class_name, obj_name, canvas_name = k
            pad_name = ''
        else:  # 4
            class_name, obj_name, pad_name, canvas_name = k

        try:
            pad_id_name = str(pad_name.split('_')[-1])
        except ValueError:
            pad_id_name = None

        new_key = StatusDisplayKey(
            name=obj_name,
            class_name=class_name,
            canvas_name=canvas_name,
            pad_id_name=pad_id_name,
        )
        new_contents[new_key] = v

    return new_contents
