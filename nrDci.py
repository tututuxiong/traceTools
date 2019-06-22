#!usr/bin/python

import sys, os
import re
import signal
import subprocess
import time
import datetime
import getpass
import copy
import readline
#import Tkinter

nrDciVersion = "v15_3_2018-12-14"
## Revision History:
## v15_3_2018-11-26: 
##    1) Add new 3GPP Spec version input parameters to allow users to specify a
##       specific 3GPP Spec for DCI decoding/encoding:
##       -v152 for 3GPP Spec 15.2
##       -v153 for 3GPP Spec 15.3
##    2) Add DMRS_SEQ_INIT for DCI11 and DCI01
##    3) Add SI_INDICATOR for DCI10SIB
## v15_3_2018-12-14: 
##    Add support of DCI 0_0 ased on 15.3 spec
## v15_3_2019-1-16: 
##    Switch to v153 default.
## v15_3_2019-1-17: 
##    Adding support of BW 5/15, and added Numerology as input.



DCI_SPEC_V15_2 = '15.2'
DCI_SPEC_V15_3 = '15.3'



NR_DCI_FORMAT_1_1 = 'DCI 1_1'
NR_DCI_FORMAT_0_0 = 'DCI 0_0'
NR_DCI_FORMAT_0_1 = 'DCI 0_1'
NR_DCI_FORMAT_1_0 = 'DCI 1_0 TC_RNTI'
NR_DCI_FORMAT_1_0_SIB = 'DCI 1_0 SIB'
NR_DCI_FORMAT_1_0_RA  = 'DCI 1_0 RA'
NR_DCI_FORMAT_NULL = 'DCI_UNK'

NR_BW_5 = 5
NR_BW_10 = 10
NR_BW_15 = 15
NR_BW_20 = 20
NR_BW_40 = 40
NR_BW_60 = 60
NR_BW_80 = 80
NR_BW_100 = 100
NR_BW_NULL = 0

NR_BW = (NR_BW_5, NR_BW_10, NR_BW_15, NR_BW_20, NR_BW_40, NR_BW_60, NR_BW_80, NR_BW_100)
NR_NOOF_BW = len(NR_BW)

NR_ALLOC_TYPE_0 = 0
NR_ALLOC_TYPE_1 = 1
NR_ALLOC_TYPE_NULL = 'UnKnown'

UL_DCI_HEADER_VAL = 0
DL_DCI_HEADER_VAL = 1

NUMEROLOGY0 = 0
NUMEROLOGY1 = 1

NR_NUMEROLOGY = (NUMEROLOGY0, NUMEROLOGY1)

NR_ALLOC_TYPES = (NR_ALLOC_TYPE_0, NR_ALLOC_TYPE_1)

gDciFormat = NR_DCI_FORMAT_NULL
gBandwidth = NR_BW_NULL
gDciMsg = []
gDecoding3gppVersion = DCI_SPEC_V15_3
gDciBase3gppVersion = DCI_SPEC_V15_2
g3gppSpecified = False
## HAVE to add new version as the last element
gAll3gppVersions = (DCI_SPEC_V15_2,
                    DCI_SPEC_V15_3)
gNumerology = None

SCHEMATIC = 'Schematic'
ENUM_VALUE = "EnumVal"
FIELD_SIZE = 'FieldSize'
TOTAL_DCI_NOF_BITS = 'DciMsgBits'
VALUE = 'dciValue'
BITMASK = 'bitMask'
SHIFT = 'bitShift'
INPUT_DCI_VALUE = 'inputDciValue'
VARIABLE_SIZE = 'variableField'
ALLOC_TYPE = 'allocType'
NOF_BIT_FIELDS = 'No Of Bit Fields'
OUTPUT_DCI_VALUE = 'outputDciValue'
USER_BF_VALUE = 'UserInputBitFieldValue'
BITS_MAX = 'maxSize'
BITS_MIN = 'minSize'



NR_ALLOC_TYPE0_RIV_BIT_SIZE = {}
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY0] = {}
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_5] = 13
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_10] = 13
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_15] = 10
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_20] = 14
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1] = {}
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_20] = 13
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_40] = 14
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_60] = 11
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_80] = 14
NR_ALLOC_TYPE0_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_100] = 18

NR_ALLOC_TYPE1_RIV_BIT_SIZE = {}
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY0] = {}
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_5] = 9
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_10] = 11
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_15] = 12
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY0][NR_BW_20] = 13
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1] = {}
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_20] = 11
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_40] = 13
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_60] = 14
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_80] = 15
NR_ALLOC_TYPE1_RIV_BIT_SIZE[NUMEROLOGY1][NR_BW_100] = 16

## COMMON DCI fields
NR_DCI_HEADER           = 'header'
NR_DCI_MCS              = 'mcs'
NR_DCI_RV               = 'rv'
NR_DCI_NDI              = 'ndi'
NR_DCI_HPID             = 'hpId'
NR_DCI_RIV            = 'riv'
NR_DCI_SLIV           = 'sliv'
NR_DCI_DMRS_SEQ_INIT  = 'DMRS Seq Init'
## COMMON DCI bit field size
NR_BIT_SIZE_VARIABLE      = 0 ## Used to specify the size of variable bit field
NR_MCS_BIT_LEN            = 5
NR_HPID_BIT_LEN           = 4
NR_NDI_BIT_LEN            = 1
NR_RV_BIT_LEN             = 2
NR_DCI_HEADER_BIT_LEN     = 1
NR_DCI_DMRS_SEQ_INIT_LEN  = 1


