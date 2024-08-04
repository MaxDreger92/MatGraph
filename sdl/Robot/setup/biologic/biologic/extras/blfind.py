""" Utility to discover Biologic instruments using the EC-Lab OEM Package library.

Adapted from the EC-Lab OEM Package library.

| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/23
"""

from __future__ import annotations

import traceback
from argparse import ArgumentParser
from typing import TYPE_CHECKING

from kbio.api import KBIOError
from kbio.types import USB_device, Ethernet_device

from biologic import get_kbio_api

if TYPE_CHECKING:
    from typing import Any


#------------------------------------------------------------------------------#

# Test parameters, to be adjusted

cli = ArgumentParser(
    description="Discover Bio-Logic instruments over TCP/IP or USB."
)
cli.add_argument(
    'kind', nargs='?', choices=('all', 'ethernet', 'usb'), default='all',
    help="Select the type of interface used to detect instruments. Defaults to all.",
)
cli.add_argument(
    '-v', action='store_true', dest='verbosity',
    help="Increase verbosity of error messages.",
)
cli.add_argument(
    '--eclab-path', default=None, dest='eclab_path',
    help="Select the directory containing EC-Lab SDK binaries.",
    metavar="DIR",
)

#------------------------------------------------------------------------------#

# one liner functions

def exception_brief (e, extended=False) :
    """Return either a simple version of an exception, or a more verbose one."""
    brief = f"{type(e).__name__} : {e}"
    if extended:
        brief += "".join(traceback.format_tb(e.__traceback__))
    return brief

def print_hline():  print('#' + '-' * 78 + '#')
def print_exception(e, verbosity) : print(f"{exception_brief(e, verbosity)}")


#==============================================================================#

def main(args: Any = None) -> None:
    """ Main code : use discovery functions with the  package API. """

    if args is None:
        args = cli.parse_args()

    try :

        # API initialize
        api = get_kbio_api(args.eclab_path)

        # discover instruments

        if args.kind == 'all' :
            # BL_FindEChemDev
            instruments = api.FindEChemDev()
        elif args.kind == 'usb' :
            # BL_FindEChemUsbDev
            instruments = api.FindEChemUsbDev()
        elif args.kind == 'ethernet' :
            # BL_FindEChemEthDev
            instruments = api.FindEChemEthDev()
        else :
          raise RuntimeError(f"argument ({args.kind}) must be one of [all,usb,ethernet]")

        if instruments :

            for instrument in instruments :

                print_hline()

                if isinstance(instrument, USB_device) :

                    # print discovered information
                    print(f"{instrument.address} : ", end='')

                    index = instrument.index

                    # BL_GetUSBdeviceinfos
                    usb_info = api.USB_DeviceInfo(index)
                    print(f"{usb_info}")

                    address = instrument.address

                elif isinstance(instrument, Ethernet_device) :

                    # extract information from instrument type
                    address = instrument.config[0]
                    name = instrument.name.strip()
                    serial_nb = instrument.serial.strip()
                    dev_id = instrument.identifier.strip()

                    # print discovered information
                    print(f"device @ {address} : '{name}', s/n '{serial_nb}', id '{dev_id}'")

                else :

                    raise RuntimeError(f"unknown device type ({instrument})")

                # Now print brief information about instrument channels ..

                # BL_Connect
                id_, device_info = api.Connect(address)

                version = f"v{device_info.FirmwareVersion/100:.2f}"
                print(f"> {device_info.model}, {version}")

                # BL_GetChannelsPlugged
                # .. PluggedChannels is a generator, expand into a set
                channels = {*api.PluggedChannels(id_)}

                for channel in sorted(channels) :
                    # BL_GetChannelInfos
                    channel_info = api.GetChannelInfo(id_,channel)
                    print(f">   channel {channel:2} : {channel_info.board} board, ", end='')
                    if channel_info.has_no_firmware :
                        print("no firmware")
                    elif channel_info.is_kernel_loaded :
                        version = channel_info.FirmwareVersion/1000
                        version = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"
                        print(f"{channel_info.firmware} (v{version})")
                    else :
                        version = channel_info.FirmwareVersion/100
                        version = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"
                        print(f"{channel_info.firmware} (v{version})")

                api.Disconnect(id_)

            print_hline()

        else :

            print("no EC instruments detected")

    except KBIOError as e :
        print(f"discover : {e!r}")

    except KeyboardInterrupt :
        print(".. interrupted")

    except Exception as e :
        print_exception(e, args.verbosity)

#==============================================================================#

if __name__ == '__main__':
    main()
