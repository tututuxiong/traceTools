#!/usr/bin/python

import subprocess
import re
# p = subprocess.Popen(['/usr/bin/python ./nrDci.py -b 20 -dci11 -dec 63488-1092-36940-0000 -v153 -n 1'], shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
# p.stdin.write('1\n')
# p.stdin.write('3\n')

# for line in p.stdout.readlines():
#   if "dai" in line:
#     patten = re.compile(r': [0-9]+ ', re.IGNORECASE)
#     m = patten.search(line)
#     print(m.group(0))



pattenDciMsg = re.compile(r'dciMsg [0-9]+', re.IGNORECASE)
pattenNumber = re.compile(r'[0-9]+', re.IGNORECASE)
pattenDciType = re.compile(r'dciFormatType [0-9]', re.IGNORECASE)
filteList = []
version = 0
bandwidth = 0
numerology = 0

def genCmd(part1, part2, part3, part4, dciType):
    InteracteCmd = []
    dciTypeCmd = ' -'
    dciMsg = ' -dec '
    cmdVersion = ' -v'
    cmdVersion += str(version)
    cmdNumerology = ' -n ' + str(numerology)

    dciMsg += (str(part1) + '-')
    dciMsg += (str(part2) + '-')
    dciMsg += (str(part3) + '-')
    dciMsg += str(part4)

    if dciType == 0:
        dciTypeCmd += 'dci00'

    if dciType == 1:
        dciTypeCmd += 'dci01'
        InteracteCmd.append('1\n')
        InteracteCmd.append('3\n')

    if dciType == 2:
        dciTypeCmd += 'dci10'

    if dciType == 3:
        dciTypeCmd += 'dci11'
        InteracteCmd.append('1\n')
        InteracteCmd.append('3\n')
    
    cmd = '/usr/bin/python ./nrDci.py -b ' + str(bandwidth) + dciTypeCmd + dciMsg + cmdVersion + cmdNumerology 
    return cmd, InteracteCmd
    
def parseDcibyPopen(cmd,InteracteCmd, filteList):
    p = subprocess.Popen([cmd], shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

    for c in InteracteCmd:
        p.stdin.write(c)
    
    patten = re.compile(r': [0-9]+ ', re.IGNORECASE)
    output = ''
    for line in p.stdout.readlines():
        for key in filteList:
            if key in line:
                m = patten.search(line)
                if m:
                    output += key +  m.group(0) + ','
    

    return output

def parseDci(part1, part2, part3, part4, dciType):
    cmd = ''
    InteracteCmd = []
    output = ''
    cmd, InteracteCmd = genCmd(part1, part2, part3, part4, int(dciType))
    output = parseDcibyPopen(cmd,InteracteCmd,filteList)
    return output

def getDciMsg(line):
    dcimsgList = []
    DciType = 0
    m = pattenDciMsg.findall(line)
    if m:
        for eachpart in m:
            numberPart = pattenNumber.search(eachpart)
            if numberPart:
                dcimsgList.append(numberPart.group(0))

    m = pattenDciType.search(line)
    if m:
        n = pattenNumber.search(m.group(0))
        if n:
            DciType = n.group(0)

    return dcimsgList, DciType