###############################
###############################
##
## Common/shared DCI fields
##
###############################
###############################
NR_DCI_PUCCH_TPC      = 'PUCCH TPC'
NR_DCI_PUCCH_RES_IND  = 'PUCCH Res Ind'
NR_DCI_K1_IND         = 'PDSCH2Harq FB Ind'

NR_DCI_PUCCH_TPC_BIT_LEN     = 2
NR_DCI_PUCCH_RES_IND_BIT_LEN = 3
NR_DCI_K1_IND_BIT_LEN        = 3



###############################
###############################
##
## DCI 0_0 specific scrambled by TC/C_RNTI
##
###############################
###############################
NR_DCI00_PADDING              = 'Padding'
NR_DCI00_FREQ_HOPPING         = 'Freq Hopping Flag'
## DCI 0_0 specific bit field size
NR_DCI00_SLIV_BIT_LEN         = 4
NR_DCI00_PADDING_BIT_LEN      = 8
NR_DCI00_FREQ_HOPPING_BIT_LEN = 1

NR_DCI00_V152_SCHEMATIC = (NR_DCI_HEADER,
                           NR_DCI_RIV,
                           NR_DCI_SLIV,
                           NR_DCI00_FREQ_HOPPING,
                           NR_DCI_MCS,
                           NR_DCI_NDI,
                           NR_DCI_RV,
                           NR_DCI_HPID,
                           NR_DCI_PUCCH_TPC,
                           NR_DCI00_PADDING)

NR_DCI00_V152_FIELD_SIZE = {}
NR_DCI00_V152_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE
NR_DCI00_V152_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI00_SLIV_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI00_FREQ_HOPPING] = NR_DCI00_FREQ_HOPPING_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI_PUCCH_TPC] = NR_DCI_PUCCH_TPC_BIT_LEN
NR_DCI00_V152_FIELD_SIZE[NR_DCI00_PADDING] = NR_DCI00_PADDING_BIT_LEN



###############################
###############################
##
## DCI 0_1 specific scrambled by C_RNTI
##
###############################
###############################
NR_DCI01_DAI1             = 'dai_1'
NR_DCI01_PUSCH_TPC        = 'PUSCH TPC'
NR_DCI01_ANTENNA_PORTS    = 'Antenna Ports'
NR_DCI01_SRS_REQ          = 'SRS Request'
NR_DCI01_CSI_REQ          = 'CSI Request'  ## variable length
NR_DCI01_UL_SCH           = 'UL SCH IND'
## DCI 0_1 specific bit field size
NR_DCI01_DAI1_BIT_LEN             = 2
NR_DCI01_SLIV_BIT_LEN             = 3
NR_DCI01_PUSCH_TPC_BIT_LEN        = 2
NR_DCI01_ANTENNA_PORTS_BIT_LEN    = 3
NR_DCI01_SRS_REQ_BIT_LEN          = 2
NR_DCI01_UL_SCH_BIT_LEN           = 1
NR_DCI01_CSI_REQ_MAX_BITS         = 3 ## use to check against user input
NR_DCI01_CSI_REQ_MIN_BITS         = 0 ## use to check against user input



NR_DCI01_V152_SCHEMATIC = (NR_DCI_HEADER,
                           NR_DCI_RIV,
                           NR_DCI_SLIV,
                           NR_DCI_MCS,
                           NR_DCI_NDI,
                           NR_DCI_RV,
                           NR_DCI_HPID,
                           NR_DCI01_DAI1,
                           NR_DCI01_PUSCH_TPC,
                           NR_DCI01_ANTENNA_PORTS,
                           NR_DCI01_SRS_REQ,
                           NR_DCI01_CSI_REQ,
                           NR_DCI01_UL_SCH)

NR_DCI01_V152_FIELD_SIZE = {}
NR_DCI01_V152_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE
NR_DCI01_V152_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI01_SLIV_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_DAI1] = NR_DCI01_DAI1_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_PUSCH_TPC] = NR_DCI01_PUSCH_TPC_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_ANTENNA_PORTS] = NR_DCI01_ANTENNA_PORTS_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_SRS_REQ] = NR_DCI01_SRS_REQ_BIT_LEN
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_CSI_REQ] = NR_BIT_SIZE_VARIABLE
NR_DCI01_V152_FIELD_SIZE[NR_DCI01_UL_SCH] = NR_DCI01_UL_SCH_BIT_LEN



NR_DCI01_V153_SCHEMATIC = (NR_DCI_HEADER,
                           NR_DCI_RIV,
                           NR_DCI_SLIV,
                           NR_DCI_MCS,
                           NR_DCI_NDI,
                           NR_DCI_RV,
                           NR_DCI_HPID,
                           NR_DCI01_DAI1,
                           NR_DCI01_PUSCH_TPC,
                           NR_DCI01_ANTENNA_PORTS,
                           NR_DCI01_SRS_REQ,
                           NR_DCI01_CSI_REQ,
                           NR_DCI_DMRS_SEQ_INIT,
                           NR_DCI01_UL_SCH)

NR_DCI01_V153_FIELD_SIZE = {}
NR_DCI01_V153_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE
NR_DCI01_V153_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI01_SLIV_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_DAI1] = NR_DCI01_DAI1_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_PUSCH_TPC] = NR_DCI01_PUSCH_TPC_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_ANTENNA_PORTS] = NR_DCI01_ANTENNA_PORTS_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_SRS_REQ] = NR_DCI01_SRS_REQ_BIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_CSI_REQ] = NR_BIT_SIZE_VARIABLE
NR_DCI01_V153_FIELD_SIZE[NR_DCI_DMRS_SEQ_INIT] = NR_DCI_DMRS_SEQ_INIT_LEN
NR_DCI01_V153_FIELD_SIZE[NR_DCI01_UL_SCH] = NR_DCI01_UL_SCH_BIT_LEN










