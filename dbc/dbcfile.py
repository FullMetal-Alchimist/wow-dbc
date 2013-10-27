#!/usr/bin/env python

import os, io
from struct import Struct, calcsize

from dtypes import *

def MakeStructureFromSkeleton(Skeleton):
    "Creates a Struct from the Skeleton"
    StructDef = ['<'] # Little Endian
    for item in Skeleton:
        if isinstance(item, Array):
            StructDef.extend(x.c for x in item.items)
        else:
            StructDef.append(item.c)
    return Struct(''.join(StructDef))

def GetIndexLocaleArray(Locale):
    if Locale == 'enUS':
        return 0
    elif Locale == 'koKR':
        return 1
    elif Locale == 'frFR':
        return 2
    elif Locale == 'deDE':
        return 3
    elif Locale == 'zhCN':
        return 4
    elif Locale == 'zhTW':
        return 5
    elif Locale == 'esES' or Locale == 'esMX':
        return 6
    elif Locale == '??': # 7
        return 7
    elif Locale == 'ruRU':
        return 8
    else:
        return 0 # Default enUS
    
def MakeLocalizationArray(StringPos, Locale):
    "Create a localization array of 16 fields"
    strings = [int()] * 17
    strings[16] = 16712190 # BitMask
    strings[GetIndexLocaleArray(Locale)] = StringPos
    return strings

def GetLocale(array_localization, str_loc):
    return array_localization[GetIndexLocaleArray(str_loc)]

class DBCRecord(object):
    "A simple object to convert a dict to an object"
    def __init__(self, d, locale = 'enUS'):
        self.RecordData = d
        self.loc = locale

    def __getitem__(self, key):
        if isinstance(self.RecordData[key], list): # Localized String
            return GetLocale(self.RecordData[key], self.loc)
        else:
            return self.RecordData[key]

    def __setitem__(self, key, value):
        self.RecordData[key] = value

class DBCWriter(object):
    """
    DBC writer
    """

    HeaderStructure = Struct('4s4i')

    def __init__(self, filename, skele, locale = 'enUS'):
        self.filename = filename
        self.verbose = False

        self.locale = locale

        self.Skeleton = skele.Skeleton
        self.DataStructure = MakeStructureFromSkeleton(skele.Skeleton)

        self.Data = []
        self.StringBlockStream = io.StringIO()
        self.StringBlockStream.write('\0')

    def SetVerbosity(self, value):
        self.verbose = value 

    def SetLocale(self, locale):
        self.locale = locale

    def Append(self, record):
        Record = []
        for item in record:
            if isinstance(item, str):
                StringPos = self.StringBlockStream.tell()
                if self.verbose:
                    print('[DBC Append Record]: Add to String block (%s) at pos %i.' % \
                        (item, StringPos))

                self.StringBlockStream.write(item)
                self.StringBlockStream.write('\0')
                localizedStr = MakeLocalizationArray(StringPos, self.locale)
                Record.extend(localizedStr)
            else:
                Record.append(item)
        if self.verbose:
            print('[DBC Append Record]: Record added %s.' % Record)
        self.Data.append(Record)

    def Write(self):
        f = open(self.filename, 'wb')

        StringBlock = self.StringBlockStream.getvalue()

        Records = len(self.Data)
        Fields = len(self.Skeleton) - 1 # Without Little Endian.
        RecordSize = self.DataStructure.size
        StringBlockSize = len(StringBlock)

        f.write(self.HeaderStructure.pack(b'WDBC', Records, Fields, RecordSize, StringBlockSize))
        if self.verbose:
            print('[DBC Header]: Header written (%i records, %i fields, %i record size, %i string block size).' % \
                (Records, Fields, RecordSize, StringBlockSize))

        f.seek(20 + Records * RecordSize)
        f.write(StringBlock.encode('utf-8'))
        f.seek(20)

        if self.verbose:
            print('[DBC String Block]: Written (%s).' % StringBlock)

        for Record in self.Data:
            f.write(self.DataStructure.pack(*Record))
            if self.verbose:
                print('[DBC Record]: Record written: %s.' % Record)

        if self.verbose:
            print('[DBC]: Write complete.')


