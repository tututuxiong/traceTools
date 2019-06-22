#!/usr/bin/python3
# -*- coding: utf-8 -*-
from signalParser import SingalParser
from traceParser import TraceParser
from paserGenerator import PaserGenerator
import json
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

with open(sys.argv[1]) as f:
    data = json.load(f)

lineNumber = 0
file = open(sys.argv[2])
lines = file.readlines()
pasers = PaserGenerator(data).getPasers()
# ts = TraceSorter()
while lineNumber < len(lines):
    step = 0
    for p in pasers:
        step = 0
        if p.match(lines, lineNumber):
            output, step = p.parse(lines, lineNumber)
            if output:
                break
    if step == 0:
        lineNumber += 1
    else:
        lineNumber += step

# ts.sortOut()
# # ts.plt(['tbSizeInBits'])
#
# fo = open("result.log", "w")
# fo.write(''.join(ts.getTrace()))
# fo.close()
