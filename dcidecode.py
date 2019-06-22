#!/usr/bin/python3

import nrDci

nrDci.gDciFormat = nrDci.NR_DCI_FORMAT_0_0 
nrDci.gBandwidth = 20 
nrDci.gDciMsg = [3238,49610,33792,0]
nrDci.gDecoding3gppVersion = nrDci.DCI_SPEC_V15_3
nrDci.gDciBase3gppVersion = nrDci.DCI_SPEC_V15_2
nrDci.g3gppSpecified = False
nrDci.gNumerology = 1
nrDci.buildDciSchematic()
print(nrDci.dciSchematic)
