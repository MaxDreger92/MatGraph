from biologic.techniques.ocv import OCVParams, OCVTechnique

from sdl.processes.biologic_utils import BiologicBaseProcedure


class OCV(BiologicBaseProcedure[OCVParams]):
    technique_cls = OCVTechnique

    name = "OCV"

    def __str__(self):
        return self.name