###############################
###############################
##
## DCI 1_0 specific scrambled by TC_RNTI
##
###############################
###############################
NR_DCI10_VPRB2PRB_MAPPING = 'vPrb2Prb Mapping'
NR_DCI10_DAI              = 'dai'
## DCI10 specific bit field size
NR_DCI10_VPRB2PRB_MAPPING_BIT_LEN = 1
NR_DCI10_SLIV_BIT_LEN             = 4
NR_DCI10_DAI_BIT_LEN              = 2

NR_DCI10_SCHEMATIC = (NR_DCI_HEADER,
                      NR_DCI_RIV,
                      NR_DCI_SLIV,
                      NR_DCI10_VPRB2PRB_MAPPING,
                      NR_DCI_MCS,
                      NR_DCI_NDI,
                      NR_DCI_RV,
                      NR_DCI_HPID,
                      NR_DCI10_DAI,
                      NR_DCI_PUCCH_TPC,
                      NR_DCI_PUCCH_RES_IND,
                      NR_DCI_K1_IND)

NR_DCI10_FIELD_SIZE = {}
NR_DCI10_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE
NR_DCI10_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI10_SLIV_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI10_VPRB2PRB_MAPPING] = NR_DCI10_VPRB2PRB_MAPPING_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI10_DAI] = NR_DCI10_DAI_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_PUCCH_TPC] = NR_DCI_PUCCH_TPC_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_PUCCH_RES_IND] = NR_DCI_PUCCH_RES_IND_BIT_LEN
NR_DCI10_FIELD_SIZE[NR_DCI_K1_IND] = NR_DCI_K1_IND_BIT_LEN


###############################
###############################
##
## DCI 1_0 specific scrambled by SI_RNTI
##
###############################
###############################
NR_DCI10SIB_RESERVED   = 'Reserved'
NR_DCI10SIB_SI_IND     = 'SI Indicator'
## DCI10SIB specific bit field size
NR_DCI10SIB_SI_IND_LEN   = 1
NR_DCI10SIB_V152_RESERVED_BIT_LEN   = 16
NR_DCI10SIB_V153_RESERVED_BIT_LEN   = 15

NR_DCI10SIB_V152_SCHEMATIC = (NR_DCI_RIV,
                         NR_DCI_SLIV,
                         NR_DCI10_VPRB2PRB_MAPPING,
                         NR_DCI_MCS,
                         NR_DCI_RV,
                         NR_DCI10SIB_RESERVED)
NR_DCI10SIB_V152_FIELD_SIZE = {}
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE 
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI10_SLIV_BIT_LEN
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI10_VPRB2PRB_MAPPING] = NR_DCI10_VPRB2PRB_MAPPING_BIT_LEN
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI10SIB_V152_FIELD_SIZE[NR_DCI10SIB_RESERVED] = NR_DCI10SIB_V152_RESERVED_BIT_LEN

NR_DCI10SIB_V153_SCHEMATIC = (NR_DCI_RIV,
                              NR_DCI_SLIV,
                              NR_DCI10_VPRB2PRB_MAPPING,
                              NR_DCI_MCS,
                              NR_DCI_RV,
                              NR_DCI10SIB_SI_IND,
                              NR_DCI10SIB_RESERVED)
NR_DCI10SIB_V153_FIELD_SIZE = {}
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE 
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI10_SLIV_BIT_LEN
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI10_VPRB2PRB_MAPPING] = NR_DCI10_VPRB2PRB_MAPPING_BIT_LEN
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI10SIB_SI_IND] = NR_DCI10SIB_SI_IND_LEN
NR_DCI10SIB_V153_FIELD_SIZE[NR_DCI10SIB_RESERVED] = NR_DCI10SIB_V153_RESERVED_BIT_LEN

###############################
###############################
##
## DCI 1_0 specific scrambled by RA_RNTI
##
###############################
###############################
NR_DCI10RA_TB_SCALING   = 'TB Scaling'
NR_DCI10RA_RESERVED   = 'Reserved'
## DCI10SIB specific bit field size
NR_DCI10RA_TB_SCALING_BIT_LEN   = 2
NR_DCI10RA_RESERVED_BIT_LEN   = 16

NR_DCI10RA_SCHEMATIC = (NR_DCI_RIV,
                        NR_DCI_SLIV,
                        NR_DCI10_VPRB2PRB_MAPPING,
                        NR_DCI_MCS,
                        NR_DCI10RA_TB_SCALING,
                        NR_DCI10RA_RESERVED)

NR_DCI10RA_FIELD_SIZE = {}
NR_DCI10RA_FIELD_SIZE[NR_DCI_RIV] = NR_BIT_SIZE_VARIABLE 
NR_DCI10RA_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI10_SLIV_BIT_LEN
NR_DCI10RA_FIELD_SIZE[NR_DCI10_VPRB2PRB_MAPPING] = NR_DCI10_VPRB2PRB_MAPPING_BIT_LEN
NR_DCI10RA_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI10RA_FIELD_SIZE[NR_DCI10RA_TB_SCALING] = NR_DCI10RA_TB_SCALING_BIT_LEN
NR_DCI10RA_FIELD_SIZE[NR_DCI10RA_RESERVED] = NR_DCI10RA_RESERVED_BIT_LEN



