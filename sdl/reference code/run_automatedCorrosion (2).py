# -*-coding:utf-8 -*-
'''
@Time    :   2024/06/26 18:30:20
@Author  :   Daniel Persaud
@Version :   1.0
@Contact :   da.persaud@mail.utoronto.ca
@Desc    :   this is a run script for running automated corrosion tests
'''

#%%
# IMPORT DEPENDENCIES------------------------------------------------------------------------------
import json
import os
import logging
from datetime import datetime
import sys
import time





import pandas as pd
from biologic.biologic.techniques.ca import CAStep, CAParams, CATechnique
from biologic.biologic.techniques.cpp import CPPParams, CPPTechnique
from biologic.biologic.techniques.ocv import OCVParams, OCVTechnique
from biologic.biologic.techniques.peis import PEISParams, SweepMode, PEISTechnique, PEISData
from biologic.kbio.types import BANDWIDTH, E_RANGE, I_RANGE


# HELPER FUNCTIONS---------------------------------------------------------------------------------

# define helper functions to manage solution
def fillWell(opentronsClient,
             strLabwareName_from,
             strWellName_from,
             strOffsetStart_from,
             strPipetteName,
             strLabwareName_to,
             strWellName_to,
             strOffsetStart_to,
             intVolume: int,
             fltOffsetX_from: float = 0,
             fltOffsetY_from: float = 0,
             fltOffsetZ_from: float = 0,
             fltOffsetX_to: float = 0,
             fltOffsetY_to: float = 0,
             fltOffsetZ_to: float = 0,
             intMoveSpeed : int = 100
             ) -> None:
    '''
    function to manage solution in a well because the maximum volume the opentrons can move is 1000 uL

    Parameters
    ----------
    opentronsClient : opentronsClient
        instance of the opentronsClient class

    strLabwareName_from : str
        name of the labware to aspirate from

    strWellName_from : str
        name of the well to aspirate from

    strOffset_from : str
        offset to aspirate from
        options: 'bottom', 'center', 'top'

    strPipetteName : str
        name of the pipette to use

    strLabwareName_to : str
        name of the labware to dispense to

    strWellName_to : str
        name of the well to dispense to

    strOffset_to : str
        offset to dispense to
        options: 'bottom', 'center', 'top'

    intVolume : int
        volume to transfer in uL

    intMoveSpeed : int
        speed to move in mm/s
        default: 100
    '''

    # while the volume is greater than 1000 uL
    while intVolume > 1000:
        # move to the well to aspirate from
        opentronsClient.moveToWell(strLabwareName = strLabwareName_from,
                                   strWellName = strWellName_from,
                                   strPipetteName = strPipetteName,
                                   strOffsetStart = 'top',
                                   fltOffsetX = fltOffsetX_from,
                                   fltOffsetY = fltOffsetY_from,
                                   intSpeed = intMoveSpeed)

        # aspirate 1000 uL
        opentronsClient.aspirate(strLabwareName = strLabwareName_from,
                                 strWellName = strWellName_from,
                                 strPipetteName = strPipetteName,
                                 intVolume = 1000,
                                 strOffsetStart = strOffsetStart_from,
                                 fltOffsetX = fltOffsetX_from,
                                 fltOffsetY = fltOffsetY_from,
                                 fltOffsetZ = fltOffsetZ_from)

        # move to the well to dispense to
        opentronsClient.moveToWell(strLabwareName = strLabwareName_to,
                                   strWellName = strWellName_to,
                                   strPipetteName = strPipetteName,
                                   strOffsetStart = 'top',
                                   fltOffsetX = fltOffsetX_to,
                                   fltOffsetY = fltOffsetY_to,
                                   intSpeed = intMoveSpeed)

        # dispense 1000 uL
        opentronsClient.dispense(strLabwareName = strLabwareName_to,
                                 strWellName = strWellName_to,
                                 strPipetteName = strPipetteName,
                                 intVolume = 1000,
                                 strOffsetStart = strOffsetStart_to,
                                 fltOffsetX = fltOffsetX_to,
                                 fltOffsetY = fltOffsetY_to,
                                 fltOffsetZ = fltOffsetZ_to)

        # subtract 1000 uL from the volume
        intVolume -= 1000


    # move to the well to aspirate from
    opentronsClient.moveToWell(strLabwareName = strLabwareName_from,
                               strWellName = strWellName_from,
                               strPipetteName = strPipetteName,
                               strOffsetStart = 'top',
                               fltOffsetX = fltOffsetX_from,
                               fltOffsetY = fltOffsetY_from,
                               intSpeed = intMoveSpeed)

    # aspirate the remaining volume
    opentronsClient.aspirate(strLabwareName = strLabwareName_from,
                             strWellName = strWellName_from,
                             strPipetteName = strPipetteName,
                             intVolume = intVolume,
                             strOffsetStart = strOffsetStart_from,
                             fltOffsetX = fltOffsetX_from,
                             fltOffsetY = fltOffsetY_from,
                             fltOffsetZ = fltOffsetZ_from)

    # move to the well to dispense to
    opentronsClient.moveToWell(strLabwareName = strLabwareName_to,
                               strWellName = strWellName_to,
                               strPipetteName = strPipetteName,
                               strOffsetStart = 'top',
                               fltOffsetX = fltOffsetX_to,
                               fltOffsetY = fltOffsetY_to,
                               intSpeed = intMoveSpeed)

    # dispense the remaining volume
    opentronsClient.dispense(strLabwareName = strLabwareName_to,
                             strWellName = strWellName_to,
                             strPipetteName = strPipetteName,
                             intVolume = intVolume,
                             strOffsetStart = strOffsetStart_to,
                             fltOffsetX = fltOffsetX_to,
                             fltOffsetY = fltOffsetY_to,
                             fltOffsetZ = fltOffsetZ_to)

    return

