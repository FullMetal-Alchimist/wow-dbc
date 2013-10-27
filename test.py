#!/usr/bin/env python

from dbc import *

Titles = CharTitlesDBC('CharTitles.dbc')
Titles.SetLocale('frFR')

NewTitle = [178, '%s Bezarius', '%s Bezarius', 178]
skeleton = [
        Int32('Id'),
        PadByte(),#Int32('condition), Never used
        Localization('TitleMale'),
        Localization('TitleFemale'),
        Int32('SelectionIndex'),
]

TestTitleWrite = DBCWriter('CharTitlesTest.dbc', skeleton, 'frFR')
TestTitleWrite.SetVerbosity(True)

TestTitleWrite.Append(NewTitle)

TestTitleWrite.Write()