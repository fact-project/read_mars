'''
Convert MARS file into h5py hdf5

Arguments:

    INPUTFILE: MARS input file
    OUTPUTFILE: outputfilename
'''
from argparse import ArgumentParser
from fact.io import to_h5py

from . import read_mars


parser = ArgumentParser(description=__doc__)
parser.add_argument('inputfile')
parser.add_argument('outputfile')
parser.add_argument('-t', '--tree', help='Tree to extract', default='Events')
parser.add_argument('-a', '--append', action='store_true', help='Append to file instead of overwrite')


def main():
    args = parser.parse_args()
    df = read_mars(args.inputfile, tree=args.tree)
    to_h5py(df, args.outputfile, key=args.tree, mode='a' if args.append else 'w')


if __name__ == '__main__':
    main()
