from biologic.techniques.ca import CAParams, CATechnique

from sdl.processes.biologic_utils import BiologicBaseProcedure


class CA(BiologicBaseProcedure[CAParams]):
    technique_cls = CATechnique
    name = "CA"

    def __str__(self):
        return self.name

