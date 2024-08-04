""" Bio-Logic OEM package data types.

This module provides a transcription of the EcLib DLL data types and constants.

As the names and values can be found in the Development Package documentation,
one should refer to the PDF for further explanations.

The main datatypes the module relies on are ctypes Structure, Enum and dataclass.

Note that the DLL has alignement requirements that can be achieved with
the _pack_ attribute in the Structures.

"""

from enum import Enum
from dataclasses import dataclass

from kbio.c_utils import *

#==============================================================================#

# Max number of slots
MAX_SLOT_NB = 16

# Array of channels
ChannelsArray = c_bool * MAX_SLOT_NB

# Array of results
ResultsArray = c_int32 * MAX_SLOT_NB

DataBuffer = c_uint32 * 1000

#==============================================================================#

@dataclass
class USB_device :

    index: int
    instrument: str
    serial: str

    def __str__ (self) :
        en_clair = f"{self.address} : {self.instrument} s/n {self.serial}"
        return en_clair

    @property
    def address (self) :
        address = f"USB{self.index}"
        return address

#==============================================================================#

@dataclass
class Ethernet_device :

    config: tuple
    instrument: str
    serial: str
    identifier: str
    name: str

    def __str__ (self) :
        en_clair = f"Ethernet{self.config} : {self.instrument}, s/n '{self.serial}'"
        if self.identifier :
            en_clair += f", id='{self.identifier}'"
        if self.name :
            en_clair += f", name='{self.name}'"
        return en_clair

#==============================================================================#

class DEVICE (Enum) :
    VMP     = 0
    VMP2    = 1
    MPG     = 2
    BISTAT  = 3
    MCS_200 = 4
    VMP3    = 5
    VSP     = 6
    HCP803  = 7
    EPP400  = 8
    EPP4000 = 9
    BISTAT2 = 10
    FCT150S = 11
    VMP300  = 12
    SP50    = 13
    SP150   = 14
    FCT50S  = 15
    SP300   = 16
    CLB500  = 17
    HCP1005 = 18
    CLB2000 = 19
    VSP300  = 20
    SP200   = 21
    MPG2    = 22
    SP100   = 23
    MOSLED  = 24
    KINEXXX = 25
    BCS815  = 26
    SP240   = 27
    MPG205  = 28
    MPG210  = 29
    MPG220  = 30
    MPG240  = 31
    BP300   = 32
    VMP3E   = 33
    VSP3E   = 34
    SP50E   = 35
    SP150E  = 36
    UNKNOWN = 255

    def __str__(self) -> str:
        return self.name

#------------------------------------------------------------------------------#

VMP3_FAMILY = (
    "VMP2",
    "VMP3",
    "BISTAT",
    "BISTAT2",
    "MCS_200",
    "VSP",
    "SP50",
    "SP150",
    "FCT50S",
    "FCT150S",
    "CLB500",
    "CLB2000",
    "HCP803",
    "HCP1005",
    "MPG2",
    "MPG205",
    "MPG210",
    "MPG220",
    "MPG240",
    "VMP3E",
    "VSP3E",
    "SP50E",
    "SP150E",
)

#------------------------------------------------------------------------------#

VMP300_FAMILY = (
    "SP100",
    "SP200",
    "SP300",
    "VSP300",
    "VMP300",
    "SP240",
    "BP300",
)

#------------------------------------------------------------------------------#

class DeviceInfo (POD) :
    _fields_ = [
        ("DeviceCode", c_int32),
        ("RAMSize", c_int32),
        ("CPU", c_int32),
        ("NumberOfChannels", c_int32),
        ("NumberOfSlots", c_int32),
        ("FirmwareVersion", c_int32),
        ("FirmwareDate_yyyy", c_int32),
        ("FirmwareDate_mm", c_int32),
        ("FirmwareDate_dd", c_int32),
        ("HTdisplayOn", c_int32),
        ("NbOfConnectedPC", c_int32)
    ]

DEVICE_INFO = POINTER(DeviceInfo)

#------------------------------------------------------------------------------#

