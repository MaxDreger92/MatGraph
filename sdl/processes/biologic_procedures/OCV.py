from biologic.biologic.techniques.ocv import OCVParams, OCVTechnique

from sdl.processes.biologic_utils import BiologicBaseProcedure


class OCV(BiologicBaseProcedure[OCVParams]):
    technique_cls = OCVTechnique