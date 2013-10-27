#!/usr/bin/env python

from dbc import *

Titles = DBCFile('New.dbc', CharTitlesDBC)
Titles.SetLocale('frFR')
# Titles.SetVerbosity(True)

print (Titles[178]['TitleMale'])