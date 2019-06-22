#!/usr/bin/python3
from paser import Parser
from paser import BbRe
import re, sys
import dciPaserHelp

class SingalParser(Parser):
    def __init__(self, signalName, dci, **kwargs):
        self.single = signalName
        self.key = signalName + ' {'
        self.includeStr = {}
        self.dci = dci
        for key, value in kwargs.items():
            self.includeStr[key] = value

    def parse(self, lines, lineNumber):
        count = 1
        output = ''
        step = 0
        # output += lines[lineNumber-1] + lines[lineNumber]
        output += lines[lineNumber]
        while count != 0:
            lineNumber += 1
            if '{' in lines[lineNumber]:
                count += 1
            if '}' in lines[lineNumber]:
                count -= 1
            step += 1

            if step > 300:
                break
            output += lines[lineNumber]

        sys.stdout.write(str(lineNumber + 1) + ':')
        sys.stdout.write(self.single)
        sys.stdout.flush()

        match,lineoutPut = BbRe(output, self.includeStr).multiMatch()
        if match:
            print(lineoutPut)
            if 'NR_PDCCH_IND' in self.key and self.dci:
                dciPartList = []
                DciType = 0
                dciPartList, DciType = dciPaserHelp.getDciMsg(lineoutPut)
                dciResult = "DCI : " 
                dciResult += dciPaserHelp.parseDci(dciPartList[0],dciPartList[1],dciPartList[2],dciPartList[3],DciType)
                print(dciResult)
            
            return output, step
        else:
            return None, 0




