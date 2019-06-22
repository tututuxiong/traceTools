#!/usr/bin/python3
from datetime import datetime
import re
import functools
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def getdata(key, line):
    patten = re.compile((key + '[ =:](/?\d+)'), re.IGNORECASE)
    m = patten.search(line)
    if m != None:
        return True, m.group(1)
    else:
        return False, 0

def getSFInfo(line):
    patten = re.compile(r'bfn:(/?\d+), sfn:(/?\d+), sf:(/?\d+.\d+), bf:(/?\d+)')
    m = patten.search(line)
    if None != m:
        return True, m.group(1),  m.group(2), m.group(3),  m.group(3), m.group(0)
    else:
        return False,0,0,0,0

def getTime(a):
    # print(a)
    patten = re.compile(r'\[.*?\]')
    m = patten.match(a)
    if m != None:
        time = datetime.strptime((m.group(0)[1:-1]), '%Y-%m-%d %H:%M:%S.%f')
        return time
    else:
        return datetime(year=2030,month=12,day=30)

def bigger(a, b):
    if getTime(a) > getTime(b):
        return 1
    else:
        return -1


class TraceSorter:
    def __init__(self):
        self.traceList = []


    def add(self, newTrace):
        self.traceList.append(newTrace)

    def getTrace(self):
        return self.traceList

    def sortOut(self):
        i = 0
        outputList = []
        sotedList = sorted(self.traceList, key=functools.cmp_to_key(bigger))
        while i < len(sotedList):
            outputList.append(sotedList[i])
            # print(sotedList[i], end='')
            i += 1

        self.traceList.clear()
        self.traceList = outputList

    def plt(self, List = ['']):
        allData = []
        for line in self.traceList:
            isValid, bfn, sfn, sf, bf, sfInfo = getSFInfo(line)
            if isValid:
                for key in List:
                    isValid, data = getdata(key, line)
                    if isValid:
                        allData.append(int(data))

        a = pd.DataFrame(allData, index=np.arange(len(allData)))
        print(a)
        a.plot()
        plt.show()
