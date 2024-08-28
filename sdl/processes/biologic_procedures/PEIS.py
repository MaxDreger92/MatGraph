from biologic.techniques.peis import PEISTechnique, PEISParams

from sdl.processes.biologic_utils import BiologicBaseProcedure


class PEIS(BiologicBaseProcedure[PEISParams]):
    technique_cls = PEISTechnique
    name = "PEIS"

    def __str__(self):
        return self.name