#!/usr/bin/env python

from dbc import *

Titles = CharTitlesDBC('CharTitles.dbc')
Titles.SetLocale('frFR')

Titles[2]['TitleMale'] = 'Ultimate %s'
print (Titles[2]['TitleMale'])