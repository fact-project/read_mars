'''
Convert MARS file into h5py hdf5

Arguments:

    INPUTFILE: MARS input file
    OUTPUTFILE: outputfilename
'''
from argparse import ArgumentParser
from fact.io import to_h5py

from . import read_mars


parser = ArgumentParser(help=__doc__)
parser.add_argument('inputfile')
parser.add_argument('outputfile')
parser.add_argument('-t', '--tree', help='Tree to extract', default='Events')
parser.add_argument(
    '--ganymed-base', dest='ganymed_base',
    default='/gpfs0/fact/processing/data.r18753/ganymed_run/'
)


def main():
    args = parser.parse_args()
    df = read_mars(args.inputfile, tree=args.tree, verbose=True)
    to_h5py(args.outputfile, df, key=args.tree, mode='w')


if __name__ == '__main__':
    main()
