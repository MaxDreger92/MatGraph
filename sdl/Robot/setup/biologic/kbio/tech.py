""" Bio-Logic OEM package python API.

This module contains support functions when building technique parameters,
and decoding experiment records.

"""

from dataclasses import dataclass

import kbio.types as KBIO
from kbio.tech_types import TECH_ID

@dataclass
class ECC_parm :
    """ECC param template"""
    label: str
    type_: type

# functions to build the technique ECC parameters (structure+contents)

def make_ecc_parm (api, ecc_parm, value=0, index=0) :
    """Given an ECC_parm template, create and return an EccParam, with its value and optional index."""
    parm = KBIO.EccParam()
    # BL_Define<xxx>Parameter
    # .. value is converted to its proper type, which DefineParameter will use
    api.DefineParameter(ecc_parm.label, ecc_parm.type_(value), index, parm)
    return parm

def make_ecc_parms (api, *ecc_parm_list) :
    """Create an EccParam array from an EccParam list, and return an EccParams refering to it."""
    nb_parms = len(ecc_parm_list)
    parms_array = KBIO.ECC_PARM_ARRAY(nb_parms)

    for i,parm in enumerate(ecc_parm_list) :
        parms_array[i] = parm

    parms = KBIO.EccParams(nb_parms, parms_array)
    return parms

# function to handle records from a running experiment

def print_experiment_data (api, data) :
    """Unpack the experiment data, decode it according to the technique, display it,
       then return the experiment status """

    current_values, data_info, data_record = data

    status = current_values.State
    status = KBIO.PROG_STATE(status).name

    tech_name = TECH_ID(data_info.TechniqueID).name

    # synthetic info for current record
    info = {
      'tb': current_values.TimeBase,
      'ix': data_info.TechniqueIndex,
      'tech': tech_name,
      'proc': data_info.ProcessIndex,
      'loop': data_info.loop,
      'skip': data_info.IRQskipped,
    }

    print("> data info :")
    print(info)

    ix = 0

    for _ in range(data_info.NbRows) :

        if tech_name == 'OCV' :

            # progress through record
            inx = ix + data_info.NbCols

            # extract timestamp and one row
            t_high, t_low, *row =  data_record[ix:inx]

            nb_words = len(row)
            if nb_words == 1 :
                vmp3 = False
            elif nb_words == 2 :
                vmp3 = True
            else :
                raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")
    
            # compute timestamp in seconds
            t_rel = (t_high << 32) + t_low
            t = current_values.TimeBase * t_rel
    
            # Ewe is a float
            Ewe = api.ConvertNumericIntoSingle(row[0])

            parsed_row = {'t': t , 'Ewe': Ewe}

            if vmp3 :
                # Ece is a float
                Ece = api.ConvertNumericIntoSingle(row[1])
                parsed_row['Ece'] = Ece

        elif tech_name == 'CP' :

            inx = ix + data_info.NbCols
            t_high, t_low, *row =  data_record[ix:inx]

            nb_words = len(row)
            if nb_words != 3 :
                raise RuntimeError(f"{tech_name} : unexpected record length ({nb_words})")

            # Ewe is a float
            Ewe = api.ConvertNumericIntoSingle(row[0])

            # current is a float
            I = api.ConvertNumericIntoSingle(row[1])

            # technique cycle is an integer
            cycle = row[2]
    
            # compute timestamp in seconds
            t_rel = (t_high << 32) + t_low
            t = current_values.TimeBase * t_rel
    
            parsed_row = {'t': t , 'Ewe': Ewe, 'I': I, 'cycle': cycle}

        else :

            # besides the previous 2 known techniques, this is provided
            # to show a raw dump of the record
            inx = ix + data_info.NbCols
            row =  data_record[ix:inx]
            parsed_row = [ f"0x{word:08X}" for word in row ]

        print("> data record :")
        print(parsed_row)

        ix = inx

    return status