# define helper function to wash electrode
def washElectrode(opentronsClient,
                  strLabwareName,
                  arduinoClient):
    '''
    function to wash electrode

    Parameters
    ----------
    opentronsClient : opentronsClient
        instance of the opentronsClient class

    strLabwareName : str
        name of the labware to wash electrode in

    intCycle : int
        number of cycles to wash electrode

    '''

    # fill wash station with Di water
    arduinoClient.dispense_ml(pump=4, volume=15)

    # move to wash station
    opentronsClient.moveToWell(strLabwareName = strLabwareName,
                               strWellName = 'A2',
                               strPipetteName = 'p1000_single_gen2',
                               strOffsetStart = 'top',
                               intSpeed = 50)

    # move to wash station
    opentronsClient.moveToWell(strLabwareName = strLabwareName,
                               strWellName = 'A2',
                               strPipetteName = 'p1000_single_gen2',
                               strOffsetStart = 'bottom',
                               fltOffsetY = -15,
                               fltOffsetZ = -10,
                               intSpeed = 50)

    arduinoClient.set_ultrasound_on(cartridge = 0, time = 30)

    # drain wash station
    arduinoClient.dispense_ml(pump=3, volume=16)

    # fill wash station with acid
    arduinoClient.dispense_ml(pump=5, volume=10)

    # move to wash station
    arduinoClient.set_ultrasound_on(cartridge = 0, time = 30)

    # drain wash station
    arduinoClient.dispense_ml(pump=3, volume=11)

    # fill wash station with Di water
    arduinoClient.dispense_ml(pump=4, volume=15)


    arduinoClient.set_ultrasound_on(cartridge = 0, time = 30)

    # drain wash station
    arduinoClient.dispense_ml(pump=3, volume=16)

    return


#%%
# SETUP LOGGING------------------------------------------------------------------------------------

# get the path to the current directory
strWD = os.getcwd()
# get the name of this file
strLogFileName = os.path.basename(__file__)
# split the file name and the extension
strLogFileName = os.path.splitext(strLogFileName)[0]
# add .log to the file name
strLogFileName = strLogFileName + ".log"
# join the log file name to the current directory
strLogFilePath = os.path.join(strWD, strLogFileName)