###############################
###############################
##
## DCI 1_1 specific
##
###############################
###############################
NR_DCI11_DAI            = 'dai'
NR_DCI11_ANT_PORT       = 'Antenna Ports'
NR_DCI11_SRS_REQ        = 'SRS Request'
## DCI11 specific bit field size
NR_DCI11_SLIV_BIT_LEN       = 1
NR_DCI11_DAI_BIT_LEN        = 2
NR_DCI11_ANT_PORTS_BIT_LEN  = 4
NR_DCI11_SRS_REQ_BIT_LEN    = 2
NR_DCI11_SLIV_MIN_BITS      = 0
NR_DCI11_SLIV_MAX_BITS      = NR_DCI11_SLIV_BIT_LEN
NR_DCI11_KI_IND_MIN_BITS      = 1
NR_DCI11_KI_IND_MAX_BITS      = NR_DCI_K1_IND_BIT_LEN

NR_DCI11_V152_SCHEMATIC = (NR_DCI_HEADER,
                           NR_DCI_RIV,
                           NR_DCI_SLIV,
                           NR_DCI_MCS,
                           NR_DCI_NDI,
                           NR_DCI_RV,
                           NR_DCI_HPID,
                           NR_DCI11_DAI,
                           NR_DCI_PUCCH_TPC,
                           NR_DCI_PUCCH_RES_IND,
                           NR_DCI_K1_IND,
                           NR_DCI11_ANT_PORT,
                           NR_DCI11_SRS_REQ)

NR_DCI11_V152_FIELD_SIZE = {}
NR_DCI11_V152_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_RIV]  = NR_BIT_SIZE_VARIABLE
NR_DCI11_V152_FIELD_SIZE[NR_DCI_SLIV] = NR_DCI11_SLIV_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI11_DAI] = NR_DCI11_DAI_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_PUCCH_TPC] = NR_DCI_PUCCH_TPC_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_PUCCH_RES_IND] = NR_DCI_PUCCH_RES_IND_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI_K1_IND] = NR_DCI_K1_IND_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI11_ANT_PORT] = NR_DCI11_ANT_PORTS_BIT_LEN
NR_DCI11_V152_FIELD_SIZE[NR_DCI11_SRS_REQ] = NR_DCI11_SRS_REQ_BIT_LEN


NR_DCI11_V153_SCHEMATIC = (NR_DCI_HEADER,
                           NR_DCI_RIV,
                           NR_DCI_SLIV,
                           NR_DCI_MCS,
                           NR_DCI_NDI,
                           NR_DCI_RV,
                           NR_DCI_HPID,
                           NR_DCI11_DAI,
                           NR_DCI_PUCCH_TPC,
                           NR_DCI_PUCCH_RES_IND,
                           NR_DCI_K1_IND,
                           NR_DCI11_ANT_PORT,
                           NR_DCI11_SRS_REQ,
                           NR_DCI_DMRS_SEQ_INIT)


NR_DCI11_V153_FIELD_SIZE = {}
NR_DCI11_V153_FIELD_SIZE[NR_DCI_HEADER] = NR_DCI_HEADER_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_RIV]  = NR_BIT_SIZE_VARIABLE
NR_DCI11_V153_FIELD_SIZE[NR_DCI_SLIV] = NR_BIT_SIZE_VARIABLE
NR_DCI11_V153_FIELD_SIZE[NR_DCI_MCS] = NR_MCS_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_NDI] = NR_NDI_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_RV] = NR_RV_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_HPID] = NR_HPID_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI11_DAI] = NR_DCI11_DAI_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_PUCCH_TPC] = NR_DCI_PUCCH_TPC_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_PUCCH_RES_IND] = NR_DCI_PUCCH_RES_IND_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_K1_IND] = NR_BIT_SIZE_VARIABLE
NR_DCI11_V153_FIELD_SIZE[NR_DCI11_ANT_PORT] = NR_DCI11_ANT_PORTS_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI11_SRS_REQ] = NR_DCI11_SRS_REQ_BIT_LEN
NR_DCI11_V153_FIELD_SIZE[NR_DCI_DMRS_SEQ_INIT] = NR_DCI_DMRS_SEQ_INIT_LEN



NR_DCI_VAR_SIZE_FIELD_MIN_MAX = {}
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI01_CSI_REQ] = {}
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI01_CSI_REQ][BITS_MAX] = NR_DCI01_CSI_REQ_MAX_BITS
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI01_CSI_REQ][BITS_MIN] = NR_DCI01_CSI_REQ_MIN_BITS
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_SLIV] = {}
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_SLIV][BITS_MAX] = NR_DCI11_SLIV_MAX_BITS
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_SLIV][BITS_MIN] = NR_DCI11_SLIV_MIN_BITS
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_K1_IND] = {}
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_K1_IND][BITS_MAX] = NR_DCI11_KI_IND_MAX_BITS
NR_DCI_VAR_SIZE_FIELD_MIN_MAX[NR_DCI_K1_IND][BITS_MIN] = NR_DCI11_KI_IND_MIN_BITS




NR_DCI_SCHEMATIC = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][ENUM_VALUE] = 3
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI11_V152_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI11_V152_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_0
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][SCHEMATIC] = NR_DCI11_V153_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][FIELD_SIZE] = NR_DCI11_V153_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_1][DCI_SPEC_V15_3][ALLOC_TYPE] = NR_ALLOC_TYPE_0


NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][ENUM_VALUE] = 2
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI10_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI10_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_1

NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][ENUM_VALUE] = 2
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI10SIB_V152_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI10SIB_V152_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_1
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][SCHEMATIC] = NR_DCI10SIB_V153_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][FIELD_SIZE] = NR_DCI10SIB_V153_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_SIB][DCI_SPEC_V15_3][ALLOC_TYPE] = NR_ALLOC_TYPE_1



NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][ENUM_VALUE] = 2
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI10RA_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI10RA_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_1_0_RA][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_1

NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][ENUM_VALUE] = 1
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI01_V152_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI01_V152_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_1

NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][SCHEMATIC] = NR_DCI01_V153_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][FIELD_SIZE] = NR_DCI01_V153_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_1][DCI_SPEC_V15_3][ALLOC_TYPE] = NR_ALLOC_TYPE_1


NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][ENUM_VALUE] = 0
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2] = {}
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][SCHEMATIC] = NR_DCI00_V152_SCHEMATIC
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][FIELD_SIZE] = NR_DCI00_V152_FIELD_SIZE
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][VARIABLE_SIZE] = [] ## will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][BITMASK] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][SHIFT] = {} # will be filled in later on
NR_DCI_SCHEMATIC[NR_DCI_FORMAT_0_0][DCI_SPEC_V15_2][ALLOC_TYPE] = NR_ALLOC_TYPE_1

#########################################################################################
def convertNumericStrToInt(numericStr, err=True):
  try:
    return int(numericStr)
  except:
    if err:
      print("Invalid numeric provided : " + numericStr)
    return None

#########################################################################################
def convertHexStrToInt(hexStr, err=True):
  try:
    return int(hexStr, 16)
  except:
    if err:
      print("Invalid Hex string provided : " + hexStr)
    return None

#########################################################################################
def exitProg():
  sys.exit()

#########################################################################################
def printUsage(errStr=''):
  global gDecoding3gppVersion
  print "%s\n"%errStr
  print "python nrDci.py -b <bw> -dci<XX> [options]"
  print ""
  print ""
  print " -n <numerology> : MANDATORY. <numerology> is the numerology index for the cell"
  print "                   Valid values: 0 for numerology0"
  print "                               : 1 for numerology1"
  print " -b <bw>     : MANDATORY. <bw> is the cell bandwidth in MHz value"
  print "               Valid values: 10/20 for FDD numerology 0"
  print "                             20/40/60/80/100 for TDD numerology 1"
  print " -dci<XX>    : MANDATORY. <XX> is the DCI type."
  print "               VAlid values: -dci01 -dci10 -dci10ra -dci10sib -dci11"
  print "                 -dci00 : for msg3 retx UL grants"
  print "                 -dci01 : for all UL grants"
  print "                 -dci10 : for DCI 1_0 scrambled by TC_RNTI"
  print "                 -dci10ra : for DCI 1_0 scrambled by RA_RNTI"
  print "                 -dci10sib : for DCI 1_0 scrambled by SI_RNTI"
  print "                 -dci11 : for DCI 1_1 scrambled by C_RNTI (UE DL data traffic)"
  print " -v<XXX>     : OPTIONAL parameter (defaulted to the current master track committed 3GPP Spec"
  print "               version."
  print "               This option specifies a user input 3GPP spec version for a DCI format"
  print "               e.g. 15.2 ==> -v152."

  print "               Supported 3GPP spec version: %s" % str(gAll3gppVersions)
  print " -dec/-hex <xxxx-xxxx-xxxx-xxxx>  "
  print "             : OPTIONAL parameter"
  print "               Either option can be used to specify an input dci coded value for decoding"
  print "               for -hex, user needs to specify the coded dci msg is hex values:"
  print "                 e.g. -hex ffff-abcd-1234-0000"
  print "               for -dec, user needs to specify the coded dci msg is decimal values:"
  print "                 e.g. -dec 65535-43981-4660-0000"
  print ""
  print "               -dec/-hex are mutually excluded, so only one can be used in the command line"
  print "                 at a time.  The format of the input dci msg value is strictly enforced"
  print "                 ie. with 4 separate U16 values separated by a '-',"
  print "                      <U16[0]>-<U16[1]>-<U16[2]>-<U16[3]>"
  print " -e          : OPTIONAL parameter.  Use this option to formulate a coded dci msg"
  print "               User will be prompted to input values for all bitfields in the specified"
  print "               dci format using the -dci<XX> option.  The final code dci msg will "
  print "               be displayed"
  print " -enum       : OPTIONAL parameter.  Display the DCI format enum value used in the"
  print "                 gNB s/w (e.g. dciFormatType field in the NR_PDCCH_IND signal) "
  print ""
  print " NOTE: if no optional parameter is specified, the script will show the schematic info "
  print "       of the specified DCI: field names, # of bits per field, # of fields"
  print "       total # of bits in the DCI etc."
  print "       This version of the script is currently default for 3GPP %s" % gDecoding3gppVersion
  print ""
  print " Version: %s" % nrDciVersion


#########################################################################################
def getUserInput(inputPrompt, highlight=True):
  ready2Return = False

  while (not ready2Return):
    if highlight:
      inputPrompt = "\033[32m" + inputPrompt + "\033[0m"
    try:
      userInput = raw_input(inputPrompt)
    except:
      return None

    result = userInput.strip()
    if len(result) > 0:
      ready2Return = True

  return result



#########################################################################################
def convertHexStrToInt(hexStr):
  try:
    return int(hexStr, 16)
  except:
    return None



#########################################################################################
def createBitmask(nofBits, shift):
  bm = 0
  i = 0
  while i < nofBits:
    bm |= 1 << i;
    i += 1
  bm = bm << shift
  return bm

#########################################################################################
def perror(str, quit=False):
  print '\033[31m' + "ERROR: %s" % str + '\033[0m'
  if quit == True:
    exitProg()

#########################################################################################
def signal_handler(sig, frame):
  print 'Exiting'
  exitProg()

