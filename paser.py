#!/usr/bin/python2
# encoding: UTF-8
import re

class Parser:
    def __init__(self, key):
        self.key = key

    def match(self, lines, lineNumber):
        if lineNumber >= len(lines):
            return False
        if self.key in unicode(lines[lineNumber], encoding='utf-8',errors='ignore'):
            return True

        return False

    def parse(self, lines, lineNumber):
        if lineNumber >= len(lines):
            return False
        if self.key in unicode(lines[lineNumber], encoding='utf-8',errors='ignore'):
            return True
        else:
            return False


class BbRe:
    def __init__(self, text, dicts):
        self.dicts = dicts
        self.text = text

    def multiMatch(self):
        match = False
        out = ''
        
        if len(self.dicts) == 0:
            match = True
            out = self.text

        for key, value in self.dicts.items():
            out += ' '
            for matchtext in value:
                patten = re.compile(matchtext + r'[ =:]{1,2}[-]?[0]?[x]?[0-9a-f]+[ ,.]?', re.IGNORECASE)
                m = patten.findall(self.text)
                if m:
                    out += ''.join(m) + ' '
                    match = True
        return match, out