# Initialize logging
logging.basicConfig(
    level = logging.DEBUG,                                                      # Can be changed to logging.INFO to see less
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(strLogFilePath, mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)

#%%
# INITIALIZE EXPERIMENT----------------------------------------------------------------------------
robotIP = "100.67.86.197"
# initialize an the opentrons client
oc = opentronsClient(strRobotIP = robotIP)

# get the current time
strTime_start = datetime.now().strftime("%H:%M:%S")

# make a variable to store the well in the autodial cell to be used
strWell2Test_autodialCell = 'C2'

# make a variable to store the well in the test solution to be used
strWell2Test_vialRack = 'A2'

# get the current date
strDate = datetime.now().strftime("%Y%m%d")

# provide a run number
strRunNumber = "002"

# make a strin with the experimentID
strExperimentID = f"{strDate}_{strRunNumber}"

# make a new directory in the data folder to store the results
strExperimentPath = os.path.join(strWD, 'data', strExperimentID)
os.makedirs(strExperimentPath, exist_ok=True)

# make a metadata file in the new directory
strMetadataPath = os.path.join(strExperimentPath, f"{strExperimentID}_metadata.json")
dicMetadata = {"date": strDate,
               "time": strTime_start,
               "runNumber": strRunNumber,
               "experimentID": strExperimentID,
               "status": "running"}

with open(strMetadataPath, 'w') as f:
    json.dump(dicMetadata, f)

# log the start of the experiment
logging.info(f"experiment {strExperimentID} started!")

#%%
# SETUP OPENTRONS PLATFORM-------------------------------------------------------------------------

# -----LOAD OPENTRONS STANDARD LABWARE-----

    # -----LOAD OPENTRONS TIP RACK-----
# load opentrons tip rack in slot 1
strID_pipetteTipRack = oc.loadLabware(intSlot = 1,
                                      strLabwareName = 'opentrons_96_tiprack_1000ul')

# -----LOAD CUSTOM LABWARE-----

# get path to current directory
strCustomLabwarePath = os.getcwd()
# join "labware" folder to current directory
strCustomLabwarePath = os.path.join(strCustomLabwarePath, 'labware')

    # -----LOAD 25ml VIAL RACK-----
# join "nis_8_reservoir_25000ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'nis_8_reservoir_25000ul.json')
# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)
# load custom labware in slot 7
strID_vialRack = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                      intSlot = 2)

    # -----LOAD WASH STATION-----
# join "nis_2_wellplate_30000ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'nis_2_wellplate_30000ul.json')
# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)
# load custom labware in slot 3
strID_washStation = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                         intSlot = 3)

    # -----LOAD AUTODIAL CELL-----
# join "nis_1_autodial_cell_10000ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'autodial_25_reservoir_4620ul.json')
# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)
# load custom labware in slot 4
strID_autodialCell = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                          intSlot = 4)

    # -----LOAD 50ml BEAKERS-----
# join "tlg_1_reservoir_50000ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'tlg_1_reservoir_50000ul.json')

# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)

strID_dIBeaker = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                      intSlot = 5)

    # -----LOAD NIS'S REACTOR-----
# join "nis_15_wellplate_3895ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'nis_15_wellplate_3895ul.json')

# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)

strID_NISreactor = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                     intSlot = 9)

    # -----LOAD ELECTRODE TIP RACK-----
# join "nis_4_tiprack_1ul.json" to labware directory
strCustomLabwarePath_temp = os.path.join(strCustomLabwarePath, 'nistall_4_tiprack_1ul.json')

# read json file
with open(strCustomLabwarePath_temp) as f:
    dicCustomLabware_temp = json.load(f)

# load custom labware in slot 10
strID_electrodeTipRack = oc.loadCustomLabware(dicLabware = dicCustomLabware_temp,
                                              intSlot = 10)