#########################################################################################
def handleInput():
  global gDciFormat
  global gBandwidth
  global gDciMsg
  global gEncodeDci
  global gDecodeDci
  global g3gppSpecified
  global gDecoding3gppVersion
  global gNumerology

  gDciSchemativcOnly = True
  nrOfArg = len(sys.argv);
  idx = 1
  gEncodeDci = False
  gDecodeDci = False
  while idx < nrOfArg:
    if (sys.argv[idx] == '-e'):
      if (gDecodeDci == True):
        perror("Option -e is mutually excluded with [-hex|-dec] ", True);
      gEncodeDci = True
      idx += 1
    elif (sys.argv[idx] == '-h'):
      printUsage()
      exitProg() 
    elif (sys.argv[idx] == '-enum'):
      for dciFormat in NR_DCI_SCHEMATIC.keys():
        print("%s = %d"%(dciFormat, NR_DCI_SCHEMATIC[dciFormat][ENUM_VALUE]))
      exitProg() 
    elif (sys.argv[idx] == '-dci00'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_0_0
        idx += 1
    elif (sys.argv[idx] == '-dci11'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_1_1
        idx += 1
    elif (sys.argv[idx] == '-dci10'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_1_0
        idx += 1
    elif (sys.argv[idx] == '-dci10sib'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_1_0_SIB
        idx += 1
    elif (sys.argv[idx] == '-dci10ra'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_1_0_RA
        idx += 1
    elif (sys.argv[idx] == '-v152'):
      if g3gppSpecified == True:
        perror("Only one 3GPP version can be specified", True);
      else:
        gDecoding3gppVersion = DCI_SPEC_V15_2
        g3gppSpecified = True
        idx += 1
    elif (sys.argv[idx] == '-v153'):
      if g3gppSpecified == True:
        perror("Only one 3GPP version can be specified", True);
      else:
        gDecoding3gppVersion = DCI_SPEC_V15_3
        g3gppSpecified = True
        idx += 1
    elif (sys.argv[idx] == '-dci01'):
      if gDciFormat != NR_DCI_FORMAT_NULL:
        perror("Only one DCI format can be selected ", True);
      else:
        gDciFormat = NR_DCI_FORMAT_0_1
        idx += 1
    elif (sys.argv[idx] == '-hex'):
      if (gEncodeDci == True):
        perror("Option -hex is mutually excluded with -e", True);
      if (len(gDciMsg) > 0) or (gDecodeDci == True):
        perror("-hex/-dec options are mutually exclusive. Only use one of them to specify DCI value",
               True)
      if (idx+1) >= nrOfArg:
        perror("Invalid -hex option : Expecting -hex XXXX-XXXX-XXXX-XXXX", True)
      m = re.search(r'(\w+)-(\w+)-(\w+)-(\w+)$', sys.argv[idx+1])
      if (m == None):
        perror("Invalid -hex option : Expecting -hex XXXX-XXXX-XXXX-XXXX", True)

      # validate we have good dci hex input values
      dciInputs = (m.group(1), m.group(2), m.group(3), m.group(4))
      gDciMsg = [];
      for dci in dciInputs:
        dciValInDec = convertHexStrToInt(dci)
        if dciValInDec != None:
          if (dciValInDec > 0xffff):
            perror("Invalid Hex value [%s] : Expecting dci hex value <= 0xffff" % dci, True)
          else:
            gDciMsg.append(dciValInDec)
        else:
          perror("Invalid Hex value [%s]" % dci, True)

      gDecodeDci = True
      idx += 2
    elif (sys.argv[idx] == '-dec'):
      if (gEncodeDci == True):
        perror("Option -dec is mutually excluded with -e", True);
      if (len(gDciMsg) > 0) or (gDecodeDci == True):
        perror("-hex/-dec options are mutually exclusive. Only use one of them to specify DCI value",
               True)
      if (idx+1) >= nrOfArg:
        perror("Invalid -dec option : Expecting -dec num-num-num-num", True)
      m = re.search(r'(\d+)-(\d+)-(\d+)-(\d+)$', sys.argv[idx+1])
      if (m == None):
        perror("Invalid DCI decimal value : Expecting -dec num-num-num-num", True)

      # validate we have good dci hex input values
      dciInputs = (m.group(1), m.group(2), m.group(3), m.group(4))
      gDciMsg = [];
      for dci in dciInputs:
        dciValInDec = convertNumericStrToInt(dci)
        if dciValInDec != None:
          if (dciValInDec > 0xffff):
            perror("Invalid Dci value [%s] : Expecting dci value <= %d" % (dciValInDec, 0xffff),
                   True)
          else:
            gDciMsg.append(dciValInDec)
        else:
          perror("Invalid DCI Decimal value [%d]" % dci, True)

      gDecodeDci = True
      idx += 2
    elif (sys.argv[idx] == '-n'):
      if (idx+1) >= nrOfArg:
        perror("Missing Numerology value for -n option : Valid values %s " % str(NR_NUMEROLOGY), True)
      numerology = convertNumericStrToInt(sys.argv[idx+1])
      if (numerology not in NR_NUMEROLOGY):
        perror("Invalid Numerology value for -n option : Expecting %s" % str(NR_NUMEROLOGY), True)
      gNumerology = numerology;
      idx += 2
    elif (sys.argv[idx] == '-b'):
      if (idx+1) >= nrOfArg:
        perror("Invalid BW value for -b option : Expecting %s in MHz" % str(NR_BW), True)
      bw = convertNumericStrToInt(sys.argv[idx+1])
      if (bw not in NR_BW):
        perror("Invalid BW value for -b option : Expecting %s in MHz" % str(NR_BW), True)
      gBandwidth = bw;
      idx += 2
    else:
      printUsage("Invalid parameter [%s]" % sys.argv[idx])
      exitProg()

  if (gDciFormat == NR_DCI_FORMAT_NULL):
    perror("Must provide a dci format: -dci11|-dci10|-dci00|-dci10sib|-dci10ra|-dci01", True)

  if (gBandwidth == NR_BW_NULL):
    perror("option -b (bandwidth) is mandatory :", True)

  if (gNumerology == None):
    perror("option -n (numerology) is mandatory :", True)

  if (gBandwidth not in NR_ALLOC_TYPE0_RIV_BIT_SIZE[gNumerology].keys()):
    perror("BW and Numerology input not supported: BW=%s Numerology=%s" % (str(gBandwidth), str(gNumerology)), True)




#########################################################################################
def displayDciSchematic(dciFormat, specVer, bandwidth, allocType):
  global gDecodeDci
  global gEncodeDci

  displayValue = False
  dciSchematic = NR_DCI_SCHEMATIC[dciFormat][specVer]
  tmp = ''

  if (gDciBase3gppVersion != gDecoding3gppVersion):
    specVerStr = "%s (no change from %s)" % (gDecoding3gppVersion, gDciBase3gppVersion)
  else:
    specVerStr = "%s" % gDecoding3gppVersion
  print '3gpp version        : %s ' % specVerStr
  print 'DCI Format          : %s ' % dciFormat
  print 'DCI Format Enum Val : %s ' % str(NR_DCI_SCHEMATIC[dciFormat][ENUM_VALUE])
  print 'Bandwidth           : %sMHz' % str(bandwidth)
  print 'Numerology          : %s' % str(gNumerology)
  print 'Allocation Type     : %s ' % str(allocType)
  print 'No of Bitfields     : %s ' % str(dciSchematic[NOF_BIT_FIELDS])
  print 'No Of Bits          : %s ' % str(dciSchematic[TOTAL_DCI_NOF_BITS])
  if gDecodeDci == True:
    print 'Input DCI Hex value : %s [%04x-%04x-%04x-%04x]' %\
           (hex(dciSchematic[INPUT_DCI_VALUE]), gDciMsg[0], gDciMsg[1], gDciMsg[2], gDciMsg[3])
    tmp = 'decoded bitField Value'
  if gEncodeDci == True:
    resultVal = dciSchematic[OUTPUT_DCI_VALUE]
    dci0 = (resultVal & 0xffff000000000000) >> 48
    dci1 = (resultVal & 0xffff00000000) >> 32
    dci2 = (resultVal & 0xffff0000) >> 16
    dci3 = (resultVal & 0xffff)
    print 'Encoded DCI Hex val : %s [%04x-%04x-%04x-%04x] [%d-%d-%d-%d]' %\
           (hex(dciSchematic[OUTPUT_DCI_VALUE]), dci0, dci1, dci2, dci3,\
                                                dci0, dci1, dci2, dci3)
    tmp = 'user Input bitField Value'

  print ''
  print '*** DCI schematic *** '

  print '%-20s[#bits : bitmask] : %s  NOTE:#bits with <*> is variable size field' %\
        ('bitfield', tmp)
  print ''

  fieldSkipped = []
  for aField in dciSchematic[SCHEMATIC]:
    valueStr = ''
    if gDecodeDci == True:
      valueStr = '%s [%s]' % (str(dciSchematic[VALUE][aField]), hex(dciSchematic[VALUE][aField]))
    if gEncodeDci == True:
      valueStr = '%s [%s]' % (str(dciSchematic[USER_BF_VALUE][aField]),
                              hex(dciSchematic[USER_BF_VALUE][aField]))
    nofBits = dciSchematic[FIELD_SIZE][aField]
    bitmask = dciSchematic[BITMASK][aField]
    varField = ' '
    if aField in dciSchematic[VARIABLE_SIZE]:
      varField = '*'
    if nofBits > 0:
      print "%-20s[%2s%s : 0x%016x] : %s" %\
            (str(aField), str(nofBits), varField, bitmask, valueStr)
    else:
      fieldSkipped.append(aField)

  if len(fieldSkipped) > 0:
    print "\nSkipped dynamic-sized field due to size being 0: %s" % str(fieldSkipped)
  
#########################################################################################
def getVariableFieldSize(aField, allocType):
  size = 0
  if aField == NR_DCI_RIV:
    if allocType == NR_ALLOC_TYPE_0:
      size = NR_ALLOC_TYPE0_RIV_BIT_SIZE[gNumerology][gBandwidth]
    else:
      size = NR_ALLOC_TYPE1_RIV_BIT_SIZE[gNumerology][gBandwidth]
  else:
    if aField in NR_DCI_VAR_SIZE_FIELD_MIN_MAX.keys():
      fMin = NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MIN]
      fMax = NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MAX]
    else:
      perror("Field[%d] is variable in size but not defined with min/max" % aFiled, True)
    ## if not list here, ask user for the size of the field.
    print ''
    input = getUserInput('Pls Enter # of bits for this %s dynamic-sized field [%s] '\
                         '(valid values:%d-%d) :' %\
                         (gDciFormat, aField, fMin, fMax), True)
    print ''
    if input == None:
      perror("Invalid User Input", True)
    if aField in NR_DCI_VAR_SIZE_FIELD_MIN_MAX.keys():
      size = convertNumericStrToInt(input)
      if (size > NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MAX] or
          size < NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MIN]):
        perror("User Input Value out of range [%d..%d] for field [%s]" %\
               (NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MIN],\
                NR_DCI_VAR_SIZE_FIELD_MIN_MAX[aField][BITS_MAX],\
                aField),\
               True)
    else:
      perror("Variable size field min/max missing in code, default to 0", True)
      size = 0
  return size

