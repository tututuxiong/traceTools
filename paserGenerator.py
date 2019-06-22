#!/usr/bin/python3
from signalParser import SingalParser
from traceParser import TraceParser
import dciPaserHelp

class PaserGenerator:
    def __init__(self, config):
        self.pasers = []
        key  = ''
        
        filterList = {}
        if 'signal' in config:
            signalList = config['signal']
            for signal in signalList:
                DCI = 0
                for k, v in signal.items():
                    if k == 'text':
                        filterList[k] = v
                    if k == 'DCI':
                        DCI = v
                self.pasers.append(SingalParser(signal['id'], DCI ,**filterList))
                filterList.clear()

        if 'trace' in config:
            traceList = config['trace']
            excludeList = []
            for trace in traceList:
                excludeList = [] 
                for k, v in trace.items():
                    if k != 'id':
                        if k == 'exclude':
                            excludeList = v
                        else:
                            filterList[k] = v
                self.pasers.append(TraceParser(trace['id'], exculdeStrs=excludeList, **filterList))
                filterList.clear()
        
        if 'DCI' in config:
            dciConfigList = config['DCI']
            for config in dciConfigList:
                dciPaserHelp.filteList = config["text"]
                dciPaserHelp.numerology = config["numerology"]
                dciPaserHelp.bandwidth = config["bandwidth"]
                dciPaserHelp.version = config["version"]


    def getPasers(self):
        return self.pasers
