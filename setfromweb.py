SITE = 'http://sessionsgrenoble.free.fr/articles.php?lng=fr&pg=332'
from bs4 import BeautifulSoup
import requests
from itertools import chain, groupby
import re
from glob import glob
from collections import Counter, OrderedDict
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
    keys = pd.DataFrame({k: Series(Counter(v))
                         for k, v in data.apply(to_keystring).iteritems()}).T
    keys.fillna(0, inplace=True)
    # find the keystrings that is the closest match to 
    setkeys = [Series(Counter(to_keystring(s))) for s in setlist_in]
    setlist = data.ix[
        [np.abs(k - keys).sum(axis=1).argmin() for k in setkeys]]
    setdata = pd.concat([pd.read_sql_query('''
    select * from songs where X = {}'''.format(ix), conn)
    for ix in setlist.index], axis=0)
    # setdata = pd.read_sql_query(
    #     'select * from songs where X in ({})'.format(', '.join(setlist.index)), conn)
    conn.close()
    return setdata

r = requests.get(SITE)
soup = BeautifulSoup(r.text, 'lxml')

morceaux = soup.find('u', text=r'Slow Session 30/08/16')
morclist = []
while len(morclist) == 0:
    morceaux = morceaux.findNext('ul')
    morclist = [li.text for li in morceaux.findAll('li')]
# split the sets into individual songs
morclist = list(chain(*(re.split('[/+]', m) for m in morclist)))
# drop the metadata
morclist = [to_keystring(m) for m in morclist]
guess = make_setdata(morclist)
print(pd.concat([guess['T'], Series(morclist, index=guess.index)],
                axis=1))
write_set(guess, 'Aug30.abc')
