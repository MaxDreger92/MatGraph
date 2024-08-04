""" Bio-Logic OEM package python API.

This module provides a pure Python interface to the EcLib DLL used to control Bio-Logic potentiostats.

As the methods of this API closely follow the DLL parameters, no docstring is provided,
as one can refer to the Development Package PDF for documentation.

The aim of this API is to shield this module's clients from the ctypes intricacies,
leaving the user to use either plain types or types coming from this module, or the kbio_types module.

The only consistent conventions in this API are :
  * id_ is the connection identifier returned by a Connect call,
  * ch is a 1 based channel identifier (vs a 0 based value in the DLL)
  * strings on the client side are encoded in this API, as the DLL uses bytes.

Most of the functions raise an exception on error (a BioLogicError exception type),
which encapsulates the error code.

This behaviour can be overriden in the BL_xxx functions with an abort flag set to False.

"""

from __future__ import annotations

import logging
from array import array

from kbio import ECLIB_PATH, BLFIND_PATH
import kbio.types as KBIO

from kbio.c_utils import *
from kbio.utils import pp_plural, warn_diff

#==============================================================================#

_log = logging.getLogger(__name__)

class KBIOError(Exception):
    """ BioLogicError is an Exception used to capture an EClib API error."""

    def __init__ (self, context: KBIO_api.Error) :
        """Encapsulate context (an Error object)."""
        self.context = context

    def __str__ (self) :
        return str(self.context)

    def is_error (self, error: KBIO.ERROR) :
        """Check whether the error code is the same as our error code."""
        is_error = self.context.is_error(error)
        return is_error

#==============================================================================#