# LOAD OPENTRONS STANDARD INSTRUMENTS--------------------------------------------------------------
# add pipette
oc.loadPipette(strPipetteName = 'p1000_single_gen2',
               strMount = 'right')

#%%
# MOVE OPENTRONS INSTRUMENTS-----------------------------------------------------------------------

# turn the lights on
oc.lights(True)

# home robot
oc.homeRobot()

# -----USE OPENTRONS TO MOVE CORROSIVE SOLUTIONS-----
# move to pipette tip rack
oc.moveToWell(strLabwareName = strID_pipetteTipRack,
              strWellName = 'A1',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetY = 1,
              intSpeed = 100)
# pick up pipette tip
oc.pickUpTip(strLabwareName = strID_pipetteTipRack,
             strPipetteName = 'p1000_single_gen2',
             strWellName = 'A1',
             fltOffsetY = 1)

fillWell(opentronsClient = oc,
         strLabwareName_from = strID_vialRack,
         strWellName_from = strWell2Test_vialRack,
         strOffsetStart_from = 'bottom',
         strPipetteName = 'p1000_single_gen2',
         strLabwareName_to = strID_autodialCell,
         strWellName_to = strWell2Test_autodialCell,
         strOffsetStart_to = 'center',
         intVolume = 400,
         fltOffsetX_from = 0,
         fltOffsetY_from = 0,
         fltOffsetZ_from = 2,
         fltOffsetX_to = -1,
         fltOffsetY_to = 0.5,
         fltOffsetZ_to = 0,
         intMoveSpeed = 100
         )


# move back to pipette tip rack
oc.moveToWell(strLabwareName = strID_pipetteTipRack,
              strWellName = 'A1',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetY = 1,
              intSpeed = 100)
# drop pipette tip
oc.dropTip(strLabwareName = strID_pipetteTipRack,
           strPipetteName = 'p1000_single_gen2',
           strWellName = 'A1',
           strOffsetStart = 'bottom',
           fltOffsetY = 1,
           fltOffsetZ = 7)

# move to the other tip in the pipette tip rack
oc.moveToWell(strLabwareName = strID_pipetteTipRack,
              strWellName = 'A12',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetY = 1,
              intSpeed = 100)
# pick up pipette tip
oc.pickUpTip(strLabwareName = strID_pipetteTipRack,
             strPipetteName = 'p1000_single_gen2',
             strWellName = 'A12',
             fltOffsetY = 1)

fillWell(opentronsClient = oc,
         strLabwareName_from = strID_dIBeaker,
         strWellName_from = 'A1',
         strOffsetStart_from = 'bottom',
         strPipetteName = 'p1000_single_gen2',
         strLabwareName_to = strID_autodialCell,
         strWellName_to = strWell2Test_autodialCell,
         strOffsetStart_to = 'center',
         intVolume = 3600,
         fltOffsetX_from = 0,
         fltOffsetY_from = 0,
         fltOffsetZ_from = 2,
         fltOffsetX_to = -1,
         fltOffsetY_to = 0.5,
         fltOffsetZ_to = 0,
         intMoveSpeed = 100
         )

# move to the other tip in the pipette tip rack
oc.moveToWell(strLabwareName = strID_pipetteTipRack,
              strWellName = 'A12',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetY = 1,
              intSpeed = 100)
# drop pipette tip
oc.dropTip(strLabwareName = strID_pipetteTipRack,
           strPipetteName = 'p1000_single_gen2',
           strWellName = 'A12',
           strOffsetStart = 'bottom',
           fltOffsetY = 1,
           fltOffsetZ = 7)



# -----USE OPENTRONS TO MOVE ELECTRODES-----

# move to electrode tip rack
oc.moveToWell(strLabwareName = strID_electrodeTipRack,
              strWellName = 'A2',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetX = 0.6,
              fltOffsetY = 0.5,
              fltOffsetZ = 3,
              intSpeed = 100)
