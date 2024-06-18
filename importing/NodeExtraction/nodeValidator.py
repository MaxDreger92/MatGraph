class NodeValidator:
    def __init__(self, input, nodes):
        self.raw_data = input
        self.nodes = nodes
        self._validation_results = None

    @property
    def validation_results(self):
        return self._validation_results

    def validate(self):
        """Needs to be implemented in the subclass."""
        pass

    def run(self):
        if not self.validation_results:
            self.validate()
        return self._validation_results

    def check_duplicates(self):
        reference_count = {}

        # Iterate over each node and each attribute in the node's attributes
        for node_index, node in enumerate(self.nodes.nodes):
            # Dynamically access all attributes of the node's attributes object
            for attr_name in dir(node.attributes):
                if not attr_name.startswith('__'):
                    attr = getattr(node.attributes, attr_name)
                    # Check if attribute is a list of items with AttributeReferences
                    if isinstance(attr, list):
                        for item in attr:
                            if hasattr(item, 'AttributeReference') and type(item.AttributeReference) == int:
                                key = item.AttributeReference
                                if key in reference_count.keys():
                                    reference_count[key].append(attr_name)
                                else:
                                    reference_count[key] = [attr_name]
                    # Check if it's a single item with an AttributeReference
                    elif hasattr(attr, 'AttributeReference')and type(attr.AttributeReference) == int:
                        key = attr.AttributeReference
                        if key in reference_count.keys():
                            reference_count[key].append(attr_name)
                        else:
                            reference_count[key] = [attr_name]

        # Filter out entries with only one attribute name (no duplicates)
        duplicates = list({str(key) for key, values in reference_count.items() if len(values) > 1})

        return duplicates






    def check_indices(self):
        """Check for indices in the list."""
        indices = {index: {"type": type , "value": value} for index, value, type in zip(self.raw_data['indices'], self.raw_data['row'], self.raw_data['attributes'])}
        errors = []  # List to hold any discrepancies found

        # Iterate over each node
        for node_index, node in enumerate(self.nodes.nodes):
            # Dynamically access all attributes of the node's attributes object
            for attr_name in dir(node.attributes):
                if not attr_name.startswith('_'):
                    attr = getattr(node.attributes, attr_name)

                    # Handle both single items and lists uniformly
                    if not isinstance(attr, list):
                        attr = [attr]  # Convert single item to list for uniform processing

                    for item in attr:
                        # Check if the item has an AttributeReference and is relevant
                        if hasattr(item, 'AttributeReference') and type(item.AttributeReference) == int:
                            ref = str(item.AttributeReference)  # Ensure it's a string for dictionary lookup
                            # Check if this reference is in indices and matches type and value
                            if ref in indices:
                                expected_type = indices[ref]['type']
                                expected_value = indices[ref]['value']
                                try:
                                    expected_value_float = float(expected_value)
                                    item_value_is_float = isinstance(item.AttributeValue, float) and float(item.AttributeValue) == expected_value_float
                                except ValueError:
                                    item_value_is_float = False

                                if ((str(attr_name) != str(expected_type) and str(attr_name) not in ['batch number', 'batch_number']) or
                                        (str(item.AttributeValue) != str(expected_value) and
                                         not (expected_value == '' or item_value_is_float))):
                                    errors.append({"index": ref,
                                                   "type": [attr_name, expected_type],
                                                   "value": [str(item.AttributeValue), expected_value]})
        print(errors)

        return errors

    def check_invalid_references(self):
        # Retrieve the indices from the input and convert to a set for efficient lookup
        valid_indices = set(self.raw_data['indices'])

        # Set to store all unique AttributeReferences found in the nodes
        found_references = set()

        # Iterate through each node in the node list
        for node in self.nodes.nodes:
            # Dynamically access all attributes of the node's attributes object
            for attr_name in dir(node.attributes):
                if not attr_name.startswith('_'):
                    attr = getattr(node.attributes, attr_name)
                    # Handle both single items and lists uniformly
                    if not isinstance(attr, list):
                        attr = [attr]  # Convert single item to list for uniform processing

                    for item in attr:
                        if hasattr(item, 'AttributeReference') and type(item.AttributeReference) == int:
                            found_references.add(str(item.AttributeReference))  # Store as string for consistency

        # Find references that are not in the set of valid indices
        invalid_references = found_references - valid_indices

        return list(invalid_references)



    def check_for_unused_indices(self):
        # Retrieve the indices from the input
        input_indices = set(self.raw_data['indices'])

        # Set to store all unique AttributeReferences found in the nodes
        used_references = set()

        # Iterate through each node in the node list
        for node in self.nodes.nodes:
            # Dynamically access all attributes of the node's attributes object
            for attr_name in dir(node.attributes):
                if not attr_name.startswith('_'):
                    attr = getattr(node.attributes, attr_name)
                    # Handle both single items and lists uniformly
                    if not isinstance(attr, list):
                        attr = [attr]  # Convert single item to list for uniform processing

                    for item in attr:
                        # Check if the item has an AttributeReference and is relevant
                        if hasattr(item, 'AttributeReference'):
                            used_references.add(str(item.AttributeReference))  # Store as string for consistency

        # Check if every index in input_indices is used at least once
        unused_indices = input_indices - used_references

        return list(unused_indices)







class MatterValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class PropertyValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class ParameterValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class ManufacturingValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class MeasurementValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class SimulationValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results

class MetadataValidator(NodeValidator):

    def validate(self):
        """Run all validation functions and gather results."""
        self._validation_results = {
            self.check_for_unused_indices.__name__: self.check_for_unused_indices(),
            self.check_invalid_references.__name__: self.check_invalid_references(),
            self.check_indices.__name__: self.check_indices(),
            self.check_duplicates.__name__: self.check_duplicates(),
        }
        return self._validation_results