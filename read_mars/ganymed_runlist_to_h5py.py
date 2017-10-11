'''
Convert ganymed file into h5py hdf5

Arguments:

    RUNLIST: a csv file with columns night,run_id
    OUTPUTFILE: outputfilename
'''
from argparse import ArgumentParser
import pandas as pd
import fact
from functools import partial
from fact.io import to_h5py
from tqdm import tqdm

from . import read_mars


parser = ArgumentParser(description=__doc__)
parser.add_argument('runlist')
parser.add_argument('outputfile')
parser.add_argument(
    '--ganymed-base', dest='ganymed_base',
    default='/gpfs0/fact/processing/data.r18753/ganymed_run/'
)


def main():
    args = parser.parse_args()
    runs = pd.read_csv(args.runlist)
    runs['night_date'] = pd.to_datetime(runs['night'].astype(str), format='%Y%m%d')

    ganymed_file_path_generator = partial(
        fact.path.tree_path,
        prefix=args.ganymed_base,
        suffix='-summary.root',
    )

    initialised = False
    for idx, run in tqdm(runs.iterrows(), total=len(runs)):
        night = int('{:%Y%m%d}'.format(run.night_date))
        run = int(run.run_id)
        ganymed_file_path = ganymed_file_path_generator(night, run)
        df = read_mars(ganymed_file_path, tree='Events')
        df['night'] = night
        df['run_id'] = run.run_id

        if not initialised:
            to_h5py(args.outputfile, df, key='events', mode='w')
            initialised = True
        else:
            to_h5py(args.outputfile, df, key='events', mode='a')


if __name__ == '__main__':
    main()
