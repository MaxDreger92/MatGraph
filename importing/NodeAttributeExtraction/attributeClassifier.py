import re

from quantulum3 import parser

from graphutils.general import TableDataTransformer
from importing.models import (ManufacturingAttribute,
                              MeasurementAttribute, MatterAttribute,
                              MetadataAttribute, PropertyAttribute,
                              ParameterAttribute, ImporterCache, LabelClassificationReport)


class AttributeClassifier(TableDataTransformer):
    """
    A classifier for attributing labels and sub-attributes to data headings.

    Attributes:
        data (list): The input data to classify.
        context (str): The context for classification.
        cache (bool): Flag to use caching mechanism.
    """

    def __init__(self, predicted_labels, ReportClass=LabelClassificationReport, **kwargs):
        kwargs['data'] = predicted_labels
        self.attribute_type = 'column_attribute'
        super().__init__(ReportClass=LabelClassificationReport, **kwargs)

    def set_labels(self, labels):
        print("Setting labels")
        print(labels)

    @property
    def iterable(self):
        """
        Returns the headers for iteration.

        Returns:
            pandas.Series: The headers of the table data.
        """
        return self.data

    def iterate(self):
        """
        Iterates over each header to transform the data.
        """
        for index, element in enumerate(self.iterable):
            self._process(element=element, index=index)

    def _process(self, **kwargs):
        """
        Transform the data.
        """
        if self._pre_check(index=kwargs['index'], element=kwargs['element']):
            return
        elif self._check_cache(index=kwargs['index'], element=kwargs['element']):
            return
        else:
            self._transform(index=kwargs['index'], element=kwargs['element'])

    def _pre_check(self, index, element):
        """
        Perform a check before processing the data.
        """

        column = element['column_values']
        if len(column) == 0:
            return True
        return False


    def _update_with_chat(self, result, input_string, **kwargs):
        """
        Update the classification result with a chat result.
        """
        print("Chat result", result)
        self._results.append({
            **kwargs['element'],
            "cached": False,
            "input_string": input_string.replace("\n", "").replace(" ", ""),
            "1_attribute": result,
            **{f"{i}_attribute": None for i in range(2, 5)},
            **{f"{i}_subattributes": None for i in range(1, 5)},
            **{f"{i}_predicted_attribute_similarities": None for i in range(1, 5)}
        })
        ImporterCache.update(kwargs['element']['header'], column_attribute=result, attribute_type=self.attribute_type)

    def build_results(self):
        self._results = sorted(self._results, key=lambda x: x['index'])

    def _update_from_cache(self, element):
        """
        Attempt to update the element from cache.

        Args:
            element (dict): The element to update.

        Returns:
            bool: True if the element was updated from cache, False otherwise.
        """
        if cached := ImporterCache.fetch(element['header'], element['column_values']):
            attribute = cached[3]
            if attribute is not None:
                self._results.append({
                    **element,
                    "cached": True,
                    "input_string": None,
                    "1_attribute": cached  # Assuming similarity is 1 for all
                })
                return True
        return False

    def analyze_results(self, results, **kwargs):
        """
        Analyze the results to find the most occurring name and calculate its ratio to the total number of names.

        Parameters:
            results (list): A list of lists, where each inner list's first element is a node with an attribute 'name'.

        Returns:
            tuple: A tuple containing the most occurring name and its ratio to the total number of names.
        """
        results = results[0:5]
        def is_number(s):
            # This pattern matches optional whitespace, followed by an optional sign,
            # followed by a sequence of digits, possibly with a decimal part or exponent part,
            # and may include arrays like [1, 2.3, -4, 5.6]
            pattern = r"^\s*(\[\s*)?(-?\d+(\.\d+)?(e-?\d+)?\s*(,\s*-?\d+(\.\d+)?(e-?\d+)?\s*)*\]?\s*)+$"
            return bool(re.fullmatch(pattern, s))
        # print(kwargs['element']['header'], results)
        if results[0][1] > 0.95:
            final_result = results[0][0]
            # print(results[0][3], final_result.name)
            return final_result.name
        from collections import Counter
        # Extract names from the results
        names = [result[0].name for result in results if result]
        names.append(results[0][0].name)
        # print(names)
        inputs = [result[2] for result in results if result]
        print(results[0][3])

        table_header = kwargs['element']['header']
        cell_value = kwargs['element']['column_values'][0]
        cell_number = is_number(cell_value)
        cell_unit = (len(parser.parse(cell_value)) > 0)
        header_number = is_number(table_header)
        header_unit = (len(parser.parse(table_header)) > 0)
        print(kwargs['element']['header'], cell_number, cell_unit, header_number, header_unit, names)
        print(kwargs['element']['header'], inputs)
        if kwargs['element']['1_label'].lower() == 'property' or kwargs['element']['1_label'].lower() == 'parameter':
            names.append('value')
            names.append('value')
            if cell_number and not cell_unit:
                print("Cell number and no unit")
                for _ in range(3):
                    if 'name' in names:
                        names.remove('name')
                    if 'unit' in names:
                        names.remove('unit')
            elif cell_unit and not cell_number:
                # print("Cell unit and no number")
                for _ in range(3):
                    if 'name' in names:
                        names.remove('name')
                names.extend(['unit', 'unit'])
            elif cell_number:
                # print("Cell number")
                if 'name' in names:
                    names.remove('name')
                if 'unit' in names:
                    names.remove('unit')
                if 'unit' in names:
                    names.remove('unit')
                if 'name' in names:
                    names.remove('name')
        else:
            if cell_number:
                 names.append('identifier')
        # print(names)
        name_counts = Counter(names)

            # Count each name's occurrence
        # Find the most common name and the number of times it appears
        most_common_name, most_common_count = name_counts.most_common(1)[0]
        print(kwargs['element']['header'], most_common_name, most_common_count)
        return most_common_name

    def _update(self, result, input_string, **kwargs):
        """
        Update the element's data based on the query result.

        Args:
            input_string (str): The input string used for the query.
            result (list): The query result to update the element with.
            **kwargs: Additional keyword arguments.
        """
        element = kwargs['element']
        self._results.append({
            **element,
            "cached": False,
            "input_string": input_string.replace("\n", ""),
            "1_attribute": result
        })
        ImporterCache.update(element['header'], column_attribute=result, attribute_type=self.attribute_type)

    def _update_with_cache(self, cached, **kwargs):
        """
        Update the element's data based on the query result.

        Args:
            input_string (str): The input string used for the query.
            result (list): The query result to update the element with.
            **kwargs: Additional keyword arguments.
        """
        element = kwargs['element']
        self._results.append({
            **element,
            "cached": True,
            "input_string": None,
            "1_attribute": cached[3],
        })

    def _llm_request(self, input_string, **kwargs):
        """
        Send a request to the node label model.
        """
        result = self._get_node_class(kwargs['element']['1_label']).nodes.get_by_string(string=input_string, limit=5,
                                                                                        include_similarity=True,
                                                                                        include_input_string=True)
        return result

    def _create_input_string(self, index, element):
        """
        Create an input string for classification based on the element.

        Args:
            element (dict): The element to create an input string for.

        Returns:
            str: The created input string.
        """
        return f""" "{element['header']}": "{element['column_values']}" """

    @staticmethod
    def _get_node_class(label):
        """
        Get the node class corresponding to a label.

        Args:
            label (str): The label to get the node class for.

        Returns:
            Class: The corresponding node class.
        """
        node_classes = {
            "Manufacturing": ManufacturingAttribute,
            "Measurement": MeasurementAttribute,
            "Matter": MatterAttribute,
            "Metadata": MetadataAttribute,
            "Property": PropertyAttribute,
            "Parameter": ParameterAttribute  # Default case
        }
        return node_classes.get(label, ParameterAttribute)

    @property
    def results(self):
        """
        Get the predicted attributes.

        Returns:
            list: The predicted attributes.
        """

        return self._results
