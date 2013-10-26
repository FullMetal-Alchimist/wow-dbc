#!/usr/bin/env python

import os
from struct import Struct

from dtypes import *

class DBCRecord(object):
    "A simple object to convert a dict to an object"
    def __init__(self, d):
        self.RecordData = d

    def __getitem__(self, key):
        return self.RecordData[key]

    def __setitem__(self, key, value):
        self.RecordData[key] = value

class DBCFile(object):
    """
    Base representation of a DBC file.
    """
    
    header_struct = Struct('4s4i') # 4 char (WDBC) and 4 ints.

    def __init__(self, filename, skele=None):
        self.filename = filename

        self.verbose = False

        if not hasattr(self, 'skeleton'):
            self.skeleton = skele
        self.__create_struct()

        self.HeaderRead = False
        self.StringBlockRead = False
        self.DataRead = False

        self.Data = dict()

    def SetVerbosity(self, value):
        self.verbose = value

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
        self.StringBlock = self.f.read(self.StringBlockSize).decode('cp850')
        self.f.seek(20)

        if self.verbose:
            print('[DBC String Block]: %s' % (self.StringBlock.encode('cp850')))

        self.StringBlockRead = True

    def ReadData(self):
        try:
            for i in range(self.Records):
                Data_Unpacked = self.struct.unpack(self.f.read(self.RecordSize))
                if self.verbose:
                    print('[DBC Data]: %s' % (Data_Unpacked,))
                record = DBCRecord(self.__process_record(Data_Unpacked))
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

    def __create_struct(self):
        "Creates a Struct from the Skeleton"
        if self.skeleton:
            s = ['<']
            for item in self.skeleton:
                if isinstance(item, Array):
                    s.extend(x.c for x in item.items)
                else:
                    s.append(item.c)
            self.struct = Struct(''.join(s))
        else:
            self.struct = None

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

