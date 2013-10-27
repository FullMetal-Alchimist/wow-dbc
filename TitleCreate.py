#!/usr/bin/env python

import sys, argparse
from dbc import *

Parser = argparse.ArgumentParser(description='Add new titles to CharTitles.dbc')
Parser.add_argument('dbc_filename_input', metavar="dbc_input_file", type=str, help="Path to CharTitles.dbc (input)")
Parser.add_argument('dbc_filename_output', metavar="dbc_output_file", type=str, help="Path to CharTitles.dbc (output)")
Parser.add_argument('titles_filename_input', metavar="titles_file", type=str, help="File where Titles are written")
Parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", help="Verbosity")

args = []

if len(sys.argv) < 2:
	print('Will activate interactive prompt.')
	str_args = input('stdin: ')
	args = str_args.split()
else:
	args = sys.argv[1::]

Arguments = Parser.parse_args(args)

InputDBC = DBCFile(Arguments.dbc_filename_input, CharTitlesDBC, 'frFR')
InputDBC.SetVerbosity(Arguments.verbose)
InputDBC.Load()

OutputDBC = DBCWriter(Arguments.dbc_filename_output, CharTitlesDBC, 'frFR')
OutputDBC.SetVerbosity(Arguments.verbose)

OutputDBC.AddRecords(InputDBC.GetRecords())

Title_File = open(Arguments.titles_filename_input, 'r')
for Line in Title_File:
	TitleData = Line.split(';')
	TitleDBCData = [int(TitleData[2]), TitleData[0], TitleData[1], int(TitleData[3])] # Title Male - Title Female - ID - SelectionIndex
	OutputDBC.Append(TitleDBCData)
	if Arguments.verbose:
		print('Title %i - %s added.' % (TitleData[2], TitleData[0]))

OutputDBC.Write()

print('DBC written. Finished.')