#########################################################################################
def encodeDci():
  global gDciBase3gppVersion
  dciSchematic = NR_DCI_SCHEMATIC[gDciFormat][gDciBase3gppVersion]

  dciSchematic[USER_BF_VALUE] = {}
  resultVal = 0
  for aField in dciSchematic[SCHEMATIC]:
    if (aField == NR_DCI_HEADER):
      if gDciFormat in (NR_DCI_FORMAT_0_0, NR_DCI_FORMAT_0_1):
        dciSchematic[USER_BF_VALUE][aField] = UL_DCI_HEADER_VAL
      else:
        dciSchematic[USER_BF_VALUE][aField] = DL_DCI_HEADER_VAL
      print 'header field defalut set to value[%d]'%dciSchematic[USER_BF_VALUE][aField] 
    else:
      fieldSize = dciSchematic[FIELD_SIZE][aField]
      maxFieldVal = (1 << fieldSize) - 1

      tryAgain = True
      while tryAgain:
        inputStr = getUserInput('Enter bit %s field [%s] value (#bits=%d] : ' %\
                                (gDciFormat, aField, fieldSize),
                                True);
        if inputStr.isdigit():
          inValue = convertNumericStrToInt(inputStr)
          if inValue <= maxFieldVal:
            tryAgain = False
          else:
            perror("Input value[%d] larger than allowed max value[%d] "% (inValue, maxFieldVal), False)
        else:
          perror("Incorrect input. Only digits are allowed (no hex value)", False)

      dciSchematic[USER_BF_VALUE][aField] = inValue
    resultVal |= (dciSchematic[USER_BF_VALUE][aField] << dciSchematic[SHIFT][aField])
    #print '0x%016x' % (dciSchematic[USER_BF_VALUE][aField] << dciSchematic[SHIFT][aField])
    print 'Aggregated DCI with field [%s]: 0x%016x' % (aField, resultVal)
  dciSchematic[OUTPUT_DCI_VALUE] = resultVal
  print ''
  print ''

