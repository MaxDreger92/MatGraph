import json

class GraphData:
    def __init__(self):
        self.nodes = {}
        self.relationships = {}

    def add_node(self, node_id, node_class, **properties):
        if node_class not in self.nodes:
            self.nodes[node_class] = []

        node = {"id": node_id, **properties}
        self.nodes[node_class].append(node)

    def add_relationship(self, source_id, target_id, relationship_type):
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []

        relationship = {"source": source_id, "target": target_id}
        self.relationships[relationship_type].append(relationship)

    def to_json(self):
        return json.dumps({"nodes": self.nodes, "relationships": self.relationships}, indent=2)



# Example usage
graph_data = GraphData()
graph_data.add_node("1", "Person", name="Alice", age=30)
graph_data.add_node("2", "Person", name="Bob", age=25)
graph_data.add_node("3", "City", name="New York")
graph_data.add_relationship("1", "3", "LIVES_IN")

print(graph_data.to_json())