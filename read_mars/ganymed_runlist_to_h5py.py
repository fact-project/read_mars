'''
Convert ganymed file into h5py hdf5

Arguments:

    RUNLIST: a csv file with columns night,run_id
    OUTPUTFILE: outputfilename
'''
from argparse import ArgumentParser
import pandas as pd
from fact.io import to_h5py
from tqdm import tqdm
import os

from . import read_mars, datepath


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

    initialised = False
    for idx, run in tqdm(runs.iterrows(), total=len(runs)):
        night = int('%Y%m%d'.format(run.night_date.date()))
        base = datepath(args.ganymed_base, night)

        ganymed_file = os.path.join(
            base,
            '{}_{:03d}-summary.root'.format(night, run.run_id)
        )

        df = read_mars(ganymed_file, tree='Events')
        df['night'] = night
        df['run_id'] = run.run_id

        if not initialised:
            to_h5py(args.outputfile, df, key='events', mode='w')
            initialised = True
        else:
            to_h5py(args.outputfile, df, key='events', mode='a')


if __name__ == '__main__':
    main()
