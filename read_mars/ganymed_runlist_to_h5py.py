'''
Convert ganymed file into h5py hdf5

Usage: ganymed_runlist_to_h5py <runlist> <outputfile>

Options:
    --ganymed-base PATH    base path for ganymed filed [default: /gpfs0/fact/processing/data.r18753/ganymed_run/]

'''
from docopt import doctopt
from functools import partial
import pandas as pd
from tqdm import tqdm

import fact
from fact.io import to_h5py

from . import read_mars


def main():
    args = doctopt(__doc__)
    runs = pd.read_csv(args['<runlist>'])
    runs['night'] = runs.night.astype(int)
    runs['run_id'] = runs.run_id.astype(int)

    ganymed_file_path_generator = partial(
        fact.path.tree_path,
        prefix=args['--ganymed-base'],
        suffix='-summary.root',
    )

    initialised = False
    for idx, run in tqdm(runs.iterrows(), total=len(runs)):
        ganymed_file_path = ganymed_file_path_generator(run.night, run.run_id)
        df = read_mars(ganymed_file_path, tree='Events')
        df['night'] = run.night
        df['run_id'] = run.run_id

        if not initialised:
            to_h5py(args['<outputfile>'], df, key='events', mode='w')
            initialised = True
        else:
            to_h5py(args['<outputfile>'], df, key='events', mode='a')


if __name__ == '__main__':
    main()
