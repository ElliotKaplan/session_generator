import sqlite3
import pandas as pd
from pandas import Series, DataFrame
from itertools import groupby, takewhile
from collections import Counter
import string
import re

stopwords = ('the', 'a', 'an')

class SplitSongs():
    '''class to keep track of when a new song has started. 

    This allows us to use itertools's groupby function to split things
    up.
    '''
    index=0
    def getindex(self, line):
        # new entries are delimited by the 'X:' tag
        if line.startswith('X'):
            self.index = int(line.split(':')[-1])
        return self.index

def main(fname, encoding='iso-8859-1'):
    with open(fname, 'r', encoding=encoding) as fobj:
        splitter = SplitSongs()
        data = []
        for i, grp in groupby(fobj, splitter.getindex):
            datum={}
            for line in grp:
                if line[0] in string.ascii_uppercase and line[1] == ':':
                    key, val = line[0], line[2:]
                    datum[key] = val.strip()
                else:
                    break
            datum['score'] = line + ''.join(grp)
            data.append(datum)
    data = DataFrame(data[1:])
    data = data[['X', 'T', 'K', 'M', 'L', 'R', 'score']]
    # drop the parentheticals from the titles
    data['T'] = data['T'].apply(lambda s: s.split('(')[0])
    data['T'] = data['T'].apply(lambda s: s.split('[')[0])

    with sqlite3.connect('songdb.sqlite3') as conn:
        data.to_sql('songs', conn)

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser('generates an sqlite database from the provided abc file')

    parser.add_argument('fname', type=str,
                        help='''abc file to sqlitize''')
    parser.add_argument('--encoding', type=str, default='iso-8859-1',
                        help='''encoding of abc file''')
                        

    args = parser.parse_args()
    fname = args.fname
    encoding = args.encoding
    
    main(fname, encoding)