class KBIO_api :

    def GetLibVersion (self) :
        version = c_buffer(32)
        self.BL_GetLibVersion(*version.parm)
        return version.to_ascii()

    def Connect (self, server, timeout=5) :
        id_ = c_int32()
        info = self.DeviceInfo()
        self.BL_Connect(server.encode(), timeout, id_, info)
        # info is only provided by this call, so it must be kept by caller for further use.
        return id_.value, info

    def USB_DeviceInfo (self, index) :

        company = c_buffer(128)
        device = c_buffer(128)
        serial_number = c_buffer(128)

        ok = self.BL_GetUSBdeviceinfos(index, *company.parm , *device.parm, *serial_number.parm)

        if not ok :
          raise RuntimeError(f"no information available for USB{index}")

        # fields must be cleaned of their NULL ending character
        return {
            'company' : company.to_ascii(),
            'device'  : device.to_ascii(),
            'serial_number' : serial_number.to_ascii(),
        }

    def TestConnection (self,id_) :
        try:
            error = self.BL_TestConnection(id_)
        except KBIOError as err:
            if err.is_error(KBIO.ERROR.GEN_NOTCONNECTED):
                return False
            raise
        return error.code == 0

    def TestComSpeed (self,id_,ch) :
        rcvt_speed = c_int32()
        firmware_speed = c_int32()
        self.BL_TestCommSpeed(id_, ch-1, rcvt_speed, firmware_speed)
        return rcvt_speed.value, firmware_speed.value

    def Disconnect (self,id_) :
        self.BL_Disconnect(id_)

    def PluggedChannels (self,id_) :
        ch_map = KBIO.ChannelsArray()
        self.BL_GetChannelsPlugged(id_, ch_map, len(ch_map))
        channels = (ch+1 for ch,present in enumerate(ch_map) if present)
        return channels

    def IsChannelPlugged (self,id_,ch) :
        ch_map = KBIO.ChannelsArray()
        self.BL_GetChannelsPlugged(id_, ch_map, len(ch_map))
        return ch_map[ch-1]

    @staticmethod
    def channel_map (channel_set) :
        """Build a boolean array of channel presence in the channel_set (an iterable)."""
        channel_map = [False] * max(channel_set)
        for ch in channel_set :
            channel_map[ch-1] = True
        return channel_map

    def GetChannelInfo (self,id_,ch) :
        info = self.ChannelInfo()
        try :
            error = self.BL_GetChannelInfos(id_, ch-1, info)
        except KBIOError as e :
            # if firmware is not loaded, part of info is still valid
            # .. so it is not considered an error
            if not e.is_error(KBIO.ERROR.FIRM_FIRMWARENOTLOADED) :
                _log.warning(f"channel info error : {e}")
        return info

    def LoadFirmware (self, id_, channels, firmware, fpga, silent=False, force=True) :

        results = KBIO.ResultsArray()
        ch_map = KBIO.ChannelsArray(*channels)

        self.BL_LoadFirmware(
            id_,
            ch_map,
            results,
            len(results),
            not silent,  # display progress bar
            force,
            firmware.encode() if firmware else None,
            fpga.encode() if fpga else None
        )

        # sift through results and print message in case of error
        for ch,r in enumerate(results) :
            error = self.Error(r)
            error.check(f"LoadFirwmare on {ch+1}", abort=False)

    def GetHardwareConf (self, id_, ch) :
        conf = self.HardwareConf()
        self.BL_GetHardConf(id_, ch-1, conf)
        return conf

    def SetHardwareConf (self, id_, ch, cnx, mode) :
        hw_conf = self.HardwareConf(cnx, mode)
        self.BL_SetHardConf(id_, ch-1, hw_conf)

    def OptionError (self, id_, ch) :
        code = c_int32()
        pos  = c_int32()
        self.BL_GetOptErr(id_,ch-1,code,pos)
        return code.value, pos.value

    def GetMessage (self, id_, ch) :
        message = c_buffer(4096)
        self.BL_GetMessage(id_, ch-1, *message.parm)
        return message.to_ascii()

    def GetErrorMsg (self, code) :
        message = c_buffer(256)
        error = self.BL_GetErrorMsg(code, *message.parm)
        return message.to_ascii()

    def DefineParameter (self, label, value, index, parm) :
        function = {
            int:   self.BL_DefineIntParameter,
            float: self.BL_DefineSglParameter,
            bool:  self.BL_DefineBoolParameter,
        } [type(value)]
        function(label.encode(), value, index, parm)

    def DefineBoolParameter (self, label, value, index, parm) :
        self.BL_DefineBoolParameter(label.encode(), value, index, parm)

    def DefineSglParameter (self, label, value, index, parm) :
        self.BL_DefineSglParameter(label.encode(), value, index, parm)

    def DefineIntParameter (self, label, value, index, parm) :
        self.BL_DefineIntParameter(label.encode(), value, index, parm)

    def UpdateParameters (self, id_, ch, index, parms, file) :
        self.BL_UpdateParameters(id_, ch-1, index, parms, file.encode())

    def GetTechniqueInfos (self, id_, ch, ix, info) :
        self.BL_GetTechniqueInfos(id_, ch-1, ix, info)

    def GetParamInfos (self, id_, ch, ix, info) :
        self.BL_GetParamInfos(id_, ch-1, ix, info)

    def LoadTechnique (self, id_, ch, file, parms, first=True, last=True, display=False) :
        self.BL_LoadTechnique(id_, ch-1, file.encode(), parms, first, last, display)

    def StartChannel (self, id_, ch) :
        self.BL_StartChannel(id_, ch-1)

    def StopChannel (self, id_, ch) :
        self.BL_StopChannel(id_, ch-1)

    def StartChannels (self, id_, channels) :

        results = KBIO.ResultsArray()
        ch_map = KBIO.ChannelsArray(*channels)
        self.BL_StartChannels(id_, ch_map, results, len(results))

        ok = True
        nb = max(channels)

        # decode the results array and print errors, if any
        for ch,r in enumerate(results) :
            if ch >= nb :
                break
            if r != 0 :
                ok = False
            error = self.Error(r)
            error.check(f"StartChannels on {ch+1}", abort=False)

        # return whether an error occured
        return ok

    def StopChannels (self, id_, channels) :

        results = KBIO.ResultsArray()
        ch_map = KBIO.ChannelsArray(*channels)
        self.BL_StopChannels(id_, ch_map, results, len(results))

        ok = True
        nb = max(channels)

        # decode the results array and print errors, if any
        for ch,r in enumerate(results) :
            if ch >= nb :
                break
            if r != 0 :
                ok = False
            error = self.Error(r)
            error.check("StopChannels on {ch+1}", abort=False)

        # return whether an error occured
        return ok

    def GetCurrentValues (self, id_, ch) :
        cv = KBIO.CurrentValues()
        self.BL_GetCurrentValues(id_, ch-1, cv)
        return cv

    def GetData (self, id_, ch) :

        pb = KBIO.DataBuffer()
        di = KBIO.DataInfo()
        cv = KBIO.CurrentValues()
        self.BL_GetData(id_, ch-1, pb, di, cv)

        rows = di.NbRows
        cols = di.NbCols
        size = rows*cols
        db = array('L', pb[:size])

        # return CurrentValues, DataInfo, Data Records
        return cv, di, db

    def ConvertNumericIntoSingle (self, vi) :
        """Convert the vi word (32b) into a float."""
        vf = c_float()
        self.BL_ConvertNumericIntoSingle(vi, vf)
        return vf.value