# pick up electrode tip
oc.pickUpTip(strLabwareName = strID_electrodeTipRack,
             strPipetteName = 'p1000_single_gen2',
             strWellName = 'A2',
             fltOffsetX = 0.6,
             fltOffsetY = 0.5)

# move to top only!!
oc.moveToWell(strLabwareName = strID_autodialCell,
              strWellName = strWell2Test_autodialCell,
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetX = 0.5,
              fltOffsetY = 0.5,
              fltOffsetZ = 5,
              intSpeed = 50)

# move to autodial cell
oc.moveToWell(strLabwareName = strID_autodialCell,
              strWellName = strWell2Test_autodialCell,
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetX = 0.5,
              fltOffsetY = 0.5,
              fltOffsetZ = -25,
              intSpeed = 50)

#%%
# RUN ELECTROCHEMICAL EXPERIMENT-------------------------------------------------------------------

# -----PEIS-----
# create PEIS parameters
peisParams_irCompensation = PEISParams(
    vs_initial = False,
    initial_voltage_step = 0.0,
    duration_step = 0,
    record_every_dT = 0.5,
    record_every_dI = 0.01,
    final_frequency = 1,
    initial_frequency = 100000,
    sweep = SweepMode.Logarithmic,
    amplitude_voltage = 0.02,
    frequency_number = 50,
    average_n_times = 4,
    correction = False,
    wait_for_steady = 0.1,
    bandwidth = BANDWIDTH.BW_5,
    E_range = E_RANGE.E_RANGE_10V,
    )

# create PEIS technique
peisTech_irCompensation = PEISTechnique(peisParams_irCompensation)

# create PEIS parameters
peisParams = PEISParams(
    vs_initial = False,
    initial_voltage_step = 0.0,
    duration_step = 0,
    record_every_dT = 0.5,
    record_every_dI = 0.01,
    final_frequency = 0.1,
    initial_frequency = 100000,
    sweep = SweepMode.Logarithmic,
    amplitude_voltage = 0.01,
    frequency_number = 60,
    average_n_times = 3,
    correction = False,
    wait_for_steady = 0.1,
    bandwidth = BANDWIDTH.BW_5,
    E_range = E_RANGE.E_RANGE_10V,
    )

# create PEIS technique
peisTech = PEISTechnique(peisParams)

# -----OCV-----
# create OCV parameters
ocvParams_30mins = OCVParams(
    rest_time_T = 1800,
    record_every_dT = 0.5,
    record_every_dE = 10,
    E_range = E_RANGE.E_RANGE_10V,
    bandwidth = BANDWIDTH.BW_5,
    )

# create OCV technique
ocvTech_30mins = OCVTechnique(ocvParams_30mins)

# create OCV parameters
ocvParams_15mins = OCVParams(
    rest_time_T = 900,
    record_every_dT = 0.5,
    record_every_dE = 10,
    E_range = E_RANGE.E_RANGE_10V,
    bandwidth = BANDWIDTH.BW_5,
    )

# create OCV technique
ocvTech_15mins = OCVTechnique(ocvParams_15mins)

# create OCV parameters
ocvParams_10mins = OCVParams(
    rest_time_T = 600,
    record_every_dT = 0.5,
    record_every_dE = 10,
    E_range = E_RANGE.E_RANGE_10V,
    bandwidth = BANDWIDTH.BW_5,
    )

# create OCV technique
ocvTech_10mins = OCVTechnique(ocvParams_10mins)

# create OCV parameters
ocvParams_10s = OCVParams(
    rest_time_T = 10,
    record_every_dT = 0.5,
    record_every_dE = 10,
    E_range = E_RANGE.E_RANGE_10V,
    bandwidth = BANDWIDTH.BW_5,
    )

# create OCV technique
ocvTech_10s = OCVTechnique(ocvParams_10s)

# -----CA-----
# make the only CA step
caStep = CAStep(
    voltage = -1.0,
    duration = 600,
    vs_initial = False
    )


# create CA parameters
caParams = CAParams(
    record_every_dT = 0.5,
    record_every_dI = 0.01,
    n_cycles = 0,
    steps = [caStep],
    I_range = I_RANGE.I_RANGE_10uA,
    )