class CHANNEL_BOARD (Enum) :
    C340_IF0       = 0
    C340_IF2_Z     = 1
    C340_OTHERS    = 2
    C340_IF2_NONZ  = 3
    C340_IF3_Z     = 4
    C340_IF3_NONZ  = 5
    C340_IF3_ZZ    = 6
    C340_IF3_NZZ   = 7
    C340_SP50      = 8
    C340_SP150Z    = 9
    C340_SP150NZ   = 10
    C437_Z         = 11
    C437_NZ        = 12
    C437_SP150Z    = 13
    C437_SP150NZ   = 14
    C437_MPG2      = 15
    C437_MPG2Z     = 16
    C437_MPGX      = 17
    C437_MPGXZ     = 18
    C437_VMP3EZ    = 19
    C437_VMP3ENZ   = 20

    def __str__(self) -> str:
        return self.name

class ChannelInfo (POD) :
    _fields_ = [
        ("Channel", c_int32),           # Channel (0..15)
        ("BoardVersion", c_int32),      # Board version
        ("BoardSerialNumber", c_int32), # Board serial number
        ("FirmwareCode" ,c_int32),      # Identifier of the firmware loaded on the channel
        ("FirmwareVersion", c_int32),   # Firmware version
        ("XilinxVersion", c_int32),     # Xilinx version
        ("AmpCode", c_int32),           # Amplifier code
        ("NbAmps", c_int32),            # Number of amplifiers (0..16)
        ("Lcboard", c_int32),           # Low current presence
        ("Zboard", c_int32),            # Impedance capabilities
        ("MUXboard", c_int32),          # MEA mux
        ("GPRAboard", c_int32),         # Analog ramp
        ("MemSize", c_int32),           # Memory size (in bytes)
        ("MemFilled", c_int32),         # Memory filled (in bytes)
        ("State", c_int32),             # Channel state : run/stop/pause
        ("MaxIRange", c_int32),         # Maximum I range allowed
        ("MinIRange", c_int32),         # Minimum I range allowed
        ("MaxBandwidth", c_int32),      # Maximum bandwidth allowed
        ("NbOfTechniques", c_int32),    # Number of techniques loaded
    ]

CH_INFO = POINTER(ChannelInfo)

#------------------------------------------------------------------------------#

class HardwareConf (POD) :
    _fields_ = [
        ("Connection", c_int32), # Electrode connection
        ("Mode", c_int32),       # Channel mode
    ]

HW_CONF = POINTER(HardwareConf)

class HW_CNX (Enum) :
    STANDARD     = 0 # Standard connection
    CE_TO_GND    = 1 # CE to ground connection
    WE_TO_GND    = 2 # WE to ground connection
    HIGH_VOLTAGE = 3 # 48V connection

class HW_MODE (Enum) :
    GROUNDED = 0 # Grounded mode
    FLOATING = 1 # Floating mode

#------------------------------------------------------------------------------#

class OPTION_ERROR (Enum) :
    NO_ERROR           =   0 # No error found
    OPT_CHANGE         =   1 # Number of options changed
    OPEN_IN            =   2 # Open-in signal was asserted
    IRCMP_OVR          =   3 # R Compensation overflow
    OPT_4A             = 100 # 4A amplifier unknown error
    OPT_4A_OVRTEMP     = 101 # 4A amplifier temperature overflow
    OPT_4A_BADPOW      = 102 # 4A amplifier bad power
    OPT_4A_POWFAIL     = 103 # 4A amplifier power fail
    OPT_48V            = 200 # 48V amplifier unknown error
    OPT_48V_OVRTEMP    = 201 # 48V amplifier temperature overflow
    OPT_48V_BADPOW     = 202 # 48V amplifier bad power
    OPT_48V_POWFAIL    = 203 # 48V amplifier power fail
    OPT_10A5V_ERR      = 300 # 10A 5V amplifier error
    OPT_10A5V_OVRTEMP  = 301 # 10A 5V amplifier overheat
    OPT_10A5V_BADPOW   = 302 # 10A 5V amplifier bad power
    OPT_10A5V_POWFAIL  = 303 # 10A 5V amplifier power fail

#-----------------------------------------------------------------------------#

class FIRMWARE (Enum) :
    NONE        = 0
    INTERPR     = 1
    UNKNOWN     = 4
    KERNEL      = 5
    INVALID     = 8
    ECAL        = 10
    ECAL4       = 11

    def __str__(self) -> str:
        return self.name

