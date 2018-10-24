import os
import uproot


__all__ = ['read_mars']


def datepath(base, date):
    return os.path.join(
        base,
        '{:04d}'.format(date.year),
        '{:02d}'.format(date.month),
        '{:02d}'.format(date.day),
    )


def read_mars(filename, tree='Events', leaf_names=None, **kwargs):
    """
    Return a Pandas DataFrame of a MARS (eg. star or ganymed output) root file.

    Parameters
    ----------

    tree: str
        Name of the tree to read

    leaf_names: str
        Specify a list of leaf_names.
        (Default is None, what reads in all interpretable leaf_names)

    **kwargs are passed to tree.pandas.df
    """

    f = uproot.open(filename)
    tree = f[tree]

    return tree.pandas.df(branches=leaf_names, **kwargs)
