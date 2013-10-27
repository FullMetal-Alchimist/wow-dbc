#!/usr/bin/env python

from dbc import *

# Read Legacy file

Titles = DBCFile('CharTitles.dbc', CharTitlesDBC)
Titles.SetLocale('frFR')
# Titles.SetVerbosity(True)
Titles.Load()

# Write in DBC
NewTitle = [178, '%s Bezarius', '%s Bezarius', 178]

TestTitleWrite = DBCWriter('CharTitlesTest.dbc', CharTitlesDBC, 'frFR')
# TestTitleWrite.SetVerbosity(True)

TestTitleWrite.AddRecords(Titles.GetRecords())
TestTitleWrite.Append(NewTitle)

TestTitleWrite.Write()

# Read written file

TestTitleRead = DBCFile('CharTitlesTest.dbc', CharTitlesDBC)
TestTitleRead.SetLocale('frFR')
# TestTitleRead.SetVerbosity(True)

print (TestTitleRead[178]['TitleMale'])