#------------------------------------------------------------------------------#

class CurrentValues (POD) :
    _fields_ = [
        ("State", c_int32),
        ("MemFilled", c_int32),
        ("TimeBase", c_float),
        ("Ewe", c_float),
        ("EweRangeMin", c_float),
        ("EweRangeMax", c_float),
        ("Ece", c_float),
        ("EceRangeMin", c_float),
        ("EceRangeMax", c_float),
        ("Eoverflow", c_int32),
        ("I", c_float),
        ("IRange", c_int32),
        ("Ioverflow", c_int32),
        ("ElapsedTime", c_float),
        ("Freq", c_float),
        ("Rcomp", c_float),
        ("Saturation", c_int32),
        ("OptErr", c_int32),
        ("OptPos", c_int32)
    ]

CURRENT_VALUES = POINTER(CurrentValues)

#------------------------------------------------------------------------------#

class DataInfo (POD) :
    _pack_ = 4
    _fields_ = [
        ("IRQskipped", c_int32),
        ("NbRows", c_int32),
        ("NbCols", c_int32),
        ("TechniqueIndex", c_int32),
        ("TechniqueID", c_int32),
        ("ProcessIndex", c_int32),
        ("loop", c_int32),
        ("StartTime", c_double),
        ("MuxPad", c_int32)
    ]

DATA_INFO = POINTER(DataInfo)

#------------------------------------------------------------------------------#

class PARAM_TYPE (Enum) :
    PARAM_INT     = 0
    PARAM_BOOLEAN = 1
    PARAM_SINGLE  = 2

#------------------------------------------------------------------------------#

class EccParam (POD) :
    _fields_ = [
        ("ParamStr", 64 * c_byte),
        ("ParamType", c_int32),
        ("ParamVal", c_uint32),
        ("ParamIndex", c_int32),
    ]

ECC_PARM = POINTER(EccParam)

#------------------------------------------------------------------------------#

class EccParams (POD) :
    _pack_ = 4
    _fields_ = [
        ("len", c_int32),
        ("pParams", ECC_PARM),
    ]

ECC_PARMS = POINTER(EccParams)

def ECC_PARM_ARRAY (nb) :
    array_type = nb * EccParam
    return array_type()

#------------------------------------------------------------------------------#

class TechniqueInfos (POD) :
    _fields_ = [
        ("Id", c_int32),
        ("indx", c_int32),
        ("nbParams", c_int32),
        ("nbSettings", c_int32),
        ("Params", ECC_PARM),
        ("HardSettings", ECC_PARM),
    ]

TECHNIQUE_INFOS = POINTER(TechniqueInfos)

#------------------------------------------------------------------------------#

class PROG_STATE (Enum) :
    STOP         = 0 # Channel is stopped
    RUN          = 1 # Channel is running
    PAUSE        = 2 # Channel is paused
    SYNC         = 3 # grouped channels synchronization (stack)

    def __str__(self) -> str:
        return self.name

#------------------------------------------------------------------------------#

class I_RANGE (Enum) :
    I_RANGE_KEEP    = -1 # Keep previous
    I_RANGE_100pA   = 0  # 100 pA
    I_RANGE_1nA     = 1  # 1 nA VMP3
    I_RANGE_10nA    = 2  # 10 nA VMP3
    I_RANGE_100nA   = 3  # 100 nA VMP3
    I_RANGE_1uA     = 4  # 1 μA VMP3
    I_RANGE_10uA    = 5  # 10 μA VMP3
    I_RANGE_100uA   = 6  # 100 μA VMP3
    I_RANGE_1mA     = 7  # 1 mA VMP3
    I_RANGE_10mA    = 8  # 10 mA VMP3
    I_RANGE_100mA   = 9  # 100 mA VMP3
    I_RANGE_1A      = 10 # 1 A VMP3
    I_RANGE_BOOSTER = 11 # Booster VMP3
    I_RANGE_AUTO    = 12 # Auto range VMP3

    def __str__(self) -> str:
        return self.name

    ## Partial Ordering
    ## Comparing elements that can't be compared results in None

    @staticmethod
    def _make_comparison(cmp):
        def compare(self, other):
            _no_compare = (self.I_RANGE_KEEP, self.I_RANGE_BOOSTER, self.I_RANGE_AUTO)
            if not isinstance(other, I_RANGE):
                return NotImplemented
            if self in _no_compare or other in _no_compare:
                return None  # partial ordering
            return cmp(self.value, other.value)
        return compare

    __lt__ = _make_comparison(lambda a, b: a < b)
    __le__ = _make_comparison(lambda a, b: a <= b)
    __gt__ = _make_comparison(lambda a, b: a > b)
    __ge__ = _make_comparison(lambda a, b: a >= b)


