#!/usr/bin/python

import subprocess
import re
p = subprocess.Popen(['/usr/bin/python ./nrDci.py -b 20 -dci11 -dec 63488-1092-36940-0000 -v153 -n 1'], shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
p.stdin.write('1\n')
p.stdin.write('3\n')

for line in p.stdout.readlines():
  if "dai" in line:
    patten = re.compile(r': [0-9]+ ', re.IGNORECASE)
    m = patten.search(line)
    print(m.group(0))



def genCmd(part1, part2, part3, part4, dciType)
{
    if dciType == 1:
        
}
