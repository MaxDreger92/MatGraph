import time

from neomodel import db

from sdl.models import Biologic, Opentrons
from sdl.setup.ExperimentalSetup import SDLSetup
from biologic import connect


class BiologicSetup(SDLSetup):
    def __init__(self, config_source, logger, model=Biologic, *args, **kwargs):
        super().__init__(config_source=config_source, model=model)
        self.logger = logger
        self.name_space = "biologic"
        self.boolTryToConnect = True
        self.intAttempts_temp = 0
        self.intMaxAttempts = 5



    def setup_sdl(self):
        # if self.simulate:
        #     self.logger.info("Simulating Biologic Setup")
        #     return
        #
        # self.logger.info("Initializing Biologic Setup")
        #
        # while self.boolTryToConnect and self.intAttempts_temp < self.intMaxAttempts:
        #     self.logger.info(f"Attempting to connect to the Biologic: {self.intAttempts_temp + 1} / {self.intMaxAttempts}")
        #
        #     try:
        #         with connect('USB0', force_load=True) as bl:
        #             self.connection = bl.get_channel(1)
        #             # Run the experiment after a successful connection
        #             self.logger.info("Experiment started successfully.")
        #
        #             # If successful, break out of the loop
        #             self.boolTryToConnect = False
        #             break
        #     except Exception as e:
        #         self.logger.error(f"Failed to connect to the Biologic: {e}")
        #         self.intAttempts_temp += 1
        #         time.sleep(5)
        pass

    def save_graph(self, **kwargs):
        # Save the graph to the database
        self.logger.info("Saving Biologic Setup")
        self.setup_node = self.setup_model()
        self.setup_node.setup_id = self.setup_node.uid

        self.setup_node.save()
        if self.config['potentiostat']['location']['device'] == 'opentrons':
            opentrons_id = kwargs['opentrons']['opentrons_id']
            slot = self.config['potentiostat']['location']['properties']['slot']
            query = f"""
            MATCH (opentrons:Opentrons {{setup_id: '{opentrons_id}'}})-[:HAS_PART]->(slot:Slot {{number: '{slot}'}})
            RETURN slot
            """
            slot = db.cypher_query(query, resolve_objects=True)[0][0][0]
            print("SLOT: ", slot)
            self.setup_node.slot.connect(slot)

    @property
    def info(self):
        return {
            "name_space": self.name_space,
            "biologic_config": self.config,
            "biologic_id": getattr(self, 'setup_node', None).setup_id if hasattr(self, 'setup_node') else None
        }





