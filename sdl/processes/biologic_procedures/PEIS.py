import os

import pandas as pd
from biologic.biologic.techniques.peis import PEISParams, PEISTechnique, PEISData

from sdl.processes.biologic_utils import BiologicBaseProcedure


class PEIS(BiologicBaseProcedure[PEISParams]):
    technique_cls = PEISTechnique
    strExperimentPath = './'

    
    def to_csv(self):
        # if the type of the result is PEISData
        if isinstance(self.runner.data, PEISData):
            dicTechniqueTracker = {'strPreviousTechnique': None,
                                   'strCurrentTechnique': None,
                                   'intTechniqueIndex': None}

            # if process_index is 0
            if self.runner.data.process_index == 0:
                # check if this technique is not the same as the previous technique
                if dicTechniqueTracker['strCurrentTechnique'] != 'PEISV':
                    # reinitialize the dataframe
                    dfData = pd.DataFrame()

                    # update the tracker
                    dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                    dicTechniqueTracker['strCurrentTechnique'] = 'PEISV'
                    dicTechniqueTracker['intTechniqueIndex'] = self.runner.tech_index

                # convert the data to a dataframe
                dfData_p0_temp = pd.DataFrame(self.runner.data.process_data.to_json(), index=[0])
                # add the dataframe to the
                dfData = pd.concat([dfData, dfData_p0_temp], ignore_index=True)

                # write the dataframe to a csv in the data folder
                # join the path to the data folder to the current directory
                strDataPath = os.path.join(self.strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEISV.csv')
                # write the dataframe to a csv
                dfData.to_csv(strDataPath)

            # if process_index is 1
            elif self.runner.data.process_index == 1:
                # check if this technique is not the same as the previous technique
                if dicTechniqueTracker['strCurrentTechnique'] != 'PEIS':
                    # reinitialize the dataframe
                    dfData = pd.DataFrame()

                    # update the tracker
                    dicTechniqueTracker['strPreviousTechnique'] = dicTechniqueTracker['strCurrentTechnique']
                    dicTechniqueTracker['strCurrentTechnique'] = 'PEIS'
                    dicTechniqueTracker['intTechniqueIndex'] = self.runner.tech_index

                # convert the data to a dataframe
                dfData_p1_temp = pd.DataFrame(self.runner.data.process_data.to_json(), index=[0])
                # add the dataframe to the
                dfData = pd.concat([dfData, dfData_p1_temp], ignore_index=True)

                # write the dataframe to a csv in the data folder
                # join the path to the data folder to the current directory
                strDataPath = os.path.join(strExperimentPath, f'{strExperimentID}_{dicTechniqueTracker["intTechniqueIndex"]}_PEIS.csv')
                # write the dataframe to a csv
                dfData.to_csv(strDataPath)