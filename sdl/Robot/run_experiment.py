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

from dotenv import load_dotenv

from mat2devplatform.settings import BASE_DIR
from opentrons import opentronsClient

# from ardu import Arduino
#
# from biologic import connect, BANDWIDTH, I_RANGE, E_RANGE
# from biologic.techniques.ocv import OCVTechnique, OCVParams, OCVData
# from biologic.techniques.peis import PEISTechnique, PEISParams, SweepMode, PEISData
# from biologic.techniques.ca import CATechnique, CAParams, CAStep, CAData
# from biologic.techniques.cpp import CPPTechnique, CPPParams, CPPData

import pandas as pd

from sdl.models import Opentron_Module, Opentron_O2


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
             intMoveSpeed: int = 100
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
        opentronsClient.moveToWell(strLabwareName=strLabwareName_from,
                                   strWellName=strWellName_from,
                                   strPipetteName=strPipetteName,
                                   strOffsetStart='top',
                                   fltOffsetX=fltOffsetX_from,
                                   fltOffsetY=fltOffsetY_from,
                                   intSpeed=intMoveSpeed)

        # aspirate 1000 uL
        opentronsClient.aspirate(strLabwareName=strLabwareName_from,
                                 strWellName=strWellName_from,
                                 strPipetteName=strPipetteName,
                                 intVolume=1000,
                                 strOffsetStart=strOffsetStart_from,
                                 fltOffsetX=fltOffsetX_from,
                                 fltOffsetY=fltOffsetY_from,
                                 fltOffsetZ=fltOffsetZ_from)

        # move to the well to dispense to
        opentronsClient.moveToWell(strLabwareName=strLabwareName_to,
                                   strWellName=strWellName_to,
                                   strPipetteName=strPipetteName,
                                   strOffsetStart='top',
                                   fltOffsetX=fltOffsetX_to,
                                   fltOffsetY=fltOffsetY_to,
                                   intSpeed=intMoveSpeed)

        # dispense 1000 uL
        opentronsClient.dispense(strLabwareName=strLabwareName_to,
                                 strWellName=strWellName_to,
                                 strPipetteName=strPipetteName,
                                 intVolume=1000,
                                 strOffsetStart=strOffsetStart_to,
                                 fltOffsetX=fltOffsetX_to,
                                 fltOffsetY=fltOffsetY_to,
                                 fltOffsetZ=fltOffsetZ_to)

        # subtract 1000 uL from the volume
        intVolume -= 1000


    # move to the well to aspirate from
    opentronsClient.moveToWell(strLabwareName=strLabwareName_from,
                               strWellName=strWellName_from,
                               strPipetteName=strPipetteName,
                               strOffsetStart='top',
                               fltOffsetX=fltOffsetX_from,
                               fltOffsetY=fltOffsetY_from,
                               intSpeed=intMoveSpeed)

    # aspirate the remaining volume
    opentronsClient.aspirate(strLabwareName=strLabwareName_from,
                             strWellName=strWellName_from,
                             strPipetteName=strPipetteName,
                             intVolume=intVolume,
                             strOffsetStart=strOffsetStart_from,
                             fltOffsetX=fltOffsetX_from,
                             fltOffsetY=fltOffsetY_from,
                             fltOffsetZ=fltOffsetZ_from)

    # move to the well to dispense to
    opentronsClient.moveToWell(strLabwareName=strLabwareName_to,
                               strWellName=strWellName_to,
                               strPipetteName=strPipetteName,
                               strOffsetStart='top',
                               fltOffsetX=fltOffsetX_to,
                               fltOffsetY=fltOffsetY_to,
                               intSpeed=intMoveSpeed)

    # dispense the remaining volume
    opentronsClient.dispense(strLabwareName=strLabwareName_to,
                             strWellName=strWellName_to,
                             strPipetteName=strPipetteName,
                             intVolume=intVolume,
                             strOffsetStart=strOffsetStart_to,
                             fltOffsetX=fltOffsetX_to,
                             fltOffsetY=fltOffsetY_to,
                             fltOffsetZ=fltOffsetZ_to)

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
    opentronsClient.moveToWell(strLabwareName=strLabwareName,
                               strWellName='A2',
                               strPipetteName='p1000_single_gen2',
                               strOffsetStart='top',
                               intSpeed=50)

    # move to wash station
    opentronsClient.moveToWell(strLabwareName=strLabwareName,
                               strWellName='A2',
                               strPipetteName='p1000_single_gen2',
                               strOffsetStart='bottom',
                               fltOffsetY=-15,
                               fltOffsetZ=-10,
                               intSpeed=50)

    arduinoClient.set_ultrasound_on(cartridge=0, time=30)

    # drain wash station
    arduinoClient.dispense_ml(pump=3, volume=16)

    # fill wash station with acid
    arduinoClient.dispense_ml(pump=5, volume=10)

    # move to wash station
    arduinoClient.set_ultrasound_on(cartridge=0, time=30)

    # drain wash station
    arduinoClient.dispense_ml(pump=3, volume=11)

    # fill wash station with Di water
    arduinoClient.dispense_ml(pump=4, volume=15)


    arduinoClient.set_ultrasound_on(cartridge=0, time=30)

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
    level=logging.DEBUG,                                                      # Can be changed to logging.INFO to see less
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(strLogFilePath, mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
from django.conf import settings
import json
import os
from jsonschema import validate, ValidationError, SchemaError

def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print(f"Validation successful for {json_data['metadata']['displayName']}")
    except ValidationError as e:
        print(f"Validation error: {e.message}")
    except SchemaError as e:
        print(f"Schema error: {e.message}")
#%%
# LOAD CONFIG FILES--------------------------------------------------------------------------------
settings.configure()
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Change the current working directory to the project root directory
os.chdir(project_root)

load_dotenv()
from neomodel import config

config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
print(config.DATABASE_URL)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
config_dir = os.path.join(strWD, 'config')
robot_config = json.load(open(os.path.join(config_dir, 'robot.json')))
labware_config = json.load(open(os.path.join(config_dir, 'labware.json')))
process_config = json.load(open(os.path.join(config_dir, 'process.json')))
experiment_config = json.load(open(os.path.join(config_dir, 'experiment.json')))

#%%
# INITIALIZE EXPERIMENT----------------------------------------------------------------------------
robotIP = robot_config["robotIP"]
# initialize an the opentrons client
oc = opentronsClient(strRobotIP=robotIP, dicHeaders=robot_config["headers"])

# get the current time
strTime_start = datetime.now().strftime("%H:%M:%S")

# experiment configuration
strWell2Test_autodialCell = experiment_config["wells"]["autodialCell"]
strWell2Test_vialRack = experiment_config["wells"]["vialRack"]
strRunNumber = experiment_config["runNumber"]

# get the current date
strDate = datetime.now().strftime("%Y%m%d")

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

# Load labware
# SDL = Opentron_O2(experiment_id=strExperimentID, date_added=strDate)
# SDL.save()
schema = json.load(open(os.path.join(BASE_DIR, 'sdl', 'Robot', 'config', 'labware', 'schemas', 'labware_schema.json')))
for lw in labware_config["labware"]:
    if lw['namespace'] == 'opentrons':
        continue
    # print(lw)
    with open(f"{os.path.join(BASE_DIR, 'sdl', 'Robot','config',  'labware')}/{lw['filename']}") as f:
        json_file = json.load(f)
        validate_json(json_file, schema)
        # print(json_file)
    # print("miau")

    # oc.loadLabware(intSlot=lw["slot"], strLabwareName=lw["name"], strNamespace=lw["namespace"], intVersion=lw["version"], strIntent=lw["intent"])
    #
    #
    # module = Opentron_Module.from_json(json_file)
    # print("miayu", SDL.slots.all)
    # print(SDL.slots)
    #
    # module.add_slot(strExperimentID, lw["slot"])

# # Load custom labware
# for custom_lw in ["vialRack", "washStation", "autodialCell", "dIBeaker", "NISreactor", "electrodeTipRack"]:
#     labware_path = labware_config[custom_lw]["path"]
#     labware_slot = labware_config[custom_lw]["slot"]
#     with open(labware_path) as f:
#         dicCustomLabware_temp = json.load(f)
#     oc.loadCustomLabware(dicLabware=dicCustomLabware_temp, intSlot=labware_slot)

# LOAD OPENTRONS STANDARD INSTRUMENTS--------------------------------------------------------------
# Pipettes are loaded with labware now









#%%
# MOVE OPENTRONS INSTRUMENTS-----------------------------------------------------------------------

# turn the lights on
# oc.lights(True)
#
# # home robot
# oc.homeRobot()

# -----USE OPENTRONS TO MOVE CORROSIVE SOLUTIONS-----
# move to pipette tip rack
# oc.moveToWell(strLabwareName=labware_config["pipetteTipRack"]["name"],
#               strWellName='A1',
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetY=1,
#               intSpeed=100)
# # pick up pipette tip
# oc.pickUpTip(strLabwareName=labware_config["pipetteTipRack"]["name"],
#              strPipetteName='p1000_single_gen2',
#              strWellName='A1',
#              fltOffsetY=1)
#
# fillWell(opentronsClient=oc,
#          **process_config["fillWellParams"],
#          strLabwareName_to=labware_config["autodialCell"]["slot"],
#          strWellName_to=strWell2Test_autodialCell)
#
# # move back to pipette tip rack
# oc.moveToWell(strLabwareName=labware_config["pipetteTipRack"]["name"],
#               strWellName='A1',
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetY=1,
#               intSpeed=100)
# # drop pipette tip
# oc.dropTip(strLabwareName=labware_config["pipetteTipRack"]["name"],
#            strPipetteName='p1000_single_gen2',
#            strWellName='A1',
#            strOffsetStart='bottom',
#            fltOffsetY=1,
#            fltOffsetZ=7)
#
# # move to the other tip in the pipette tip rack
# oc.moveToWell(strLabwareName=labware_config["pipetteTipRack"]["name"],
#               strWellName='A12',
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetY=1,
#               intSpeed=100)
# # pick up pipette tip
# oc.pickUpTip(strLabwareName=labware_config["pipetteTipRack"]["name"],
#              strPipetteName='p1000_single_gen2',
#              strWellName='A12',
#              fltOffsetY=1)
#
# fillWell(opentronsClient=oc,
#          **process_config["fillWellParams"],
#          strLabwareName_from=labware_config["dIBeaker"]["slot"],
#          strWellName_from='A1',
#          strLabwareName_to=labware_config["autodialCell"]["slot"],
#          strWellName_to=strWell2Test_autodialCell,
#          intVolume=3600)
#
# # move to the other tip in the pipette tip rack
# oc.moveToWell(strLabwareName=labware_config["pipetteTipRack"]["name"],
#               strWellName='A12',
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetY=1,
#               intSpeed=100)
# # drop pipette tip
# oc.dropTip(strLabwareName=labware_config["pipetteTipRack"]["name"],
#            strPipetteName='p1000_single_gen2',
#            strWellName='A12',
#            strOffsetStart='bottom',
#            fltOffsetY=1,
#            fltOffsetZ=7)
#
# # -----USE OPENTRONS TO MOVE ELECTRODES-----
#
# # move to electrode tip rack
# oc.moveToWell(strLabwareName=labware_config["electrodeTipRack"]["slot"],
#               strWellName='A2',
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetX=0.6,
#               fltOffsetY=0.5,
#               fltOffsetZ=3,
#               intSpeed=100)
# # pick up electrode tip
# oc.pickUpTip(strLabwareName=labware_config["electrodeTipRack"]["slot"],
#              strPipetteName='p1000_single_gen2',
#              strWellName='A2',
#              fltOffsetX=0.6,
#              fltOffsetY=0.5)
#
# # move to top only!!
# oc.moveToWell(strLabwareName=labware_config["autodialCell"]["slot"],
#               strWellName=strWell2Test_autodialCell,
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetX=0.5,
#               fltOffsetY=0.5,
#               fltOffsetZ=5,
#               intSpeed=50)
#
# # move to autodial cell
# oc.moveToWell(strLabwareName=labware_config["autodialCell"]["slot"],
#               strWellName=strWell2Test_autodialCell,
#               strPipetteName='p1000_single_gen2',
#               strOffsetStart='top',
#               fltOffsetX=0.5,
#               fltOffsetY=0.5,
#               fltOffsetZ=-25,
#               intSpeed=50)
#
# #%%
# # RUN ELECTROCHEMICAL EXPERIMENT-------------------------------------------------------------------

# -----PEIS-----
# create PEIS parameters
# peisParams_irCompensation = PEISParams(**experiment_config["PEIS"])
#
# # create PEIS technique
# peisTech_irCompensation = PEISTechnique(peisParams_irCompensation)
#
# # create PEIS parameters
# peisParams = PEISParams(**experiment_config["PEIS"])
#
# # create PEIS technique
# peisTech = PEISTechnique(peisParams)
#
# # -----OCV-----
# # create OCV parameters
# ocvParams_30mins = OCVParams(**experiment_config["OCV"])
#
# # create OCV technique
# ocvTech_30mins = OCVTechnique(ocvParams_30mins)
#
# # create OCV parameters
# ocvParams_15mins = OCVParams(**experiment_config["OCV"])
#
# # create OCV technique
# ocvTech_15mins = OCVTechnique(ocvParams_15mins)
#
# # create OCV parameters
# ocvParams_10mins = OCVParams(**experiment_config["OCV"])
#
# # create OCV technique
# ocvTech_10mins = OCVTechnique(ocvParams_10mins)
#
# # create OCV parameters
# ocvParams_10s = OCVParams(**experiment_config["OCV"])
#
# # create OCV technique
# ocvTech_10s = OCVTechnique(ocvParams_10s)
#
# # -----CA-----
# # make the only CA step
# caStep = CAStep(**experiment_config["CA"])
#
# # create CA parameters
# caParams = CAParams(steps=[caStep], **experiment_config["CA"])
#
# # create CA technique
# caTech = CATechnique(caParams)
#
# # ----CPP-----
# # create CPP parameters
# cppParams = CPPParams(**experiment_config["CPP"])
#
# # create CPP technique
# cppTech = CPPTechnique(cppParams)
#
#
# boolTryToConnect = True
# intAttempts_temp = 0
# intMaxAttempts = 5
#
# # initialize an empty dataframe to store the results
# dfData = pd.DataFrame()
#
# while boolTryToConnect and intAttempts_temp < intMaxAttempts:
#     logging.info(f"Attempting to connect to the Biologic: {intAttempts_temp+1} / {intMaxAttempts}")
#
#     try:
#         # run all techniques
#         with connect('USB0', force_load=True) as bl:
#             channel = bl.get_channel(1)
#
#             # make a way to track the techniques
#             dicTechniqueTracker = {'strPreviousTechnique': None,
#                                    'strCurrentTechnique': None,
#                                    'intTechniqueIndex': None}
#
#             # run all techniques
#             runner = channel.run_techniques([peisTech_irCompensation,
#                                              ocvTech_10mins,
#                                              caTech,
#                                              ocvTech_15mins,
#                                              peisTech,
#                                              cppTech,
#                                              ocvTech_30mins,
#                                              peisTech])
#
#             for data_temp in runner:
#
#                 # if the type of the result is PEISData
#                 if isinstance(data_temp.data, PEISData):
#
#                     # if process_index is 0
#                     if data_temp.data.process_index == 0:
#                         # check if this technique is not the same as the previous technique
#                         if dicTechniqueTracker['strCurrentTechnique'] != 'PEISV':
#                             # reinitialize the dataframe
#                             dfData = pd.DataFrame()
#
#                             # update the tracker
#                             dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
#                             dicTechniqueTracker['strCurrentTechnique'] = 'PEISV'
#                             dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index
#
#                         # convert the data to a dataframe
#                         dfData_p0_temp = pd.DataFrame(data_temp.data.process_data.to_json(), index=[0])
#                         # add the dataframe to the
#                         dfData = pd.concat([dfData, dfData_p0_temp], ignore_index=True)
#
#                         # write the dataframe to a csv in the data folder
#                         # join the path to the data folder to the current directory
#                         strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEISV.csv')
#                         # write the dataframe to a csv
#                         dfData.to_csv(strDataPath)
#
#                     # if process_index is 1
#                     elif data_temp.data.process_index == 1:
#                         # check if this technique is not the same as the previous technique
#                         if dicTechniqueTracker['strCurrentTechnique'] != 'PEIS':
#                             # reinitialize the dataframe
#                             dfData = pd.DataFrame()
#
#                             # update the tracker
#                             dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
#                             dicTechniqueTracker['strCurrentTechnique'] = 'PEIS'
#                             dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index
#
#                         # convert the data to a dataframe
#                         dfData_p1_temp = pd.DataFrame(data_temp.data.process_data.to_json(), index=[0])
#                         # add the dataframe to the
#                         dfData = pd.concat([dfData, dfData_p1_temp], ignore_index=True)
#
#                         # write the dataframe to a csv in the data folder
#                         # join the path to the data folder to the current directory
#                         strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEIS.csv')
#                         # write the dataframe to a csv
#                         dfData.to_csv(strDataPath)
#
#
#                 # if the type of the result is OCVData
#                 elif isinstance(data_temp.data, OCVData):
#
#                     # check if this technique is not the same as the previous technique
#                     if dicTechniqueTracker['strCurrentTechnique'] != 'OCV':
#                         # reinitialize the dataframe
#                         dfData = pd.DataFrame()
#
#                         # update the tracker
#                         dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
#                         dicTechniqueTracker['strCurrentTechnique'] = 'OCV'
#                         dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index
#
#                     # convert the data to a dataframe
#                     dfData_temp = pd.DataFrame(data_temp.data.to_json(), index=[0])
#                     # add the dataframe to the
#                     dfData = pd.concat([dfData, dfData_temp], ignore_index=True)
#
#                     # write the dataframe to a csv in the data folder
#                     # join the path to the data folder to the current directory
#                     strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_OCV.csv')
#                     # write the dataframe to a csv
#                     dfData.to_csv(strDataPath)
#
#                 # if the type of the result is CAData
#                 elif isinstance(data_temp.data, CAData):
#
#                     # check if this technique is not the same as the previous technique
#                     if dicTechniqueTracker['strCurrentTechnique']
#                         ...


