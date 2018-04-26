import requests
from itertools import chain, groupby
import re
from glob import glob
from collections import Counter, OrderedDict

from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import sqlite3

from makeset import to_keystring, write_set


def make_setdata(setlist_in):
    # get the full list of titles
    conn = sqlite3.connect('songdb.sqlite3')
    data = pd.read_sql_query('''
    SELECT X, T FROM songs
    ''', conn, index_col='X')['T']
    # eliminate any accents, generate a pandas Series object with a count of
    # letters. This serves as our method for finding a title
    keys = pd.DataFrame({k: Series(Counter(v))
                         for k, v in data.apply(to_keystring).iteritems()}).T
    keys.fillna(0, inplace=True)
    # find the keystrings that is the closest match to 
    setkeys = [Series(Counter(to_keystring(s))) for s in setlist_in]
    setlist = data.ix[
        [np.abs(k - keys).sum(axis=1).argmin() for k in setkeys]]
    # use the guesses to generate the set data
    setdata = pd.concat(
        [pd.read_sql_query('''
        select * from songs where X = {}'''.format(ix), conn)
        for ix in setlist.index],
        axis=0)
    conn.close()
    return setdata

def main(setlabel, outfile, site):
    r = requests.get(site)
    soup = BeautifulSoup(r.text, 'lxml')

    morceaux = soup.find('u', text=setlabel)
    morclist = []
    while len(morclist) == 0:
        morceaux = morceaux.findNext('ul')
        morclist = [li.text for li in morceaux.findAll('li')]
    # split the sets into individual songs
    morclist_raw = list(chain(*(re.split('[/+]', m) for m in morclist)))
    # drop the metadata
    morclist = [to_keystring(m) for m in morclist_raw]
    guess = make_setdata(morclist)
    write_set(guess, outfile)
    # print a comparison of the chosen songs with the raw text
    to_stdout = pd.concat([guess['T'], Series(morclist_raw, index=guess.index)], axis=1)
    to_stdout.rename(columns={'T':'Title', 0:'raw text'}, inplace=True)
    print(to_stdout)

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('setlabel', type=str, help='''
    string that delimits the set''')
    parser.add_argument('outfile', type=str, help='''
    name of output file''')
    parser.add_argument('--site', type=str,
                        default='http://sessionsgrenoble.free.fr/articles.php?lng=fr&pg=299',
                        help='''website hosting the list''')

    args = parser.parse_args()
    main(args.setlabel, args.outfile, args.site)
