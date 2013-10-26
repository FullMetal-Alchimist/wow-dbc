#!/usr/bin/env python

from dbc import *

Titles = CharTitlesDBC('CharTitles.dbc')

for title in Titles:
    #print ', '.join(x for x in dir(spell) if not x.startswith('__'))
    print(GetLocale(title.TitleMale, 'frFR'))
    print(GetLocale(title.TitleFemale, 'frFR'))