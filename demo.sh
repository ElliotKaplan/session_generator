#!/bin/bash

wget http://sessionsgrenoble.free.fr/file/01_repertorio_irish.abc
python3 makedb.py 01_repertorio_irish.abc
python3 setfromweb.py 'Slow session 14/06/2016' test.abc
abcm2ps test.abc
