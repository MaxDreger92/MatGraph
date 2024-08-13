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
        if self.simulate:
            self.logger.info("Simulating Biologic Setup")
            return
        self.logger.info("Initializing Biologic Setup")
        with connect('USB0', force_load=True) as bl:
            self.connection = bl.get_channel(1)
        while self.boolTryToConnect and self.intAttempts_temp < self.intMaxAttempts:
            self.logger.info(f"Attempting to connect to the Biologic: {self.intAttempts_temp+1} / {self.intMaxAttempts}")

            try:
                # run all techniques
                with connect('USB0', force_load=True) as bl:
                    self.connection = bl.get_channel(1)
            except Exception as e:
                self.logger.error(f"Failed to connect to the Biologic: {e}")
                self.intAttempts_temp += 1
                time.sleep(5)
                return e

    def save_graph(self, **kwargs):
        # Save the graph to the database
        self.logger.info("Saving Biologic Setup")
        biologic = self.setup_model()
        biologic.save()
        if self.config['potentiostat']['location']['device'] == 'opentrons':
            opentrons_id = kwargs['opentrons']['opentrons_id']
            slot = self.config['potentiostat']['location']['properties']['slot']
            query = f"""
            MATCH (opentrons:Opentrons {{setup_id: '{opentrons_id}'}})-[:HAS_PART]->(slot:Slot {{number: {slot}}})
            RETURN slot
            """
            slot = db.cypher_query(query, resolve_objects=True)[0][0][0]
            print("SLOT: ", slot)
            biologic.slot.connect(slot)

    @property
    def info(self):
        return {
            "name_space": self.name_space,
            "biologic_config": self.config,
        }





