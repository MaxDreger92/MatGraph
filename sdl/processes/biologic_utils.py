import os
import time
import uuid
from dataclasses import asdict, fields
from datetime import datetime
from enum import Enum
from typing import TypeVar, Generic

import pandas as pd
from biologic.technique import Technique
from biologic.params import TechniqueParams
from biologic.techniques.ca import CAData
from biologic.techniques.cpp import CPPData
from biologic.techniques.ocv import OCVData
from biologic import connect
from biologic.techniques.peis import PEISData
from sdl.processes.utils import ProcessOutput

from mat2devplatform.settings import BASE_DIR
from matgraph.models.processes import Measurement
from matgraph.models.properties import Property, Parameter
from sdl.models import Biologic
from sdl.processes.utils import ProcessOutput
from sdl.workflow.utils import BaseProcedure

P = TypeVar('P', bound=TechniqueParams)

class BiologicDataHandler:

    def handle_data(self, runner, experiment_path, techniques, **kwargs):

        def custom_asdict(obj):
            if not hasattr(obj, '__dataclass_fields__'):
                return obj  # Return the object directly if it’s not a dataclass

            result = {}
            for field in fields(obj):
                value = getattr(obj, field.name)
                if isinstance(value, Enum):
                    result[field.name] = value.value  # Convert Enums to their value
                elif hasattr(value, '__dataclass_fields__'):
                    result[field.name] = custom_asdict(value)  # Recursively handle nested dataclasses
                else:
                    result[field.name] = value
            return result

        dicTechniqueTracker = {
            'strPreviousTechnique': None,
            'strCurrentTechnique': None,
            'intTechniqueIndex': None
        }
        experiment_id = kwargs.get('experiment_id')

        # To gather data for storing in the graph
        gathered_data = []
        outputs = []
        technique_index = 0
        current_technique = None

        for data_temp in runner:
            data_type = None
            time_value = getattr(data_temp.data, 'time', None)

            # Determine the type of data (technique)
            if isinstance(data_temp.data, PEISData):
                data_type = 'PEISV' if data_temp.data.process_index == 0 else 'PEIS'
            elif isinstance(data_temp.data, OCVData):
                data_type = 'OCV'
            elif isinstance(data_temp.data, CAData):
                data_type = 'CA'
            elif isinstance(data_temp.data, CPPData):
                data_type = 'CPP'

            if data_type:
                # Check if the current technique is different from the previous technique
                if dicTechniqueTracker['strCurrentTechnique'] != data_type:
                    # Update the tracker
                    dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                    dicTechniqueTracker['strCurrentTechnique'] = data_type
                    dicTechniqueTracker['intTechniqueIndex'] = data_temp.tech_index

                # Check if time has reset to '00'
                if time_value == 0.0 and len(gathered_data) != 0:
                    print("Processing gathered data")
                    # Process the gathered data as one JSON and store in the graph
                    uid = str(uuid.uuid4())
                    input_data = custom_asdict(techniques[technique_index].param_values)
                    current_technique = data_type
                    self.process_gathered_data(gathered_data, input_data, current_technique, experiment_path, uid, **kwargs)

                    # Save the gathered data to CSV
                    dfData = pd.concat(gathered_data, ignore_index=True)  # Combine the gathered data
                    strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_{data_type}_{str(technique_index)}.csv')
                    dfData.to_csv(strDataPath, index=False)

                    gathered_data = []  # Reset the gathered data
                    output = ProcessOutput(id=uid, status="success", output={"data": gathered_data}, input=input_data)
                    outputs.append(output)
                    technique_index += 1

                # Append the current data to gathered data
                dfData_temp = pd.DataFrame(data_temp.data.to_json(), index=[0])
                gathered_data.append(dfData_temp)

        # Process any remaining gathered data
        if len(gathered_data) != 0:
            print("Processing remaining gathered data")
            uid = str(uuid.uuid4())
            input_data = custom_asdict(techniques[technique_index].param_values)
            self.process_gathered_data(gathered_data, input_data, current_technique, experiment_path, uid, **kwargs)

            # Save the remaining data to CSV
            dfData = pd.concat(gathered_data, ignore_index=True)
            strDataPath = os.path.join(experiment_path, f'{experiment_id}_{dicTechniqueTracker["intTechniqueIndex"]}_{current_technique}_{str(technique_index)}.csv')
            dfData.to_csv(strDataPath, index=False)

            output = ProcessOutput(id=uid, status="success", output={"data": gathered_data}, input=input_data)
            outputs.append(output)

        return outputs

    def process_gathered_data(self, gathered_data, input_data, data_type, experiment_path, uid, **kwargs):
        """
        Process the gathered data as one JSON and store it in the graph.
        """
        if not gathered_data:
            return
        experiment_id = kwargs.get('experiment_id')

        # Concatenate all data in the gathered list to a single DataFrame
        df_gathered = pd.concat(gathered_data, ignore_index=True)

        # Convert the gathered data to JSON
        gathered_json = df_gathered.to_json(orient='records')

        # Prepare the graph data for the gathered data
        graph_data = {
            'id': uid,
            'technique': data_type,
            'data': gathered_json,
            'input': input_data
        }

        # Store the current measurement in the graph
        self.store_graph(graph_data, **kwargs)

    def store_graph(self, graph_data, **kwargs):
        """
        Store the experiment data in the graph database, including Measurement and Property nodes.
        One node per measurement technique.
        """
        time_started = self.time_started
        time_ended = self.time_ended
        experiment_id = kwargs.get('experiment_id')
        biologic_id = kwargs.get('biologic').get('biologic_id')
        uid = graph_data['id']

        # Create a Measurement node for each technique
        measurement_node = Measurement(
            time_started=time_started,
            time_ended=time_ended,
            run_id=experiment_id,
            uid = uid,
            name=graph_data['technique']
        ).save()
        print("Measurement node created", uid)

        # Store the corresponding Property node for each technique
        property_node = Property(
            dataframe_json=graph_data['data']
        ).save()
        for key, value in graph_data['input'].items():
            parameter =  Parameter(
                name = key,
                value = value
            ).save()
            measurement_node.parameter.connect(parameter)

        # Connect the Property node to the Measurement node
        measurement_node.property_output.connect(property_node)

        # Connect the Measurement node to the Biologic setup
        biologic_setup = Biologic.nodes.get(uid=biologic_id)
        measurement_node.researcher.connect(biologic_setup)

class BiologicBaseProcedure(BaseProcedure, Generic[P], BiologicDataHandler):
    technique_cls=  Technique

    def __init__(self, params: P):
        self.params = params
        self.technique = self.technique_cls(params)
        self.boolTryToConnect = True
        self.intMaxAttempts = 5
        self.saving_path = BASE_DIR




    def execute(self, *args, **kwargs):
        self.time_started = datetime.now()
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


                    self.boolTryToConnect = False
            except Exception as e:
                logger.error(f"Failed to connect to the Biologic: {e}")
                self.intAttempts_temp += 1
                time.sleep(5)


        self.time_ended = datetime.now()
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



