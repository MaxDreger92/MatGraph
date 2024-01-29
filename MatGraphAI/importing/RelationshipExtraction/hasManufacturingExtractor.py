import networkx as nx

from importing.RelationshipExtraction.relationshipExtractor import RelationshipExtractor
from importing.utils.openai import chat_with_gpt4


class hasManufacturingExtractor(RelationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        super().__init__(*args, **kwargs)



    @property
    def triples_correct(self):
        """
        Validate the triples to check if they use correct nodes for label_one and label_two.
        """
        wrong_second_nodes = [*[triple[2] for triple in self.triples if triple[2] not in self.node_label_two_ids and triple[1] == "is_input"],
                              *[triple[0] for triple in self.triples if triple[0] not in self.node_label_two_ids and triple[1] == "has_output"]]
        wrong_first_nodes = [*[triple[2] for triple in self.triples if triple[2] not in self.node_label_one_ids and triple[1] == "has_output"],
                             *[triple[0] for triple in self.triples if triple[0] not in self.node_label_one_ids and triple[1] == "is_input"]]
        return wrong_first_nodes, wrong_second_nodes
    def revise_has_output(self):
        if self.check_one_to_one_destination("has_output"):
            prompt = f"""- These matter have multiple "has_output" edges two different manufacturing nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {self.check_one_to_one_destination("has_output")} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.update_triples(response)
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})
    @property
    def manufacturing_cycles(self):
        G = nx.DiGraph()  # Create a directed graph

        # Add edges based on the triples
        for src, rel, dst in self.triples:
            G.add_edge(src, dst, relation=rel)

        problematic_nodes = set()

        # Iterate through nodes and check for the specific condition
        for node in G:
            predecessors = list(G.predecessors(node))
            successors = list(G.successors(node))
            common_nodes = set(predecessors).intersection(successors)

            for common in common_nodes:
                if G[common][node]['relation'] == 'is_input' and G[node][common]['relation'] == 'has_output':
                    problematic_nodes.add(common)

        return list(problematic_nodes) if len(problematic_nodes) != 0 else False

    def revise_manufacturing_cycles(self):
        if self.manufacturing_cycles:
            prompt = f"""- The following matter nodes share 'is_input' and 'has_output' edges with one and the same 
                    manufacturing nodes: {self.manufacturing_cycles}. 
                    Suggest another reasonable solution in which matter nodes share do not share 'is_input' and 'has_output' 
                    edges with one and the same manufacturing node. 
                    \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})
            self.revise_manufacturing_cycles()

    def refine_results(self):
        """ Validate the extracted relationships. """
        print("Refining results...")
        self.revise_triples()
        self.revise_manufacturing_cycles()
        self.revise_has_output()
        self.revise_isolated_nodes()
        self.revise_connectedness()


    def generate_result(self):
        """ Generate the final result. """
        return [
            {
                "rel_type": triple[1].upper(),
                "connection": [triple[0], triple[2]]
            }
            for triple in self.triples
        ]