# create CA technique
caTech = CATechnique(caParams)

# ----CPP-----
# create CPP parameters
cppParams = CPPParams(
    record_every_dEr = 10,
    rest_time_T = 1800,
    record_every_dTr = 0.5,
    vs_initial_scan = (True,True,True),
    voltage_scan = (-0.25, 1.5, -0.25),
    scan_rate = (0.01, 0.01, 0.01),
    I_pitting = 0.01,
    t_b = 10,
    record_every_dE = 0.01,
    average_over_dE = False,
    begin_measuring_I = 0.75,
    end_measuring_I = 1.0,
    record_every_dT = 0.5)

# create CPP technique
cppTech = CPPTechnique(cppParams)


boolTryToConnect = True
intAttempts_temp = 0
intMaxAttempts = 5

# initialize an empty dataframe to store the results
dfData = pd.DataFrame()

while boolTryToConnect and intAttempts_temp < intMaxAttempts:
    logging.info(f"Attempting to connect to the Biologic: {intAttempts_temp+1} / {intMaxAttempts}")

    try:
        # run all techniques
        with connect('USB0', force_load=True) as bl:
            channel = bl.get_channel(1)

            # make a way to track the techniques
            dicTechniqueTracker = {'strPreviousTechnique': None,
                                   'strCurrentTechnique': None,
                                   'intTechniqueIndex': None}

            # run all techniques
            runner = channel.run_techniques([peisTech_irCompensation,
                                         ocvTech_10mins,
                                         caTech,
                                         ocvTech_15mins,
                                         peisTech,
                                         cppTech,
                                         ocvTech_30mins,
                                         peisTech])

            for data_temp in runner:

                # if the type of the result is PEISData
                if isinstance(data_temp.data, PEISData):

                    # if process_index is 0
                    if data_temp.data.process_index == 0:
                        # check if this technique is not the same as the previous technique
                        if dicTechniqueTracker['strCurrentTechnique'] != 'PEISV':
                            # reinitialize the dataframe
                            dfData = pd.DataFrame()

                            # update the tracker
                            dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                            dicTechniqueTracker['strCurrentTechnique'] = 'PEISV'
                            dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                        # convert the data to a dataframe
                        dfData_p0_temp = pd.DataFrame(data_temp.data.process_data.to_json(), index=[0])
                        # add the dataframe to the
                        dfData = pd.concat([dfData, dfData_p0_temp], ignore_index=True)

                        # write the dataframe to a csv in the data folder
                        # join the path to the data folder to the current directory
                        strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEISV.csv')
                        # write the dataframe to a csv
                        dfData.to_csv(strDataPath)

                    # if process_index is 1
                    elif data_temp.data.process_index == 1:
                        # check if this technique is not the same as the previous technique
                        if dicTechniqueTracker['strCurrentTechnique'] != 'PEIS':
                            # reinitialize the dataframe
                            dfData = pd.DataFrame()

                            # update the tracker
                            dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                            dicTechniqueTracker['strCurrentTechnique'] = 'PEIS'
                            dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                        # convert the data to a dataframe
                        dfData_p1_temp = pd.DataFrame(data_temp.data.process_data.to_json(), index=[0])
                        # add the dataframe to the
                        dfData = pd.concat([dfData, dfData_p1_temp], ignore_index=True)

                        # write the dataframe to a csv in the data folder
                        # join the path to the data folder to the current directory
                        strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEIS.csv')
                        # write the dataframe to a csv
                        dfData.to_csv(strDataPath)


                # if the type of the result is OCVData
                elif isinstance(data_temp.data, OCVData):

                    # check if this technique is not the same as the previous technique
                    if dicTechniqueTracker['strCurrentTechnique'] != 'OCV':
                        # reinitialize the dataframe
                        dfData = pd.DataFrame()

                        # update the tracker
                        dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                        dicTechniqueTracker['strCurrentTechnique'] = 'OCV'
                        dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                    # convert the data to a dataframe
                    dfData_temp = pd.DataFrame(data_temp.data.to_json(), index=[0])
                    # add the dataframe to the
                    dfData = pd.concat([dfData, dfData_temp], ignore_index=True)

                    # write the dataframe to a csv in the data folder
                    # join the path to the data folder to the current directory
                    strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_OCV.csv')
                    # write the dataframe to a csv
                    dfData.to_csv(strDataPath)

                # if the type of the result is CAData
                elif isinstance(data_temp.data, CAData):

                    # check if this technique is not the same as the previous technique
                    if dicTechniqueTracker['strCurrentTechnique'] != 'CA':
                        # reinitialize the dataframe
                        dfData = pd.DataFrame()

                        # update the tracker
                        dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                        dicTechniqueTracker['strCurrentTechnique'] = 'CA'
                        dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                    # convert the data to a dataframe
                    dfData_temp = pd.DataFrame(data_temp.data.to_json(), index=[0])
                    # add the dataframe to the
                    dfData = pd.concat([dfData, dfData_temp], ignore_index=True)

                    # write the dataframe to a csv in the data folder
                    # join the path to the data folder to the current directory
                    strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_CA.csv')
                    # write the dataframe to a csv
                    dfData.to_csv(strDataPath)

                # if the type of the result is CPPData
                elif isinstance(data_temp.data, CPPData):

                    # check if this technique is not the same as the previous technique
                    if dicTechniqueTracker['strCurrentTechnique'] != 'CPP':
                        # reinitialize the dataframe
                        dfData = pd.DataFrame()

                        # update the tracker
                        dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                        dicTechniqueTracker['strCurrentTechnique'] = 'CPP'
                        dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                    # convert the data to a dataframe
                    dfData_temp = pd.DataFrame(data_temp.data.to_json(), index=[0])
                    # add the dataframe to the
                    dfData = pd.concat([dfData, dfData_temp], ignore_index=True)

                    # write the dataframe to a csv in the data folder
                    # join the path to the data folder to the current directory
                    strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_CPP.csv')
                    # write the dataframe to a csv
                    dfData.to_csv(strDataPath)

                # log the data
                logging.info(data_temp)
            else:
                time.sleep(1)

            # break the loop - successful connection
            boolTryToConnect = False

    except Exception as e:
        logging.error(f"Failed to connect to the Biologic: {e}")
        logging.info(f"Attempting again in 50 seconds")
        time.sleep(50)
        intAttempts_temp += 1
    return e


