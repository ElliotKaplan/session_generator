import sqlite3
import numpy as np
import pandas as pd
import unicodedata
from pandas import Series, DataFrame
from collections import Counter
import re

# taken from http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

# clean up the names
def to_keystring(title):    
    return remove_accents(title.split(',')[0].split('(')[0].lower().replace(' ', '')).strip()


def write_set(setdata, outfile):
    with open(outfile, 'w') as fobj:
        for i, row in setdata.reset_index().iterrows():
            fobj.write('X: {}\n'.format(i))
            fobj.write('\n'.join(
                ('{}: {}'.format(k, v)
                 for k, v in row[['T', 'K', 'M', 'L', 'R']].iteritems())
                ))
            fobj.write('\n'+ row['score'])
    
def make_setlist(infile):
    # get the full list of titles
    conn = sqlite3.connect('songdb.sqlite3')
    data = pd.read_sql_query('''
    SELECT X, T FROM songs
    ''', conn, index_col='X')['T']
    keys = pd.DataFrame({k: Series(Counter(v))
                         for k, v in data.apply(to_keystring).iteritems()}).T
    keys.fillna(0, inplace=True)
    # find the keystrings that is the closest match to 
    with open(infile, 'r') as fobj:
        setlist_in = list(fobj)
    setkeys = [Series(Counter(to_keystring(s))) for s in setlist_in]

    setlist = data.ix[
        [np.abs(k - keys).sum(axis=1).argmin() for k in setkeys]]
    setdata = pd.read_sql_query(
        'select * from songs where X in ({})'.format(', '.join(setlist.index)), conn)
    conn.close()
    return setdata
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        '''create an abc file for a specified list of songs'''
        )
    parser.add_argument('input', type=str,
                        help='name of setlist file')
    parser.add_argument('-o', '--output', type=str,
                        help='name of output abc file')
    clin = parser.parse_args()
    setlist = make_setlist(clin.input)
    write_set(setlist, clin.output)
