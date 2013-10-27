#!/usr/bin/env python

from dbc import *

Titles = DBCFile('CharTitles.dbc', CharTitlesDBC)
Titles.SetLocale('frFR')
Titles.SetVerbosity(True)

print (Titles[1]['TitleMale'])

NewTitle = [178, '%s Bezarius', '%s Bezarius', 178]
skeleton = [
        Int32('Id'),
        PadByte(),#Int32('condition), Never used
        Localization('TitleMale'),
        Localization('TitleFemale'),
        Int32('SelectionIndex'),
]

TestTitleWrite = DBCWriter('CharTitlesTest.dbc', CharTitlesDBC, 'frFR')
TestTitleWrite.SetVerbosity(True)

TestTitleWrite.Append(NewTitle)

TestTitleWrite.Write()

TestTitleRead = DBCFile('CharTitlesTest.dbc', CharTitlesDBC)
TestTitleRead.SetLocale('frFR')
TestTitleRead.SetVerbosity(True)

print (TestTitleRead[178]['TitleMale'])