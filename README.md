# read_mars
Python library to read MARS output (e.g. ganymed or star files)

On the ISDC, this is installed in `/swdev_nfs/anaconda3`,
you also need to put

```
source /swdev_nfs/root_v5.34.36-anaconda3/bin/thisroot.sh
export PATH=/swdev_nfs/anaconda3/bin:$PATH
export PATH=/swdev_nfs/Mars_root_v5.34.36-anaconda3:$PATH
export LD_LIBRARY_PATH=/swdev_nfs/Mars_root_v5.34.36-anaconda3:$LD_LIBRARY_PATH
```
in your `.bashrc`

## StatusDisplay
Interface to translate the content of ROOT Files containing MARS's `MStatusDisplay`
into the python world. 

Reads the ROOT file and transforms the contained (and supported) ROOT objects to numpy arrays.

Certain plots in a `MStatusDisplay` are addressed by use of `StatusDisplay.find()`. A list of keys that are searchable, can be found in the representation of `StatusDisplay.find()`.

Usage e.g.:
``` 
from read_mars import StatusDisplay
from fact.plotting import camera
import matplotlib.pyplot as plt
%matplotlib inline  ## when in jupyter notebook

f = StatusDisplay('resources/20130930_244_244_B.root')
img = camera(f.find(name='Gain'), cmap='viridis', vmin=150)
plt.colorbar(img);
```