#------------------------------------------------------------------------------#

class E_RANGE (Enum) :
    E_RANGE_2_5V = 0  # ±2.5V
    E_RANGE_5V   = 1  # ±5V
    E_RANGE_10V  = 2  # ±10V
    E_RANGE_AUTO = 3  # auto

    def __str__(self) -> str:
        return self.name

    ## Partial Ordering
    ## Comparing elements that can't be compared results in None

    @staticmethod
    def _make_comparison(cmp):
        def compare(self, other):
            if not isinstance(other, I_RANGE):
                return NotImplemented
            if E_RANGE.E_RANGE_AUTO in (self, other):
                return None  # partial ordering
            return cmp(self.value, other.value)
        return compare

    __lt__ = _make_comparison(lambda a, b: a < b)
    __le__ = _make_comparison(lambda a, b: a <= b)
    __gt__ = _make_comparison(lambda a, b: a > b)
    __ge__ = _make_comparison(lambda a, b: a >= b)

#------------------------------------------------------------------------------#

class BANDWIDTH (Enum) :
    BW_1 = 1
    BW_2 = 2
    BW_3 = 3
    BW_4 = 4
    BW_5 = 5
    BW_6 = 6
    BW_7 = 7
    BW_8 = 8
    BW_9 = 9
    BW_KEEP = -1

    def __str__(self) -> str:
        return self.name

    ## Partial Ordering
    ## Comparing elements that can't be compared results in None

    @staticmethod
    def _make_comparison(cmp):
        def compare(self, other):
            if not isinstance(other, BANDWIDTH):
                return NotImplemented
            if BANDWIDTH.BW_KEEP in (self, other):
                return None  # partial ordering
            return cmp(self.value, other.value)
        return compare

    __lt__ = _make_comparison(lambda a, b: a < b)
    __le__ = _make_comparison(lambda a, b: a <= b)
    __gt__ = _make_comparison(lambda a, b: a > b)
    __ge__ = _make_comparison(lambda a, b: a >= b)

#------------------------------------------------------------------------------#

class GAIN (Enum) :
    GAIN_1    = 0
    GAIN_10   = 1
    GAIN_100  = 2
    GAIN_1000 = 3

#------------------------------------------------------------------------------#

class FILTER (Enum) :
    FILTER_NONE  = 0
    FILTER_50KHZ = 1
    FILTER_1KHZ  = 2
    FILTER_5HZ   = 3

#------------------------------------------------------------------------------#

