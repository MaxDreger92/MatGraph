import operator

import networkx as nx

from importing.RelationshipExtraction.input_generator import prepare_lists


class relationshipValidator:
    def __init__(self, input, result):
        self.input = input
        self.result = result
        self.triples = []
        self.label_one, self.label_two = None, None
        self._label_one_nodes, self._label_two_nodes = None, None
        self._validation_results = None

        for rel in self.result.relationships:
            self.triples.append([str(rel.source), rel.type, str(rel.target)])
            print(str(rel.source), rel.type, str(rel.target))


    def validate(self):
        """Needs to be implemented in the subclass."""
        pass

    def cardinality(self, cardinality, rel_type, node_type='target', check_type='>'):
        """
        Check the cardinality of source or target nodes in relationship triples, allowing checks for cardinality
        using specified comparison operators ('!=', '<', '>').

        Parameters:
        - cardinality: The cardinality threshold for the node.
        - rel_type: The type of relationship to consider.
        - node_type: Specifies which node's cardinality to check ('source' or 'target').
        - check_type: Specifies the comparison operator as a string ('!=', '<', '>').
        """

        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            if rel == rel_type:
                g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Map the string representation of the operator to the actual operator function
        operators = {'>': operator.gt, '<': operator.lt, '!=': operator.ne}
        compare = operators.get(check_type)

        if not compare:
            raise ValueError("Invalid comparison operator. Use '!=', '<', or '>'.")

        node_degrees = g.in_degree() if node_type == 'target' else g.out_degree()

        for node, degree in node_degrees:
            if compare(degree, cardinality):
                related_nodes = [
                    src if node_type == 'target' else dst
                    for src, dst, data in g.edges(data=True)
                    if data['relation'] == rel_type and (
                                (dst == node and node_type == 'target') or (src == node and node_type == 'source'))
                ]
                if related_nodes:
                    wrong_nodes[node] = related_nodes

        return {'cardinality': cardinality, 'rel_type': rel_type, 'node_type': node_type, 'check_type': check_type,
                'nodes': wrong_nodes} if wrong_nodes else True

    def no_isolated_nodes(self):
        """Get a list of nodes that are isolated or return True."""
        isolated_nodes = [str(node) for node in self.node_ids if node not in self.flatten_relations]
        return isolated_nodes if len(isolated_nodes) != 0 else True

    def no_isolated_nodes_node_list(self, list_of_nodes, triple_position: 0 | 2):
        # Extract the last part of each triple
        elements = [triple[triple_position] for triple in self.triples]
        isolated_property_nodes = [node for node in self.node_label_ids(list_of_nodes) if node not in elements]
        # Check if all elements are present in the last_elements list
        return isolated_property_nodes if len(isolated_property_nodes) != 0 else True

    def full_connectivity(self):
        """Check if the relationship graph is connected."""
        g = nx.Graph()
        for triple in self.triples:
            src, _, dst = triple
            g.add_edge(src, dst)
        return nx.is_connected(g)

    def triples_correct(self, rel_type):
        """
        Validate the triples to check if they use correct nodes for label_one and label_two.
        """
        wrong_first_nodes = [triple[0] for triple in self.triples if
                             triple[0] not in self.node_label_ids(self.label_one_nodes) and triple[1] == rel_type]
        wrong_second_nodes = [triple[2] for triple in self.triples if
                              triple[2] not in self.node_label_ids(self.label_two_nodes) and triple[1] == rel_type]
        return {'wrong_first_nodes': wrong_first_nodes, 'rel_type': rel_type,
                'wrong_second_nodes': wrong_second_nodes} if len(wrong_first_nodes) != 0 or len(
            wrong_second_nodes) != 0 else True

    def triples_correct_reversed(self, rel_type):
        """
        Validate the triples to check if they use correct nodes for label_one and label_two.
        """
        wrong_first_nodes = [triple[0] for triple in self.triples if
                             triple[0] not in self.node_label_ids(self.label_two_nodes) and triple[1] == rel_type]
        wrong_second_nodes = [triple[2] for triple in self.triples if
                              triple[2] not in self.node_label_ids(self.label_one_nodes) and triple[1] == rel_type]
        return {'wrong_first_nodes': wrong_first_nodes, 'rel_type': rel_type,
                'wrong_second_nodes': wrong_second_nodes} if len(wrong_first_nodes) != 0 or len(
            wrong_second_nodes) != 0 else True

    def no_cycles(self, rel1, rel2):
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
                if G[common][node]['relation'] == rel1 and G[node][common]['relation'] == rel2:
                    problematic_nodes.add(common)

        return {'rel1': rel1, 'rel2': rel2, 'nodes': list(problematic_nodes)} if len(problematic_nodes) != 0 else True

    @property
    def flatten_relations(self):
        """Flatten the relationship triples."""
        return [item for sublist in self.triples for item in sublist if isinstance(item, (int, str))]

    @property
    def node_ids(self):
        """Get all node IDs from label_one_nodes and label_two_nodes."""
        return [item['id'] for item in [*self.label_one_nodes, *self.label_two_nodes]]

    def node_label_ids(self, node_list):
        """Get node IDs from label_one_nodes."""
        return [item['id'] for item in node_list]

    @property
    def node_label_two_ids(self):
        """Get node IDs from label_two_nodes."""
        return [item['id'] for item in self.label_two_nodes]

    @property
    def validation_results(self):
        return self._validation_results

    @property
    def label_one_nodes(self):
        return self._label_one_nodes

    @property
    def label_two_nodes(self):
        return self._label_two_nodes

    def run(self):
        if not self.validation_results:
            self.validate()
        return self._validation_results


class hasPropertyValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_property"
        self.label_one, self.label_two = ["matter"], ["property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.no_isolated_nodes_node_list.__name__: self.no_isolated_nodes_node_list(self.label_two_nodes, 2),
            self.cardinality.__name__: self.cardinality(1, self.rel_type, 'target', '!='),
            self.triples_correct.__name__: self.triples_correct(self.rel_type)
        }


class hasManufacturingValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "is_manufacturing_input"
        self.rel_type2 = "has_manufacturing_output"
        self.label_one, self.label_two = ["matter"], ["manufacturing"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.cardinality.__name__: self.cardinality(1, self.rel_type2, 'target', '>'),
            self.no_cycles.__name__: self.no_cycles(self.rel_type, self.rel_type2),
            self.triples_correct.__name__: self.triples_correct(self.rel_type),
            self.triples_correct_reversed.__name__: self.triples_correct_reversed(self.rel_type2),
            self.no_isolated_nodes.__name__: self.no_isolated_nodes()
        }


class hasParameterValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_parameter"
        self.label_one, self.label_two = ["manufacturing", "measurement"], ["parameter"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.no_isolated_nodes_node_list.__name__: self.no_isolated_nodes_node_list(self.label_two_nodes, 2),
            self.cardinality.__name__: self.cardinality(1, self.rel_type, 'target', '!='),
            self.triples_correct.__name__: self.triples_correct(self.rel_type),
        }


class hasMeasurementValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_measurement"
        self.label_one, self.label_two = ["measurement"], ["property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.no_isolated_nodes.__name__: self.no_isolated_nodes_node_list(self.label_one_nodes, 0)
        }


class hasPartMatterValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_part"
        self.label_one, self.label_two = ["matter"], ["matter"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.triples_correct.__name__: self.triples_correct(self.rel_type)
        }

class hasPartManufacturingValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_part"
        self.label_one, self.label_two = ["manufacturing"], ["manufacturing"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.triples_correct.__name__: self.triples_correct(self.rel_type)
        }

class hasPartMeasurementValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_part"
        self.label_one, self.label_two = ["measurement"], ["measurement"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input, self.label_one, self.label_two)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.triples_correct.__name__: self.triples_correct(self.rel_type)
        }