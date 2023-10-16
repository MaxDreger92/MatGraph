import csv
from io import StringIO
from importing.importer import Importer
class TableImporter(Importer):
    """
    A TableImporter class to handle table data.
    This subclass is specialized for handling table (e.g., CSV) data.
    """

    type = 'table'

    def __init__(self, data, column_types=None, *args, **kwargs):
        """
        Initialize the TableImporter instance.

        Args:
            column_types (dict): A dictionary specifying the type of each column e.g., {'name': str, 'age': int}
        """
        super().__init__(data, *args, **kwargs)
        self.column_types = column_types or {}
        self.table_data = None

    def build_query(self):
        """
        Method to build query for table data.
        """
        # Parse CSV data and convert it to appropriate format for your database
        # You might want to build a Cypher (for Neo4j) query to add nodes or relationships based on this data
        self.table_data = self._parse_csv()

        query = ""  # Your Cypher query here
        params = {}  # Any parameters for your query

        return query, params

    def _parse_csv(self):
        """
        Parses CSV data and returns a list of dictionaries.
        """
        data_io = StringIO(self.data)
        reader = csv.DictReader(data_io)

        data_list = []
        for row in reader:
            # Convert each value based on column type if specified
            for col, col_type in self.column_types.items():
                if col in row:
                    try:
                        row[col] = col_type(row[col])
                    except ValueError:
                        # Handle inappropriate type conversion, you can log or raise an exception
                        pass
            data_list.append(row)

        return data_list

    def build_results_for_report(self):
        """
        Override to present table data in the report.
        """
        # You might want to display only the first few rows in the report as an example
        sample_data = self.table_data[:10]  # First 10 rows as an example

        columns = list(sample_data[0].keys()) if sample_data else []

        return sample_data, columns
