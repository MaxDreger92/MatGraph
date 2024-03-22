import networkx as nx

from importing.RelationshipExtraction.completeRelExtractor import prepare_lists


class relationshipValidator:
    def __init__(self, result, label_one, label_two, label_one_nodes, label_two_nodes):
        self.result = result
        self.triples = []
        self.label_one, self.label_two = label_one, label_two
        self.label_one_nodes, self.label_two_nodes = label_one_nodes, label_two_nodes

        for value in self.result.values():
            for rel in value.relationships:
                self.triples.append([str(rel.source), rel.type, str(rel.target)])

    def validate(self):
        """Needs to be implemented in the subclass."""
        pass

    def cardinality_one_target(self, cardinality, rel_type):
        """
        Check cardinality of target nodes in the relationship triples.
        """
        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            if rel == rel_type:
                g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Check nodes with 'has_output' relationship for multiple outputs
        for src, dst, data in g.edges(data=True):
            if data['relation'] == rel and g.in_degree(dst) > cardinality:
                if dst in wrong_nodes.keys():
                    wrong_nodes[dst].append(src)
                else:
                    wrong_nodes[dst] = [src]
        return wrong_nodes if len(wrong_nodes.keys()) != 0 else True

    def cardinality_one_source(self, cardinality):
        """
        Check cardinality of source nodes in the relationship triples.
        """
        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Check nodes with 'has_output' relationship for multiple outputs
        for src, dst, data in g.edges(data=True):
            if data['relation'] == rel and g.in_degree(src) > cardinality:
                if dst in wrong_nodes.keys():
                    wrong_nodes[src].append(dst)
                else:
                    wrong_nodes[src] = [dst]
        return wrong_nodes if len(wrong_nodes.keys()) != 0 else True

    def no_isolated_nodes(self):
        """Get a list of nodes that are isolated or return True."""
        isolated_nodes = [str(node) for node in self.node_ids if node not in self.flatten_relations]
        return  isolated_nodes if len(isolated_nodes) != 0 else True

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
        wrong_second_nodes = [triple[2] for triple in self.triples if triple[2] not in self.node_label_two_ids and triple[1] == rel_type]
        wrong_first_nodes = [triple[0] for triple in self.triples if triple[0] not in self.node_label_one_ids and triple[1] == rel_type]
        return [wrong_first_nodes, wrong_second_nodes] if len(wrong_first_nodes) != 0 or len(wrong_second_nodes) != 0 else True

    def triples_correct_reversed(self, rel_type):
        """
        Validate the triples to check if they use correct nodes for label_one and label_two.
        """
        wrong_first_nodes = [triple[0] for triple in self.triples if triple[0] not in self.node_label_two_ids and triple[1] == rel_type]
        wrong_second_nodes = [triple[2] for triple in self.triples if triple[2] not in self.node_label_one_ids and triple[1] == rel_type]
        return [wrong_first_nodes, wrong_second_nodes] if len(wrong_first_nodes) != 0 or len(wrong_second_nodes) != 0 else True


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

        return list(problematic_nodes) if len(problematic_nodes) != 0 else True

    def no_isolated_nodes_node_list(self, list_of_nodes, triple_position: 0|2):
        # Extract the last part of each triple
        elements = [triple[triple_position] for triple in self.triples]
        isolated_property_nodes = [node for node in self.node_label_one_ids if node not in elements]
        # Check if all elements are present in the last_elements list
        return isolated_property_nodes if len(isolated_property_nodes) != 0 else True



    @property
    def flatten_relations(self):
        """Flatten the relationship triples."""
        return [item for sublist in self.triples for item in sublist if isinstance(item, (int, str))]

    @property
    def node_ids(self):
        """Get all node IDs from label_one_nodes and label_two_nodes."""
        return [item['id'] for item in [*self.label_one_nodes, *self.label_two_nodes]]

    @property
    def node_label_one_ids(self):
        """Get node IDs from label_one_nodes."""
        return [item['id'] for item in self.label_one_nodes]

    @property
    def node_label_two_ids(self):
        """Get node IDs from label_two_nodes."""
        return [item['id'] for item in self.label_two_nodes]

    @property
    def results(self):
        if not self.validation_results:
            self.validate()
        return self._validation_to_correction

class hasPropertyValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_property"

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_to_correction = {
            self.cardinality_one_target.__name__: self.cardinality_one_target(1, self.rel_type),
            self.triples_correct.__name__: self.triples_correct(self.rel_type),
            self.correct_no_isolated_nodes_node_list.__name__: self.no_isolated_nodes_node_list(self.label_two_nodes, 2),
        }
        return self.validation_to_correction

class hasManufacturingValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_type = "has_manufacturing_input"
        self.rel_type2 = "is_manufacturing_output"

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_to_correction = {
            self.cardinality_one_target.__name__: self.cardinality_one_target(1, self.rel_type2),
            self.no_cycles.__name__: self.no_cycles(self.rel_type, self.rel_type2),
            self.triples_correct.__name__: self.triples_correct(self.rel_type),
            self.triples_correct_reversed.__name__: self.triples_correct_reversed(self.rel_type2),
            self.no_isolated_nodes.__name__: self.no_isolated_nodes
        }

class hasParameterValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_to_correction = {
            self.cardinality_one_target.__name__: self.cardinality_one_target(1),
            self.no_isolated_nodes.__name__: self.no_isolated_nodes(self.label_two_nodes, 2)
        }

class hasMeasurementValidator(relationshipValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_to_correction = {
            self.no_isolated_nodes.__name__: self.no_isolated_nodes(self.label_two_nodes, 2)
        }