#==============================================================================#

    def FindEChemDev (self) :
        serialized = utf16_buffer(8192)
        nb_devices = c_uint32()
        self.BL_FindEChemDev(*serialized.parm, nb_devices)
        devices = self._parse_device_serialization(nb_devices.value, serialized.decode())
        return devices


    def FindEChemEthDev (self) :
        serialized = utf16_buffer(4096)
        nb_devices = c_uint32()
        self.BL_FindEChemEthDev(*serialized.parm, nb_devices)
        devices = self._parse_device_serialization(nb_devices.value, serialized.decode())
        return devices


    def FindEChemUsbDev (self) :
        serialized = utf16_buffer(4096)
        nb_devices = c_uint32()
        self.BL_FindEChemUsbDev(*serialized.parm, nb_devices)
        devices = self._parse_device_serialization(nb_devices.value, serialized.decode())
        return devices

    def SetEthernetConfig (self, target_ip, new_ip=None, netmask=None, gateway=None) :
        new_config = ""
        if new_ip :
            new_config += f"IP%{new_ip}$"
        if netmask :
            new_config += f"NM%{netmask}$"
        if gateway :
            new_config += f"GW%{gateway}$"
        self.BL_SetConfig(target_ip, new_config)

    #--------------------------------------------------------------------------#

    @classmethod
    def _parse_device_serialization (cls, nb_devices, serialized) :

        """Analyze a serialized instrument bundle and turn into a list of devices."""

        devices = list()

        if not serialized :
            return devices

        # check instrument separator is correct

        sep = '%'
        last = serialized[-1]
        separators = (last,sep)

        if not warn_diff("serialization does not end with separator", separators) :
            serialized = serialized[:-1]

        instruments = serialized.split(sep)

        for instrument in instruments :

            # separate instrument info into fragments
            all_frags = instrument.split('$')
            mode = all_frags[0]
            # remove blank fields as not meaningful
            fragments = [ f for f in all_frags if f ]

            if mode == 'USB' :

                try :
                    # decode fragments into their repective fields
                    index, kind, serial = fragments[1:]
                    index = int(index)
                except :
                    raise RuntimeError(f"malformed USB serialization ({fragments})")

                # make fields into an USB_device object
                device = KBIO.USB_device(index,kind,serial)

            elif mode == 'Ethernet' :

                try :
                    # decode fragments into their repective fields :
                    # config = ip_address, gateway, netmask, mac_address
                    *config, identifier, instrument, serial, name = fragments[1:]
                except :
                    raise RuntimeError(f"malformed Ethernet serialization ({fragments})")

                # make fields into an Ethernet_device object
                device = KBIO.Ethernet_device(config, instrument, serial, identifier, name)

            else :

                raise RuntimeError(f"serialization not understood ({serialized})")

            devices.append(device)

        # check consistency of number of decoded instruments
        nbs = (nb_devices, len(devices))
        warn_diff(f"unexpected nb of devices", nbs)

        return devices

    #--------------------------------------------------------------------------#

    class DeviceInfo (KBIO.DeviceInfo) :

        """DeviceInfo adds a few helper methods over the KBIO plain old data equivalent"""

        @property
        def model (self) :
            device = KBIO.DEVICE(self.DeviceCode)
            return device.name

        def __str__ (self) :

            fragments = list()

            channels = self.NumberOfChannels
            slots = self.NumberOfSlots

            fragments.append(
                f"{self.model} {self.RAMSize}MB, CPU={self.CPU}"
                f", {pp_plural(channels,'channel')}"
                f", {pp_plural(slots,'slot')}"
            )
            fragments.append(
                f"Firmware: v{self.FirmwareVersion/100:.2f} "
                f"{self.FirmwareDate_yyyy}/{self.FirmwareDate_mm}/{self.FirmwareDate_dd}"
            )

            cnx = self.NbOfConnectedPC
            fragments.append(
                f"{pp_plural(cnx,'connection')}"
                f", HTdisplay {'on' if self.HTdisplayOn else 'off'}")

            en_clair = '\n'.join(fragments)
            return en_clair

    #--------------------------------------------------------------------------#

    class ChannelInfo (KBIO.ChannelInfo) :

        """ChannelInfo adds a few helper methods over the KBIO plain old data equivalent"""

        @property
        def firmware (self) :
            firmware = KBIO.FIRMWARE(self.FirmwareCode)
            return firmware.name

        @property
        def has_no_firmware (self) :
            firmware = KBIO.FIRMWARE(self.FirmwareCode)
            has_no_firmware = (firmware.value == 0)
            return has_no_firmware

        @property
        def is_kernel_loaded (self) :
            firmware = KBIO.FIRMWARE(self.FirmwareCode)
            return (firmware.name == "KERNEL")

        @property
        def board (self) :
            board = KBIO.CHANNEL_BOARD(self.BoardVersion)
            return board.name

        @property
        def state (self) :
            state = KBIO.PROG_STATE(self.State)
            return state.name

        @property
        def amplifier (self) :
            amplifier = KBIO.AMPLIFIER(self.AmpCode)
            return amplifier.name

        @property
        def min_IRange (self) :
            min_IRange = KBIO.I_RANGE(self.MinIRange)
            return min_IRange.name

        @property
        def max_IRange (self) :
            max_IRange = KBIO.I_RANGE(self.MaxIRange)
            return max_IRange.name

        def __str__ (self) :

            fragments = list()

            if self.has_no_firmware :

                fragments.append(f"{self.board} board, no firmware")

            elif self.is_kernel_loaded :

                fragments.append(f"Channel: {self.Channel+1}")
                fragments.append(f"{self.board} board, S/N {self.BoardSerialNumber}")
                fragments.append(f"{'has a'if self.Lcboard else 'no'} LC head")
                fragments.append(f"{'with' if self.Zboard else 'no'} EIS capabilities")
                fragments.append(pp_plural(self.NbOfTechniques,"technique"))
                fragments.append(f"State: {self.state}")

                if self.NbAmps :
                    fragments.append(f"{self.amplifier} amplifier (x{self.NbAmps})")
                else :
                    fragments.append(f"no amplifiers")

                fragments.append(f"IRange: [{self.min_IRange}, {self.max_IRange}]")
                fragments.append(f"MaxBandwidth: {self.MaxBandwidth}")

                memsize = self.MemSize
                if memsize :
                    fragments.append(
                        f"Memory: {self.MemSize/1024:.1f}KB"
                        f" ({(self.MemFilled/self.MemSize*100.):.2f}% filled)"
                    )
                else :
                    fragments.append("Memory: 0KB")

                version = self.FirmwareVersion/1000
                vstr = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"

                fragments.append(
                    f"{self.firmware} (v{vstr}), "
                    f"FPGA ({self.XilinxVersion:04X})"
                )

            else :

                version = self.FirmwareVersion/100
                vstr = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"
                fragments.append(
                    f"{self.firmware} (v{vstr}), "
                    f"FPGA ({self.XilinxVersion:04X})"
                )

            en_clair = '\n'.join(fragments)
            return en_clair

    #--------------------------------------------------------------------------#

    class HardwareConf (KBIO.HardwareConf) :

        """HardwareConf adds a few helper methods over the KBIO plain old data equivalent"""

        @property
        def mode (self) :
          mode = KBIO.HW_MODE(self.Mode)
          return mode.name

        @property
        def connection (self) :
          connection = KBIO.HW_CNX(self.Connection)
          return connection.name

    #--------------------------------------------------------------------------#

    class Error:
        """Class to encapsulate an EClib error code."""

        def __init__ (self, code) :
            """Encapsulate an error code."""
            self.code = code

        @property
        def translate (self) :
            """Turn error code into tuple (code, enum-name, clear text)."""
            code = self.code
            try :
                tag = self.enum(code)
                en_clair = self.list_by_tag[tag]
                traduction = code, tag.name, en_clair
            except :
                traduction = code, "UNKNOWN_ERROR", "Unknown error"
            return traduction

        def __repr__ (self) :
            """Full text representation of error"""
            code, tag, description = self.translate
            return f"{self.name} error {code} [{tag}], {description}"

        def __str__ (self) :
            """Clear text representation of error code."""
            code, tag, description = self.translate
            return f"{description}"

        def is_error (self,error) :
            """Return whether error code is same as numeric value"""
            is_error = (self.code == error.value)
            return is_error

        def check (self, context=None, abort=True, show=True) :
            """Raise an error or print an error in case an error happened.
            
               context gives local info in case of error, otherwise keep default one
               abort decide between raising an exception versus just printing
               (if show is set to True)
            """
            happened = (self.code != 0)
            if happened :
                if abort :
                    if context is not None :
                        self.name = context
                    exception = KBIOError(self)
                    raise exception
                else :
                    if show :
                        _log.error(f"{context} : {self.translate}")

        #----------------------------------------------------------------------#

        name = "EClib"
        enum = KBIO.ERROR
        list_by_tag = {
            KBIO.ERROR.NOERROR                   : "No error",
            KBIO.ERROR.GEN_NOTCONNECTED          : "No instrument connected",
            KBIO.ERROR.GEN_CONNECTIONINPROGRESS  : "Connection in progress",
            KBIO.ERROR.GEN_CHANNELNOTPLUGGED     : "Selected channel(s) unplugged",
            KBIO.ERROR.GEN_INVALIDPARAMETERS     : "Invalid function parameters",
            KBIO.ERROR.GEN_FILENOTEXISTS         : "Selected file does not exist",
            KBIO.ERROR.GEN_FUNCTIONFAILED        : "Function failed",
            KBIO.ERROR.GEN_NOCHANNELSELECTED     : "No channel selected",
            KBIO.ERROR.GEN_INVALIDCONF           : "Invalid instrument configuration",
            KBIO.ERROR.GEN_ECLAB_LOADED          : "EC-Lab firmware loaded on the instrument",
            KBIO.ERROR.GEN_LIBNOTCORRECTLYLOADED : "Library not correctly loaded in memory",
            KBIO.ERROR.GEN_USBLIBRARYERROR       : "USB library not correctly loaded in memory",
            KBIO.ERROR.GEN_FUNCTIONINPROGRESS    : "Function already in progress",
            KBIO.ERROR.GEN_CHANNEL_RUNNING       : "Selected channel(s) already used",
            KBIO.ERROR.GEN_DEVICE_NOTALLOWED     : "Device not allowed",
            KBIO.ERROR.GEN_UPDATEPARAMETERS      : "Invalid update function parameters",
            KBIO.ERROR.INSTR_VMEERROR            : "Internal instrument communication failed",
            KBIO.ERROR.INSTR_TOOMANYDATA         : "Too many data to transfer from the instrument (device error)",
            KBIO.ERROR.INSTR_RESPNOTPOSSIBLE     : "Selected channel(s) unplugged (device error)",
            KBIO.ERROR.INSTR_RESPERROR           : "Instrument response error",
            KBIO.ERROR.INSTR_MSGSIZEERROR        : "Invalid message size",
            KBIO.ERROR.COMM_COMMFAILED           : "Communication failed with the instrument",
            KBIO.ERROR.COMM_CONNECTIONFAILED     : "Cannot establish connection with the instrument",
            KBIO.ERROR.COMM_WAITINGACK           : "Waiting for the instrument response",
            KBIO.ERROR.COMM_INVALIDIPADDRESS     : "Invalid IP address",
            KBIO.ERROR.COMM_ALLOCMEMFAILED       : "Cannot allocate memory in the instrument",
            KBIO.ERROR.COMM_LOADFIRMWAREFAILED   : "Cannot load firmware into selected channel(s)",
            KBIO.ERROR.COMM_INCOMPATIBLESERVER   : "Communication firmware not compatible",
            KBIO.ERROR.COMM_MAXCONNREACHED       : "Maximum number of allowed connections reached",
            KBIO.ERROR.FIRM_FIRMFILENOTEXISTS    : "Cannot find kernel.bin file",
            KBIO.ERROR.FIRM_FIRMFILEACCESSFAILED : "Cannot read kernel.bin file",
            KBIO.ERROR.FIRM_FIRMINVALIDFILE      : "Invalid kernel.bin file",
            KBIO.ERROR.FIRM_FIRMLOADINGFAILED    : "Cannot load kernel.bin on the selected channel(s)",
            KBIO.ERROR.FIRM_XILFILENOTEXISTS     : "Cannot find FPGA file",
            KBIO.ERROR.FIRM_XILFILEACCESSFAILED  : "Cannot read FPGA file",
            KBIO.ERROR.FIRM_XILINVALIDFILE       : "Invalid FPGA file",
            KBIO.ERROR.FIRM_XILLOADINGFAILED     : "Cannot load FPGA file on the selected channel(s)",
            KBIO.ERROR.FIRM_FIRMWARENOTLOADED    : "No firmware loaded on the selected channel(s)",
            KBIO.ERROR.FIRM_FIRMWAREINCOMPATIBLE : "Loaded firmware not compatible with the library",
            KBIO.ERROR.TECH_ECCFILENOTEXISTS     : "Cannot find the selected ECC file",
            KBIO.ERROR.TECH_INCOMPATIBLEECC      : "ECC file not compatible with the channel firmware",
            KBIO.ERROR.TECH_ECCFILECORRUPTED     : "ECC file corrupted",
            KBIO.ERROR.TECH_LOADTECHNIQUEFAILED  : "Cannot load the ECC file",
            KBIO.ERROR.TECH_DATACORRUPTED        : "Data returned by the instrument are corrupted",
            KBIO.ERROR.TECH_MEMFULL              : "Cannot load techniques: full memory",
            KBIO.ERROR.OPT_CHANGE                : "Number of options changed",
            KBIO.ERROR.OPT_4A_ERROR              : "4A amplifier unknown error",
            KBIO.ERROR.OPT_4A_OVERTEMP           : "4A amplifier temperature overflow",
            KBIO.ERROR.OPT_4A_BADPOWER           : "4A amplifier bad power",
            KBIO.ERROR.OPT_4A_POWERFAIL          : "4A amplifier power fail",
            KBIO.ERROR.OPT_48V_ERROR             : "48V amplifier unknown error",
            KBIO.ERROR.OPT_48V_OVERTEMP          : "48V amplifier temperature overflow",
            KBIO.ERROR.OPT_48V_BADPOWER          : "48V amplifier bad power",
            KBIO.ERROR.OPT_48V_POWERFAIL         : "48V amplifier power fail",
            KBIO.ERROR.OPT_10A5V_ERROR           : "10A 5V amplifier error",
            KBIO.ERROR.OPT_10A5V_OVERTEMP        : "10A 5V amplifier overheat",
            KBIO.ERROR.OPT_10A5V_BADPOWER        : "10A 5V amplifier bad power",
            KBIO.ERROR.OPT_10A5V_POWERFAIL       : "10A 5V amplifier power fail",
            KBIO.ERROR.OPT_1A48VP_ERROR          : "1A48VP amplifier error",
            KBIO.ERROR.OPT_1A48VP_OVERTEMP       : "1A48VP amplifier overheat",
            KBIO.ERROR.OPT_1A48VP_BADPOWER       : "1A48VP amplifier bad power",
            KBIO.ERROR.OPT_1A48VP_POWERFAIL      : "1A48VP amplifier power fail",

        }

    #==========================================================================#

    class FindError(Error):
        name = "blfind"
        enum = KBIO.FIND_ERROR
        list_by_tag = {
            KBIO.FIND_ERROR.NO_ERROR           : "no error",
            KBIO.FIND_ERROR.UNKNOWN_ERROR      : "unknown error",
            KBIO.FIND_ERROR.INVALID_PARAMETER  : "invalid function parameters",
            KBIO.FIND_ERROR.ACK_TIMEOUT        : "instrument response timeout",
            KBIO.FIND_ERROR.EXP_RUNNING        : "experiment is running on instrument",
            KBIO.FIND_ERROR.CMD_FAILED         : "instrument do not execute command",
            KBIO.FIND_ERROR.FIND_FAILED        : "find failed",
            KBIO.FIND_ERROR.SOCKET_WRITE       : "cannot write the request of the descriptions of Ethernet instruments",
            KBIO.FIND_ERROR.SOCKET_READ        : "cannot read descriptions of Ethernet instrument",
            KBIO.FIND_ERROR.CFG_MODIFY_FAILED  : "set TCP/IP parameters failed",
            KBIO.FIND_ERROR.READ_PARAM_FAILED  : "deserialization of TCP/IP parameters failed",
            KBIO.FIND_ERROR.EMPTY_PARAM        : "not any TCP/IP parameters in serialization",
            KBIO.FIND_ERROR.IP_FORMAT          : "invalid format of IP address",
            KBIO.FIND_ERROR.NM_FORMAT          : "invalid format of netmask address",
            KBIO.FIND_ERROR.GW_FORMAT          : "invalid format of gateway address",
            KBIO.FIND_ERROR.IP_NOT_FOUND       : "instrument to modify not found",
            KBIO.FIND_ERROR.IP_ALREADYEXIST    : "new IP address in TCP/IP parameters",
        }

    #==========================================================================#

    """ List of the EClib entry points, their parameter types and return type if not standard. """

    ecl_api = [
        ("BL_GetLibVersion",
         [c_char_p, c_uint32_p]),
        ("BL_Connect",
            [c_char_p, c_uint8, c_int32_p, KBIO.DEVICE_INFO]),
        ("BL_GetUSBdeviceinfos",
            [c_uint32, c_char_p, c_uint32_p, c_char_p, c_uint32_p, c_char_p, c_uint32_p],
             c_bool),
        ("BL_Disconnect",
            [c_int32]),
        ("BL_TestConnection",
            [c_int32]),
        ("BL_TestCommSpeed",
            [c_int32, c_uint8, c_int32_p, c_int32_p]),
        ("BL_GetChannelsPlugged",
            [c_int32, KBIO.ChannelsArray, c_uint8]),
        ("BL_LoadFirmware",
            [c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8, c_bool, c_bool, c_char_p, c_char_p ]),
        ("BL_GetChannelInfos",
            [c_int32, c_uint8, KBIO.CH_INFO]),
        ("BL_GetHardConf",
            [c_int32, c_uint8, KBIO.HW_CONF]),
        ("BL_SetHardConf",
            [c_int32, c_uint8, KBIO.HardwareConf]),
        ("BL_GetErrorMsg",
            [c_int32, c_char_p, c_uint32_p],
             int),
        ("BL_GetOptErr",
            [c_int32, c_int8, c_int32_p, c_int32_p]),
        ("BL_GetMessage",
            [c_int32, c_uint8, c_char_p, c_uint32_p]),
        ("BL_LoadTechnique",
            [c_int32, c_uint8, c_char_p, KBIO.EccParams, c_bool, c_bool, c_bool]),
        ("BL_DefineBoolParameter",
            [c_char_p, c_bool, c_int32, KBIO.ECC_PARM]),
        ("BL_DefineSglParameter",
            [c_char_p, c_float, c_int32, KBIO.ECC_PARM]),
        ("BL_DefineIntParameter",
            [c_char_p, c_int32, c_int32, KBIO.ECC_PARM]),
        ("BL_UpdateParameters",
            [c_int32, c_int8, c_int32, KBIO.ECC_PARMS, c_char_p]),
        ("BL_GetParamInfos",
            [c_int32, c_int8, c_int32, KBIO.TECHNIQUE_INFOS]),
        ("BL_GetTechniqueInfos",
            [c_int32, c_int8, c_int32, KBIO.TECHNIQUE_INFOS]),
        ("BL_StartChannel",
            [c_int32, c_int8]),
        ("BL_StartChannels",
            [c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8]),
        ("BL_StopChannel",
            [c_int32, c_int8]),
        ("BL_StopChannels",
            [c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8]),
        ("BL_GetCurrentValues",
            [c_int32, c_int8, KBIO.CURRENT_VALUES]),
        ("BL_GetData",
            [c_int32, c_int8, KBIO.DataBuffer, KBIO.DATA_INFO, KBIO.CURRENT_VALUES]),
        ("BL_ConvertNumericIntoSingle",
            [c_uint32, c_float_p]),
    ]

    """ List of the blfind entry points, and their parameter types. """

    blfind_api = [
        ("BL_FindEChemDev",
            [c_char_p, c_uint32_p, c_uint32_p]),
        ("BL_FindEChemEthDev",
            [c_char_p, c_uint32_p, c_uint32_p]),
        ("BL_FindEChemUsbDev",
            [c_char_p, c_uint32_p, c_uint32_p]),
        ("BL_SetConfig",
            [c_char_p, c_char_p]),
    ]

    #--------------------------------------------------------------------------#

    def __init__ (self, eclib_file=None, blfind_file=None) :
        """Rebuild the api dicts with ctype function with attribute and result types."""

        if eclib_file is None:
            eclib_file = ECLIB_PATH
        if blfind_file is None:
            blfind_file = BLFIND_PATH

        # first visit the EClib.dll API ..
        self.bind_api(self.ecl_api, eclib_file)

        # .. next visit the blfind.dll API
        self.bind_api(self.blfind_api, blfind_file)

    #--------------------------------------------------------------------------#

    def bind_api (self, api, dll_file) :
        try :
            dll = WinDLL(dll_file) if dll_file else None
        except FileNotFoundError as e :
            raise FileNotFoundError(dll_file)
        except OSError as e :
            if e.winerror == 193 :
                raise RuntimeError(f"{dll_file} and Python mismatch.")
            else :
                raise

        for name, argtypes, *args in api :
            # rebuild api dict with ctype func with attributes
            # and optional result type
            self.bind_function(dll,name,argtypes,*args)

    #--------------------------------------------------------------------------#

    def bind_function (self, dll, name, argtypes, restype=None) :
        """Rebind api with wrapped ctype function, registering attribute types and error handling."""

        if dll is None :

            # if missing, force errors on each entry point

            def force_error (*args, abort=True) :
                # makeshift error
                error = self.Error(-999)
                error.check('missing dll',abort)
                return error

            # replace function with force_error
            setattr(self, name, force_error)

        else :

            # retrieve function by name
            function = dll[name]
            # set its argument types
            function.argtypes = argtypes

            # by default function will be error checked on return
            guarded = (restype is None)
            # set function return type
            function.restype = self.Error if guarded else restype

            if guarded :
                # wrap function with a check of return code ..
                def guarded_call (*args, abort=True) :
                    error = function(*args)
                    error.check(name,abort)
                    return error
                # replace function with wrapper function
                setattr(self, name, guarded_call)
            else :
                # .. else set it as the function with argtypes+restype set
                setattr(self, name, function)

#==============================================================================#
