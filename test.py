#!/usr/bin/env python

from dbc import *

Titles = CharTitlesDBC('CharTitles.dbc')
Titles.SetVerbosity(True)

print (GetLocale(Titles[2]['TitleMale'], 'frFR'))