class AMPLIFIER (Enum) :
    AMPL_NONE             = 0   # No Amplifier
    AMPL_2A               = 1   # Amplifier 2 A
    AMPL_1A               = 2   # Amplifier 1 A
    AMPL_5A               = 3   # Amplifier 5 A
    AMPL_10A              = 4   # Amplifier 10 A
    AMPL_20A              = 5   # Amplifier 20 A
    AMPL_HEUS             = 6   # reserved
    AMPL_LC               = 7   # Low current amplifier
    AMPL_80A              = 8   # Amplifier 80 A
    AMPL_4AI              = 9   # Amplifier 4 A
    AMPL_PAC              = 10  # Fuel Cell Tester
    AMPL_4AI_VSP          = 11  # Amplifier 4 A (VSP instrument)
    AMPL_LC_VSP           = 12  # Low current amplifier (VSPinstrument)
    AMPL_UNDEF            = 13  # Undefined amplifier
    AMPL_MUIC             = 14  # reserved
    AMPL_ERROR            = 15  # No amplifier (error case)
    AMPL_8AI              = 16  # Amplifier 8 A
    AMPL_LB500            = 17  # Amplifier LB500
    AMPL_100A5V           = 18  # Amplifier 100 A
    AMPL_LB2000           = 19  # Amplifier LB2000
    AMPL_1A48V            = 20  # Amplifier 1A 48V
    AMPL_4A14V            = 21  # Amplifier 4A 14V
    AMPL_5A_MPG2B         = 22  # Amplifier 5A
    AMPL_10A_MPG2B        = 23  # Amplifier 10A
    AMPL_20A_MPG2B        = 24  # Amplifier 20A
    AMPL_40A_MPG2B        = 25  # Amplifier 40A
    AMPL_COIN_CELL_HOLDER = 26  # Coin cell holder amplifier
    AMPL4_10A5V           = 27  # Amplifier 10A 5V
    AMPL4_2A30V           = 28  # Amplifier 2A 30V
    AMPL4_30A50V          = 77  # 30A/50V amplifier
    AMPL3_50A60V          = 93  # 50A/60V amplifier (FlexP 0160)
    AMPL3_200A12V         = 97  # 200A/12V amplifier (FlexP 0012)
    AMPL3_50A60VII        = 101 # 50A/60V amplifier (FlexP 0060)
    AMPL4_1A48VPII        = 105 # 1A/48VP v2
    AMPL4_1A48VPIII       = 129 # 1A/48VP v3

    def __str__(self) -> str:
        return self.name

#------------------------------------------------------------------------------#

