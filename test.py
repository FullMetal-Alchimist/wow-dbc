#!/usr/bin/env python

from dbc import *

Titles = CharTitlesDBC('CharTitles.dbc')
Titles.SetLocale('frFR')

print (Titles[2]['TitleMale'])