# log the end of the experiment
logging.info("End of electrochemical experiment")

# update the metadata file
dicMetadata['status'] = "completed"
dicMetadata['time'] = datetime.now().strftime("%H:%M:%S")
with open(strMetadataPath, 'w') as f:
    json.dump(dicMetadata, f)



#%%
# USE OPENTRONS INSTRUMENTS AND ARDUINO TO CLEAN ELECTRODE-----------------------------------------

# initialize an the arduino client
ac = Arduino() #arduino_search_string = "USB Serial")

# wash electrode
washElectrode(opentronsClient = oc,
              strLabwareName = strID_washStation,
              arduinoClient = ac)

# move to electrode tip rack
oc.moveToWell(strLabwareName = strID_electrodeTipRack,
              strWellName = 'A2',
              strPipetteName = 'p1000_single_gen2',
              strOffsetStart = 'top',
              fltOffsetX = 0.6,
              fltOffsetY = 0.5,
              intSpeed = 50)

# drop electrode tip
oc.dropTip(strLabwareName = strID_electrodeTipRack,
               strPipetteName = 'p1000_single_gen2',
               strWellName = 'A2',
               fltOffsetX = 0.6,
               fltOffsetY = 0.5,
               fltOffsetZ = 7,
               strOffsetStart = "bottom")

# close arduino
ac.disconnect()
# home robot
oc.homeRobot()
# turn the lights off
oc.lights(False)
# %%