class DBCFile(object):
    """
    Base representation of a DBC file.
    """
    
    header_struct = Struct('4s4i') # 4 char (WDBC) and 4 ints.

    def __init__(self, filename, skele):
        self.filename = filename

        self.verbose = False
        self.locale = 'enUS'

        self.skeleton = skele.Skeleton
        self.struct = MakeStructureFromSkeleton(skele.Skeleton)

        self.HeaderRead = False
        self.StringBlockRead = False
        self.DataRead = False

        self.Data = dict()

    def SetVerbosity(self, value):
        self.verbose = value

    def SetLocale(self, locale):
        self.locale = locale

    def ReadHeader(self):
        if not os.path.exists(self.filename):
            raise Exception("File %s not found" % (self.filename,))

        self.f = open(self.filename, 'rb')

        # Read header
        Signature, Records, Fields, RecordSize, StringBlockSize = self.header_struct.unpack(self.f.read(20))

        # Check if signature is DBC's one
        if (Signature.decode('utf-8')) != str('WDBC'):
            self.f.close()
            raise Exception('Invalid file type (invalid signature: %s)!' % Signature.decode('utf-8'))

        self.Records = Records 
        self.Fields = Fields 
        self.RecordSize = RecordSize
        self.StringBlockSize = StringBlockSize

        if not self.struct:
            self.skeleton = Array('data', Int32, Fields)
            self.__create_struct()

        if self.struct.size != RecordSize:
            self.f.close()
            raise Exception('Struct size mismatch (%d != %d' % (self.struct.size, RecordSize))

        if self.verbose:
            print('[DBC Header]: %i records, %i fields, %i record size, %i string block size.' % \
                (self.Records, self.Fields, self.RecordSize, self.StringBlockSize))

        self.HeaderRead = True

    def ReadStringBlock(self):
        self.f.seek(20 + self.Records * self.RecordSize)
        self.StringBlockBytes = self.f.read(self.StringBlockSize)
        self.StringBlock = self.StringBlockBytes.decode('cp1252')
        self.f.seek(20)

        if self.verbose:
            print('[DBC String Block]: %s' % (self.StringBlock))

        self.StringBlockRead = True

    def ReadData(self):
        try:
            for i in range(self.Records):
                Data_Unpacked = self.struct.unpack(self.f.read(self.RecordSize))
                if self.verbose:
                    print('[DBC Data]: %s' % (Data_Unpacked,))
                record = DBCRecord(self.__process_record(Data_Unpacked), self.locale)
                self.Data[record['Id']] = record
        finally:
            self.f.close()
            self.DataRead = True

    def GetData(self, idx):
        if not self.HeaderRead:
            self.ReadHeader()
        if not self.StringBlockRead:
            self.ReadStringBlock()
        if not self.DataRead:
            self.ReadData()
        if not self.Data[idx]:
            raise Exception('Out of range (Data Index)')

        return self.Data[idx]

    def __getitem__(self, key):
        return self.GetData(key)

    def __setitem__(self, key, value):
        self.DataDBC[key] = value

    def __len__(self):
        return len(self.Data)
   
    def __iter__(self):
        "Iterated based approach to the dbc reading"
        if not self.HeaderRead:
            self.ReadHeader()
        
        if not self.StringBlockRead:
            self.ReadStringBlock()

        if not self.DataRead:
            self.ReadData()

        for Record in self.Data.values():
            yield Record

    def __process_record(self, data):
        "Processes a record (row of data)"
        output = {}
        i = d = 0
        while i < len(self.skeleton):
            if isinstance(self.skeleton[i], Array):
                temp = []
                for t in self.skeleton[i].items:
                    t = self.__process_field(t, data[d])
                    if t:
                        temp.append(t[0])
                        d += 1
                if temp:
                    output[self.skeleton[i].name] = temp
            else:
                t = self.__process_field(self.skeleton[i], data[d])
                if t:
                    output.update(t)
                    d += 1
            i += 1
        return output
    
    def __process_field(self, _type, data):
        "Processes a field inside a record"
        output = {}
        name = _type.name if _type.name else 0 # Default to name of 0 (for arrays)
        if isinstance(_type, String):
            if data == 0:
                output[name] = str()
            else:
                if data > self.StringBlockSize or self.StringBlock[data - 1] != '\0':
                    raise Exception('Invalid string (%i, %s)' % (data, type(_type)))
                else:
                    s = self.StringBlock[data:self.StringBlock.index('\0', data)]
                    output[name] = str(s)
                    if self.verbose:
                        print('[DBC Field]: String %s loaded.' % s)
        elif not isinstance(_type, PadByte): # Ignore PadBytes
            output[name] = data
        return output

