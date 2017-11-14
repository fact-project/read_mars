import ROOT

result = ROOT.gSystem.Load('libmars.so')
if result != 0:
    raise ImportError(
        'Could not load libmars, Make sure to set your "LD_LIBRARY_PATH"'
    )

# import this only after libmars.so
from .status_display import StatusDisplay
from .tree_file import tree_file_to_dict
