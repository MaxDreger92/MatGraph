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
from biologic.techniques.ocv import OCVData

from mat2devplatform.settings import BASE_DIR
from matgraph.models.processes import Measurement
from matgraph.models.properties import Property
from sdl.models import Biologic
from sdl.processes.utils import ProcessOutput
from sdl.workflow.utils import BaseProcedure

P = TypeVar('P', bound=TechniqueParams)

class BiologicBaseProcedure(BaseProcedure, Generic[P]):
    technique_cls=  Technique
    def __init__(self, params: P):
        self.params = params
        self.technique = self.technique_cls(params)
        self.boolTryToConnect = True
        self.intMaxAttempts = 5
        self.saving_path = BASE_DIR


    def execute(self, *args, **kwargs):
        # logger = kwargs.get("logger")
        # self.intAttempts_temp = 0
        # while self.boolTryToConnect and self.intAttempts_temp < self.intMaxAttempts:
        #     logger.info(f"Attempting to connect to the Biologic: {self.intAttempts_temp + 1} / {self.intMaxAttempts}")
        #
        #     try:
        #         with connect('USB0', force_load=True) as bl:
        #             channel = bl.get_channel(1)
        #             # Run the experiment after a successful connection
        #             logger.info("Experiment started successfully.")
        #             runner = channel.run_techniques([self.technique])
        #
        #             # If successful, break out of the loop
        #             for data_temp in runner:
        #                 print(data_temp)
        #             self.boolTryToConnect = False
        #     except Exception as e:
        #         logger.error(f"Failed to connect to the Biologic: {e}")
        #         self.intAttempts_temp += 1
        #         time.sleep(5)
        time_started = datetime.fromtimestamp(time.time())
        process_id = uuid.uuid4()
        runner = [
            IndexData(tech_index=0, data=OCVData(time=0.4999999873689376, total_time=0.4999999873689376, Ewe=0.00036612385883927345, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=0.9999999747378752, total_time=0.9999999747378752, Ewe=-0.0009172508725896478, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=1.4999999621068127, total_time=1.4999999621068127, Ewe=0.00036612385883927345, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=1.9999999494757503, total_time=1.9999999494757503, Ewe=0.00036612385883927345, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=2.499999936844688, total_time=2.499999936844688, Ewe=-0.000596407160628587, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=2.9999999242136255, total_time=2.9999999242136255, Ewe=0.001007811282761395, Ece=None)),
            IndexData(tech_index=0, data=OCVData(time=3.499999911582563, total_time=3.499999911582563, Ewe=-0.0009172508725896478, Ece=None))
        ]
        time_ended = datetime.fromtimestamp(time.time())



        self.store_csv(runner, **kwargs)
        self.store_graph(runner, time_started= time_started, time_ended = time_ended, **kwargs)
        data = {"output" :[{
            data_key: data_value for data_key, data_value in index_data.data.__dict__.items()
        } for index_data in runner]}
        return ProcessOutput(output=data, input=asdict(self.params))


    def store_csv(self, runner, **kwargs):
        # Prepare the data for the DataFrame
        data = [{
            data_key: data_value for data_key, data_value in index_data.data.__dict__.items()
        } for index_data in runner]
        df = pd.DataFrame(data)

        # Retrieve the experiment ID

        experiment_id = kwargs["experiment_id"]


        # Create the base CSV file path
        base_csv_file_path = os.path.join(self.saving_path, str(experiment_id), str(self.technique_cls.__name__) + ".csv")

        # Initialize the final file path
        csv_file_path = base_csv_file_path
        # Check if the file already exists, and if so, create a new name with incremented suffix
        counter = 1
        while os.path.exists(csv_file_path):
            file_name, file_extension = os.path.splitext(base_csv_file_path)
            csv_file_path = f"{file_name}_{counter}{file_extension}"
            counter += 1

        # Print the final CSV file path
        print("CSV FILE PATH: ", csv_file_path)

        # Save the DataFrame to the CSV file
        df.to_csv(csv_file_path, index=False)

        return csv_file_path

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



