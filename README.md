# Session Generator

This is a small script written for generating abc files---think LaTeX,
but for music---based upon a master list of songs and a setlist. The
purpose is to simplify practice by having all of the songs on a given
list available in a single document

## Requirements

This script makes use of the `BeautifulSoup`, `pandas`, `numpy`, and
`sqlite` external libraries. Furthermore `abcm2ps` is necessary to
typeset the set.

## Contents

### `makeset.py`

Contains the main functions for munging a title and writing a setlist
out to abc format.


### `makedb.py`

This will take a given master abc file, with all the songs that could
possibly be requested, and generate an sqlite database. This database
can then be converted to a pandas DataFrame object for ease of
manipulation.


### setfromweb.py

This was written specifically for taking the setlist posted to
http://sessionsgrenoble.free.fr each week and generating a practice
sheet for the next week. Because the data entry isn't spell checked, a
heuristic is used to guess which title was intended by the input
text. (Specifically, the count of each letter is cast as a vector, and
compared against the count for all the titles in the database). This
isn't perfect, but for the number of songs in a typical set it works
well enough.