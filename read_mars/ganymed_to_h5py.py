'''
Convert ganymed file into h5py hdf5

Arguments:

    INPUTFILE: ganymed input file (YYYYMMDD_RUN-analysis.root)
    OUTPUTFILE: outputfilename
'''
from argparse import ArgumentParser
from fact.io import to_h5py

from . import read_mars


parser = ArgumentParser(help=__doc__)
parser.add_argument('inputfile')
parser.add_argument('outputfile')
parser.add_argument(
    '--ganymed-base', dest='ganymed_base',
    default='/gpfs0/fact/processing/data.r18753/ganymed_run/'
)


def main():
    args = parser.parse_args()
    df = read_mars(args.inputfile, tree='Events', verbose=True)
    to_h5py(args.outputfile, df, key='events', mode='w')


if __name__ == '__main__':
    main()
