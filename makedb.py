import sqlite3
import pandas as pd
from pandas import Series, DataFrame
from itertools import groupby, takewhile
from collections import Counter
import string
import re

stopwords = ('the', 'a', 'an')

class SplitSongs():
    index=0
    def getindex(self, line):
        if line.startswith('X'):
            self.index = int(line.split(':')[-1])
        return self.index

fname = 'repertoire.abc'
with open(fname, 'r') as fobj:
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