#########################################################################################
def decodeDci():
  global gDciBase3gppVersion
  dciSchematic = NR_DCI_SCHEMATIC[gDciFormat][gDciBase3gppVersion]

  dciIdx = 0
  bitPosInU16 = 0
  dciValue =  dciSchematic[INPUT_DCI_VALUE]
  dciSchematic[VALUE] = {}
  for aField in dciSchematic[SCHEMATIC]:
    bitMask = dciSchematic[BITMASK][aField]
    shift = dciSchematic[SHIFT][aField]
    value = (dciValue & bitMask) >> shift
    dciSchematic[VALUE][aField] = value
     
#########################################################################################
def getDci3gppVersion():
  global gDecoding3gppVersion
  global gDciFormat
  global gDciBase3gppVersion

  ver = gDecoding3gppVersion

  dciSchematicAllVersions = NR_DCI_SCHEMATIC[gDciFormat]

  ## check to see which 3gpp version to use..
  ## first to see if the "ver" is defined in the schematic for that DCI.
  ## if yes, use that version.
  ## if not, then step back to the previous version from the "gAll3gppVersions" and see
  ##  if that previous version is supported in the schematic.. continue until we found one.

  dciDefinedVersionList = dciSchematicAllVersions.keys()
  if ver not in dciDefinedVersionList:
    # the "requested" version is not defined, find the previous supported version.
    curVerIndex = gAll3gppVersions.index(ver)
    if curVerIndex == 0:
      perror("S/W error: dci=%s requested 3gpp=%s AllVersions=%s dciVesrion=%s" % (str(gDciFormat), str(gDecoding3gppVersion), str(gAll3gppVersions), str(dciDefinedVersionList)), True)
    else:
      while curVerIndex >= 0:
        ver = gAll3gppVersions[curVerIndex]
        if ver in dciDefinedVersionList:
          ## found next one, 
          break;
        else:
          curVerIndex -= 1

  return ver

#########################################################################################
def buildDciSchematic():
  global gDecodeDci
  global gDciBase3gppVersion

  nofBits = 0
  nofBitfields = 0


  gDciBase3gppVersion = getDci3gppVersion()
  dciSchematic = NR_DCI_SCHEMATIC[gDciFormat][gDciBase3gppVersion]

  if (len(gDciMsg) > 0):
    dciSchematic[INPUT_DCI_VALUE] = (gDciMsg[0] << 48) + (gDciMsg[1] << 32) +\
                                    (gDciMsg[2] << 16) + gDciMsg[3]

  allocType = dciSchematic[ALLOC_TYPE]
  for aField in dciSchematic[SCHEMATIC]:
    if (dciSchematic[FIELD_SIZE][aField] == NR_BIT_SIZE_VARIABLE):
      dciSchematic[FIELD_SIZE][aField] = getVariableFieldSize(aField, allocType)
      dciSchematic[VARIABLE_SIZE].append(aField)


    nofBits += dciSchematic[FIELD_SIZE][aField]
    bitShift = 64 - nofBits
    dciSchematic[BITMASK][aField] = createBitmask(dciSchematic[FIELD_SIZE][aField], bitShift)
    dciSchematic[SHIFT][aField] = bitShift;
    nofBitfields += 1

  dciSchematic[NOF_BIT_FIELDS] = nofBitfields
  dciSchematic[TOTAL_DCI_NOF_BITS] = nofBits
  if (gDecodeDci == True):
    decodeDci()

  if (gEncodeDci == True):
    encodeDci()

  displayDciSchematic(gDciFormat, gDciBase3gppVersion, gBandwidth, dciSchematic[ALLOC_TYPE])

#########################################################################################
def main():

  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)

  handleInput()
  buildDciSchematic()

  

#########################################################################################
if __name__ == '__main__':
  main()
