from biologic.biologic.techniques.cpp import CPPParams, CPPTechnique

from sdl.processes.biologic_utils import BiologicBaseProcedure


class CPP(BiologicBaseProcedure[CPPParams]):
    technique_cls = CPPTechnique