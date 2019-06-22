#!/usr/bin/python3
from paser import Parser
from paser import BbRe
import re, sys

class TraceParser(Parser):
    def __init__(self, key, exculdeStrs=[], **kwargs):
        self.key = key
        self.includeStr = {}
        self.exculdeStrs = exculdeStrs
        for key, value in kwargs.items():
            self.includeStr[key] = value


    def parse(self, lines, lineNumber):
        discard = False
        line = lines[lineNumber]

        for exculdeStr in self.exculdeStrs:
            if exculdeStr in line:
                discard = True

        if discard == False:
            sys.stdout.write(str(lineNumber + 1) + ': ' + self.key + ' ')
            sys.stdout.flush()
            match,lineoutPut = BbRe(line[line.find(self.key):], self.includeStr).multiMatch()
            if match:
                print(lineoutPut)
                return line, 0
            else:
                return None, 0
        else:
            return None, 0