class ERROR (Enum) :
    NOERROR                   =    0  # "No error"
    GEN_NOTCONNECTED          =   -1  # "No instrument connected"
    GEN_CONNECTIONINPROGRESS  =   -2  # "Connection in progress"
    GEN_CHANNELNOTPLUGGED     =   -3  # "Selected channel(s) unplugged"
    GEN_INVALIDPARAMETERS     =   -4  # "Invalid function parameters"
    GEN_FILENOTEXISTS         =   -5  # "Selected file does not exist"
    GEN_FUNCTIONFAILED        =   -6  # "Function failed"
    GEN_NOCHANNELSELECTED     =   -7  # "No channel selected"
    GEN_INVALIDCONF           =   -8  # "Invalid instrument configuration"
    GEN_ECLAB_LOADED          =   -9  # "EC-Lab firmware loaded on the instrument"
    GEN_LIBNOTCORRECTLYLOADED =  -10  # "Library not correctly loaded in memory"
    GEN_USBLIBRARYERROR       =  -11  # "USB library not correctly loaded in memory"
    GEN_FUNCTIONINPROGRESS    =  -12  # "Function already in progress"
    GEN_CHANNEL_RUNNING       =  -13  # "Selected channel(s) already used"
    GEN_DEVICE_NOTALLOWED     =  -14  # "Device not allowed"
    GEN_UPDATEPARAMETERS      =  -15  # "Invalid update function parameters"
    INSTR_VMEERROR            = -101  # "Internal instrument communication failed"
    INSTR_TOOMANYDATA         = -102  # "Too many data to transfer from the instrument (device error)"
    INSTR_RESPNOTPOSSIBLE     = -103  # "Selected channel(s) unplugged (device error)"
    INSTR_RESPERROR           = -104  # "Instrument response error"
    INSTR_MSGSIZEERROR        = -105  # "Invalid message size"
    COMM_COMMFAILED           = -200  # "Communication failed with the instrument"
    COMM_CONNECTIONFAILED     = -201  # "Cannot establish connection with the instrument"
    COMM_WAITINGACK           = -202  # "Waiting for the instrument response"
    COMM_INVALIDIPADDRESS     = -203  # "Invalid IP address"
    COMM_ALLOCMEMFAILED       = -204  # "Cannot allocate memory in the instrument"
    COMM_LOADFIRMWAREFAILED   = -205  # "Cannot load firmware into selected channel(s)"
    COMM_INCOMPATIBLESERVER   = -206  # "Communication firmware not compatible"
    COMM_MAXCONNREACHED       = -207  # "Maximum number of allowed connections reached"
    FIRM_FIRMFILENOTEXISTS    = -300  # "Cannot find kernel.bin file"
    FIRM_FIRMFILEACCESSFAILED = -301  # "Cannot read kernel.bin file"
    FIRM_FIRMINVALIDFILE      = -302  # "Invalid kernel.bin file"
    FIRM_FIRMLOADINGFAILED    = -303  # "Cannot load kernel.bin on the selected channel(s)"
    FIRM_XILFILENOTEXISTS     = -304  # "Cannot find FPGA file"
    FIRM_XILFILEACCESSFAILED  = -305  # "Cannot read FPGA file"
    FIRM_XILINVALIDFILE       = -306  # "Invalid FPGA file"
    FIRM_XILLOADINGFAILED     = -307  # "Cannot load FPGA file on the selected channel(s)"
    FIRM_FIRMWARENOTLOADED    = -308  # "No firmware loaded on the selected channel(s)"
    FIRM_FIRMWAREINCOMPATIBLE = -309  # "Loaded firmware not compatible with the library"
    TECH_ECCFILENOTEXISTS     = -400  # "Cannot find the selected ECC file"
    TECH_INCOMPATIBLEECC      = -401  # "ECC file not compatible with the channel firmware"
    TECH_ECCFILECORRUPTED     = -402  # "ECC file corrupted"
    TECH_LOADTECHNIQUEFAILED  = -403  # "Cannot load the ECC file"
    TECH_DATACORRUPTED        = -404  # "Data returned by the instrument are corrupted"
    TECH_MEMFULL              = -405  # "Cannot load techniques: full memory"
    OPT_CHANGE                =   1   # "Number of options changed"
    OPT_OPEN_IN               =   2   # "Open-in signal was asserted"
    OPT_4A_ERROR              = 100   # 4A10V amplifier error
    OPT_4A_OVERTEMP           = 101   # 4A10V amplifier overload temperature
    OPT_4A_BADPOWER           = 102   # 4A10V amplifier invalid power
    OPT_4A_POWERFAIL          = 103   # 4A10V amplifier power fail
    OPT_48V_ERROR             = 200   # 1A48V amplifier error
    OPT_48V_OVERTEMP          = 201   # 1A48V amplifier overload temperature
    OPT_48V_BADPOWER          = 202   # 1A48V amplifier invalid power
    OPT_48V_POWERFAIL         = 203   # 1A48V amplifier power fail
    OPT_10A5V_ERROR           = 300   # 10A5V amplifier error
    OPT_10A5V_OVERTEMP        = 301   # 10A5V amplifier overload temperature
    OPT_10A5V_BADPOWER        = 302   # 10A5V amplifier invalid power
    OPT_10A5V_POWERFAIL       = 303   # 10A5V amplifier power fail
    OPT_1A48VP_ERROR          = 600   # 1A48VP amplifier error
    OPT_1A48VP_OVERTEMP       = 601   # 1A48VP amplifier overheat
    OPT_1A48VP_BADPOWER       = 602   # 1A48VP amplifier bad power
    OPT_1A48VP_POWERFAIL      = 603   # 1A48VP amplifier power fail

#==============================================================================#

class FIND_ERROR (Enum) :
    NO_ERROR           =   0 # "No error"
    UNKNOWN_ERROR      =  -1 # unknown error
    INVALID_PARAMETER  =  -2 # invalid function parameters
    ACK_TIMEOUT        = -10 # instrument response timeout
    EXP_RUNNING        = -11 # experiment is running on instrument
    CMD_FAILED         = -12 # instrument do not execute command
    FIND_FAILED        = -20 # find failed
    SOCKET_WRITE       = -21 # cannot write the request of the descriptions of Ethernet instruments
    SOCKET_READ        = -22 # cannot read descriptions of Ethernet instrument
    CFG_MODIFY_FAILED  = -30 # set TCP/IP parameters failed
    READ_PARAM_FAILED  = -31 # deserialization of TCP/IP parameters failed
    EMPTY_PARAM        = -32 # not any TCP/IP parameters in serialization
    IP_FORMAT          = -33 # invalid format of IP address
    NM_FORMAT          = -34 # invalid format of netmask address
    GW_FORMAT          = -35 # invalid format of gateway address
    IP_NOT_FOUND       = -38 # instrument to modify not found
    IP_ALREADYEXIST    = -39 # new IP address in TCP/IP parameters

#==============================================================================#
