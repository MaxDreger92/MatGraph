from uuid import UUID
import os
# TODO implement filtering for values!
QUERY_BY_VALUE = """"""
from matching.matcher import Matcher
from dbcommunication.ai.searchEmbeddings import EmbeddingSearch
from matgraph.models.ontology import *
class FabricationWorkflowMatcher(Matcher):

    type = 'job'

    def __init__(self, workflow_dict, count=False, **kwargs):
        materials_search = EmbeddingSearch(EMMOMatter)
        process_search = EmbeddingSearch(EMMOProcess)
        self.educt = [materials_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOMatter']['educt']]]
        self.product = [materials_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOMatter']['product']]]
        self.materials = [materials_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOMatter']['intermediates']]]
        self.processes = [process_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOProcess']]]
        self.parameters = [process_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOQuantity']]]
        self.count = count
        super().__init__(**kwargs)


    def build_query(self):
        query = '''
        MATCH (emmo_educt:EMMOMatter),
              (emmo_product:EMMOMatter)

        WHERE emmo_educt.uid IN $educt 
            AND emmo_product.uid IN $product 

              
        WITH collect(emmo_educt) as educt,
             collect(emmo_product) as product

        
        CALL apoc.path.expandConfig(educt, {
                relationshipFilter: "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT|IS_MEASUREMENT_INPUT|HAS_PROPERTY|HAS_MEASUREMENT_OUTPUT|<IS_A",
            labelFilter: "Manufacturing|Matter|Measurement|Property|EMMOMatter|EMMOProcess|EMMOQuantity",
            minLevel: 0,
            maxLevel: 10,
            limit: 10,
            endNode: [product]
        })
        YIELD path
        RETURN path
        '''


        params= {
            'educt': self.educt,
            'product': self.product,
            'intermediates': self.materials,
            'processes': self.processes,
            'parameters': self.parameters
        }
        return query, params

    def build_result(self):

        if self.count:
            return self.db_results[0][0]
        pass

    def build_results_for_report(self):
        return self.db_result[0][0], self.db_columns


    def build_extra_reports(self):
        pass


def main():

    workflow_dict = {
        'nodes':  {
            'EMMOMatter': {
                'educt':[
                    {'id': 1, 'name': "Platinum Catalyst"},
                    {'id': 3, 'name': "Ethanol"}
                ],
                'intermediates': [],
                'product': [
                    {'id': 5, 'name': "CatalystInk"}
                ]},
            'EMMOProcess': [
                {'id': 2, 'name': "Fabrication"}
            ]
        },
        'relationships': {'IS_MANUFACTURING_INPUT': [{'connect' : (1, 2)}, {'connect' : (3, 2)}],
                          'HAS_MANUFACTURING_OUTPUT': [{'connect' : (2, 5)}]},

    }
    list = ['Pt', 'Ethanol']
    educt = [materials_search.find_string(query) for query in [el['name'] for el in workflow_dict['nodes']['EMMOMatter']['educt']]]
    materials = [mat.uid for mat in ontology.is_a.all()]
    pass

# Non-Django related imports
from dotenv import load_dotenv
from neomodel import db

# Django-related imports only when the script is run directly
if __name__ == "__main__":
    print("HIIIII")
    import django
    from django.template.loader import render_to_string
    from django.conf import settings

    from dbcommunication.ai.searchEmbeddings import EmbeddingSearch
    from matching.matcher import Matcher
    from matgraph.models.ontology import EMMOMatter, EMMOProcess

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()

    # Setup Django
    django.setup()
    main()
