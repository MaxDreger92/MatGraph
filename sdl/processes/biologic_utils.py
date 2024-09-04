import os
import time
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import TypeVar, Generic

import pandas as pd
from biologic.runner import IndexData
from biologic.technique import Technique
from biologic.params import TechniqueParams
from biologic.techniques.ca import CAData
from biologic.techniques.cpp import CPPData
from biologic.techniques.ocv import OCVData
from biologic import connect
from biologic.techniques.peis import PEISData

from mat2devplatform.settings import BASE_DIR
from matgraph.models.processes import Measurement
from matgraph.models.properties import Property
from sdl.models import Biologic
from sdl.processes.utils import ProcessOutput
from sdl.workflow.utils import BaseProcedure

P = TypeVar('P', bound=TechniqueParams)

class BiologicDataHandler:

    def handle_data(self, runner, experiment_id, experiment_path):
        dicTechniqueTracker = {'strPreviousTechnique': None,
                               'strCurrentTechnique': None,
                               'intTechniqueIndex': None}
        print(experiment_path)
        dfData = pd.DataFrame()

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
                    strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_PEISV.csv')
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
                    strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_PEIS.csv')
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
                strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_OCV.csv')
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
                strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_CA.csv')
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
                strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_CPP.csv')
                # write the dataframe to a csv
                dfData.to_csv(strDataPath)


class BiologicBaseProcedure(BaseProcedure, Generic[P], BiologicDataHandler):
    technique_cls=  Technique

    def __init__(self, params: P):
        self.params = params
        self.technique = self.technique_cls(params)
        self.boolTryToConnect = True
        self.intMaxAttempts = 5
        self.saving_path = BASE_DIR




    def execute(self, *args, **kwargs):
        time_started = datetime.now()
        logger = kwargs.get("logger")
        self.intAttempts_temp = 0
        while self.boolTryToConnect and self.intAttempts_temp < self.intMaxAttempts:
            logger.info(f"Attempting to connect to the Biologic: {self.intAttempts_temp + 1} / {self.intMaxAttempts}")

            try:
                with connect('USB0', force_load=True) as bl:
                    channel = bl.get_channel(1)
                    # Run the experiment after a successful connection
                    logger.info("Experiment started successfully.")
                    runner = channel.run_techniques([self.technique])
                    experiment_id = kwargs["experiment_id"]
                    experiment_directory = kwargs["experiment_directory"]
                    self.handle_data(runner, experiment_id, experiment_directory )

                    # If successful, break out of the loop
                    for data_temp in runner:
                        print(data_temp)
                    self.boolTryToConnect = False
            except Exception as e:
                logger.error(f"Failed to connect to the Biologic: {e}")
                self.intAttempts_temp += 1
                time.sleep(5)


        time_ended = datetime.now()
        self.store_csv(runner, **kwargs)
        self.store_graph(runner, time_started= time_started, time_ended = time_ended, **kwargs)
        data = {"output" :[{
            data_key: data_value for data_key, data_value in index_data.data.__dict__.items()
        } for index_data in runner]}
        return ProcessOutput(output=data, input=asdict(self.params))


    def store_graph(self, runner, **kwargs):
        # Check if Property node already exists for the experiment, otherwise create it
        data = [{
            data_key: data_value for data_key, data_value in index_data.data.__dict__.items()
        } for index_data in runner]
        df = pd.DataFrame(data)
        experiment_id = kwargs["experiment_id"]


        # Create Measurement node

        time_started = kwargs["time_started"]
        time_ended = kwargs["time_ended"]

        measurement_node = Measurement(
            time_started=time_started,
            time_ended= time_ended,
            run_id = experiment_id,
        ).save()

        property_node = Property(
            dataframe_json = df.to_json(orient='records')
        ).save()

        # Create relationship from Property to Measurement
        measurement_node.property_output.connect(property_node)
        biologic_setup = Biologic.nodes.get(uid = kwargs["biologic_id"])
        measurement_node.researcher.connect(biologic_setup)



